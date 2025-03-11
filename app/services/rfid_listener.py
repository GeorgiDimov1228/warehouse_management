import threading
import logging
import json
import time
import datetime
import websocket
import requests
from flask import current_app
from app.services.rfid_service import process_rfid_scan

# Store active listeners by reader ID
active_listeners = {}

class RFIDReaderListener(threading.Thread):
    """
    Real-time RFID reader listener using WebSockets to connect to RFID reader hardware.
    Runs as a daemon thread in the background.
    """
    
    def __init__(self, reader_id, reader_url, api_key=None):
        """Initialize the RFID reader listener thread"""
        super().__init__(daemon=True)
        self.reader_id = reader_id
        self.reader_url = reader_url
        self.api_key = api_key
        self.ws = None
        self.running = False
        self.reconnect_delay = 1.0  # Start with 1 second delay, will increase with backoff
        self.max_reconnect_delay = 60.0  # Maximum reconnect delay (1 minute)
        self.reconnect_attempts = 0
        self.last_activity = datetime.datetime.now()
        self.connected = False
        self.error_count = 0
        
        self.name = f"RFID-Reader-{reader_id}"  # Name the thread for easier debugging
        logging.info(f"Initialized RFID Reader Listener for reader {reader_id} at {reader_url}")
    
    def connect(self):
        """Establish WebSocket connection to the RFID reader"""
        try:
            # Close existing connection if any
            if self.ws:
                self.ws.close()
            
            # Prepare headers for authentication if needed
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            # Create a new WebSocket connection
            self.ws = websocket.WebSocketApp(
                self.reader_url,
                header=headers,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            return True
        except Exception as e:
            logging.error(f"Failed to initialize WebSocket for reader {self.reader_id}: {str(e)}")
            self.error_count += 1
            return False
    
    def on_open(self, ws):
        """Called when WebSocket connection is established"""
        logging.info(f"Connected to RFID reader {self.reader_id}")
        self.reconnect_delay = 1.0  # Reset reconnect delay on successful connection
        self.reconnect_attempts = 0
        self.connected = True
        self.last_activity = datetime.datetime.now()
        
        # Send initialization message if required by the reader
        try:
            init_message = {
                "action": "initialize",
                "reader_id": self.reader_id,
                "client": "flask-warehouse-app"
            }
            ws.send(json.dumps(init_message))
        except Exception as e:
            logging.error(f"Failed to send initialization message: {str(e)}")
    
    def on_message(self, ws, message):
        """Process messages received from the RFID reader"""
        try:
            data = json.loads(message)
            self.last_activity = datetime.datetime.now()
            
            # Check if this is a scan event message
            if data.get("event_type") == "scan":
                rfid_tags = data.get("rfid_tags", [])
                if rfid_tags:
                    logging.info(f"Received scan from reader {self.reader_id}: {len(rfid_tags)} tags")
                    # Process the scan in a separate thread to avoid blocking the WebSocket
                    processing_thread = threading.Thread(
                        target=self._process_scan,
                        args=(rfid_tags,),
                        daemon=True
                    )
                    processing_thread.start()
            
            # Handle other event types if needed
            elif data.get("event_type") == "status":
                logging.info(f"Reader {self.reader_id} status: {data.get('status')}")
            
            elif data.get("event_type") == "error":
                logging.error(f"Reader {self.reader_id} error: {data.get('error_message')}")
                self.error_count += 1
        
        except json.JSONDecodeError:
            logging.error(f"Received invalid JSON from reader {self.reader_id}: {message}")
            self.error_count += 1
        except Exception as e:
            logging.error(f"Error processing message from reader {self.reader_id}: {str(e)}")
            self.error_count += 1
    
    def _process_scan(self, rfid_tags):
        """Process a batch of scanned RFID tags (runs in a separate thread)"""
        try:
            # Import app from a different thread requires a context
            from flask import current_app
            with current_app.app_context():
                process_rfid_scan(self.reader_id, rfid_tags)
        except Exception as e:
            logging.error(f"Error processing scan batch: {str(e)}")
            self.error_count += 1
    
    def on_error(self, ws, error):
        """Handle WebSocket errors"""
        logging.error(f"WebSocket error for reader {self.reader_id}: {str(error)}")
        self.error_count += 1
        self.connected = False
    
    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket connection close"""
        logging.warning(f"Connection to RFID reader {self.reader_id} closed: {close_msg} (code: {close_status_code})")
        self.connected = False
        
        # Attempt reconnection if we're still supposed to be running
        if self.running:
            self.reconnect_attempts += 1
            logging.info(f"Attempting to reconnect to reader {self.reader_id} in {self.reconnect_delay} seconds (attempt {self.reconnect_attempts})")
            time.sleep(self.reconnect_delay)
            
            # Implement exponential backoff for reconnection attempts
            self.reconnect_delay = min(self.reconnect_delay * 1.5, self.max_reconnect_delay)
            
            # Attempt to reconnect
            self.connect()
            
            # Start the WebSocket connection in this thread
            if self.ws:
                self.ws.run_forever()
    
    def run(self):
        """Main thread execution method"""
        self.running = True
        
        # First connection attempt
        if self.connect():
            # Start the WebSocket connection loop
            self.ws.run_forever()
        
        # If we get here, the WebSocket loop has ended
        logging.info(f"RFID reader listener for {self.reader_id} has stopped")
    
    def stop(self):
        """Stop the listener thread"""
        self.running = False
        if self.ws:
            self.ws.close()
        logging.info(f"Stopped RFID reader listener for {self.reader_id}")

    def get_status(self):
        """Get current status information"""
        now = datetime.datetime.now()
        return {
            'reader_id': self.reader_id,
            'connected': self.connected,
            'connection_url': self.reader_url,
            'running': self.running,
            'reconnect_attempts': self.reconnect_attempts,
            'error_count': self.error_count,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'inactivity_seconds': (now - self.last_activity).total_seconds() if self.last_activity else None
        }


class RFIDPollingListener(threading.Thread):
    """
    Alternative implementation for RFID readers that don't support WebSockets.
    Uses HTTP polling at regular intervals.
    """
    
    def __init__(self, reader_id, reader_url, api_key=None, poll_interval=2.0):
        """Initialize the polling listener thread"""
        super().__init__(daemon=True)
        self.reader_id = reader_id
        self.reader_url = reader_url
        self.api_key = api_key
        self.poll_interval = poll_interval
        self.running = False
        self.last_scan_id = None
        self.last_activity = datetime.datetime.now()
        self.connected = False
        self.error_count = 0
        self.reconnect_attempts = 0
        
        self.name = f"RFID-Poller-{reader_id}"
        logging.info(f"Initialized RFID Polling Listener for reader {reader_id} at {reader_url}")
    
    def run(self):
        """Main thread execution method"""
        self.running = True
        
        while self.running:
            try:
                self._poll_reader()
                self.connected = True
                time.sleep(self.poll_interval)
            except Exception as e:
                self.connected = False
                self.error_count += 1
                logging.error(f"Error polling RFID reader {self.reader_id}: {str(e)}")
                # Don't bombard the server if there's an error
                backoff_time = min(self.poll_interval * 2, 10)
                time.sleep(backoff_time)
                self.reconnect_attempts += 1
    
    def _poll_reader(self):
        """Poll the RFID reader for new scan data"""
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Add last scan ID if we have one to only get new scans
        params = {}
        if self.last_scan_id:
            params["since_id"] = self.last_scan_id
        
        try:
            response = requests.get(
                self.reader_url,
                headers=headers,
                params=params,
                timeout=5
            )
            
            self.last_activity = datetime.datetime.now()
            
            if response.status_code == 200:
                data = response.json()
                
                # Get new scans
                scans = data.get("scans", [])
                if scans:
                    for scan in scans:
                        # Update last scan ID
                        scan_id = scan.get("scan_id")
                        if scan_id and (not self.last_scan_id or scan_id > self.last_scan_id):
                            self.last_scan_id = scan_id
                        
                        # Process tags
                        rfid_tags = scan.get("rfid_tags", [])
                        if rfid_tags:
                            logging.info(f"Polled {len(rfid_tags)} tags from reader {self.reader_id}")
                            # Process in separate thread
                            processing_thread = threading.Thread(
                                target=self._process_scan,
                                args=(rfid_tags,),
                                daemon=True
                            )
                            processing_thread.start()
            else:
                self.error_count += 1
                logging.error(f"Failed to poll reader {self.reader_id}: HTTP {response.status_code}")
        
        except requests.RequestException as e:
            self.error_count += 1
            logging.error(f"Request error polling reader {self.reader_id}: {str(e)}")
    
    def _process_scan(self, rfid_tags):
        """Process a batch of scanned RFID tags (runs in a separate thread)"""
        try:
            # Import app from a different thread requires a context
            from flask import current_app
            with current_app.app_context():
                process_rfid_scan(self.reader_id, rfid_tags)
        except Exception as e:
            self.error_count += 1
            logging.error(f"Error processing poll scan batch: {str(e)}")
    
    def stop(self):
        """Stop the polling thread"""
        self.running = False
        logging.info(f"Stopped RFID polling listener for {self.reader_id}")

    def get_status(self):
        """Get current status information"""
        now = datetime.datetime.now()
        return {
            'reader_id': self.reader_id,
            'connected': self.connected,
            'connection_url': self.reader_url,
            'running': self.running,
            'reconnect_attempts': self.reconnect_attempts,
            'error_count': self.error_count,
            'poll_interval': self.poll_interval,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'inactivity_seconds': (now - self.last_activity).total_seconds() if self.last_activity else None,
            'last_scan_id': self.last_scan_id
        }


def start_rfid_reader_listener():
    """
    Start background processes to listen for RFID reader events
    Automatically determines the appropriate listener type based on URL
    """
    readers_config = current_app.config.get('RFID_READERS', {})
    
    # If no readers are explicitly configured, use the default from the config
    if not readers_config:
        default_reader_url = current_app.config.get('RFID_READER_API_URL')
        default_reader_key = current_app.config.get('RFID_READER_API_KEY')
        
        if default_reader_url:
            readers_config = {
                'default': {
                    'url': default_reader_url,
                    'api_key': default_reader_key
                }
            }
    
    # Start listeners for all configured readers
    for reader_id, config in readers_config.items():
        url = config.get('url')
        api_key = config.get('api_key')
        
        if not url:
            logging.warning(f"Skipping reader {reader_id} - no URL configured")
            continue
        
        # Check if we already have an active listener for this reader
        if reader_id in active_listeners and active_listeners[reader_id].is_alive():
            logging.info(f"Listener for reader {reader_id} is already running")
            continue
        
        # Choose the appropriate listener type based on the URL
        if url.startswith(('ws://', 'wss://')):
            # WebSocket-based listener
            listener = RFIDReaderListener(reader_id, url, api_key)
        else:
            # HTTP polling-based listener
            polling_interval = config.get('polling_interval', 2.0)
            listener = RFIDPollingListener(reader_id, url, api_key, polling_interval)
        
        # Start the listener thread
        listener.start()
        
        # Store the active listener
        active_listeners[reader_id] = listener
        
        logging.info(f"Started RFID reader listener for {reader_id} at {url}")
    
    # Start monitoring thread if listeners were created and we're in production
    if active_listeners and current_app.config.get('FLASK_ENV') == 'production':
        monitor_thread = threading.Thread(
            target=monitor_listeners,
            daemon=True,
            name="RFID-Monitor"
        )
        monitor_thread.start()
        logging.info("Started RFID listeners monitoring thread")
    
    return active_listeners

def monitor_listeners():
    """Monitor all RFID listeners and restart any that have failed"""
    # Wait a bit to let initial connections establish
    time.sleep(10)
    
    while True:
        try:
            for reader_id, listener in list(active_listeners.items()):
                # Check if thread is alive
                if not listener.is_alive():
                    logging.warning(f"Reader {reader_id} listener thread died, restarting")
                    # Remove dead listener
                    active_listeners.pop(reader_id, None)
                    # Get config again
                    if reader_id in current_app.config.get('RFID_READERS', {}):
                        config = current_app.config['RFID_READERS'][reader_id]
                        # Restart with original config
                        start_rfid_reader_listener()
                        # Send alert
                        send_alert(f"RFID reader {reader_id} connection lost and restarted")
                
                # Check for excessive errors or long inactivity
                elif hasattr(listener, 'get_status'):
                    status = listener.get_status()
                    
                    # If too many errors, restart
                    if status.get('error_count', 0) > 50:
                        logging.warning(f"Reader {reader_id} has {status['error_count']} errors, restarting")
                        listener.stop()
                        active_listeners.pop(reader_id, None)
                        # Wait a moment for thread to fully stop
                        time.sleep(1)
                        # Restart
                        start_rfid_reader_listener()
                        # Send alert
                        send_alert(f"RFID reader {reader_id} restarted due to excessive errors")
                    
                    # If inactive for too long (30 minutes)
                    elif status.get('inactivity_seconds', 0) > 1800:
                        logging.warning(f"Reader {reader_id} inactive for {status['inactivity_seconds']} seconds, sending alert")
                        # Send alert but don't restart yet
                        send_alert(f"RFID reader {reader_id} inactive for {status['inactivity_seconds']} seconds")
            
            # Check every 30 seconds
            time.sleep(30)
        
        except Exception as e:
            logging.error(f"Error in RFID monitor thread: {str(e)}")
            time.sleep(60)  # Wait a bit longer if we hit an error

def send_alert(message):
    """Send alert about RFID reader issues - implement based on your alerting system"""
    # In a production system, this might send an email, SMS, or notification
    logging.critical(f"RFID ALERT: {message}")
    
    # Example: If you have a webhook for alerts
    try:
        alert_webhook = current_app.config.get('ALERT_WEBHOOK_URL')
        if alert_webhook:
            requests.post(
                alert_webhook,
                json={
                    'source': 'rfid_system',
                    'severity': 'critical',
                    'message': message,
                    'timestamp': datetime.datetime.now().isoformat()
                },
                timeout=5
            )
    except Exception as e:
        logging.error(f"Failed to send alert: {str(e)}")

def get_reader_status():
    """Get status info for all active RFID readers"""
    status = {}
    
    for reader_id, listener in active_listeners.items():
        # Get detailed status if available
        if hasattr(listener, 'get_status'):
            status[reader_id] = listener.get_status()
        else:
            # Basic status if get_status not implemented
            status[reader_id] = {
                'reader_id': reader_id,
                'running': listener.is_alive(),
                'connection_url': getattr(listener, 'reader_url', 'unknown')
            }
    
    return status

def stop_all_rfid_listeners():
    """Stop all active RFID reader listeners"""
    for reader_id, listener in active_listeners.items():
        try:
            listener.stop()
            logging.info(f"Stopped RFID reader listener for {reader_id}")
        except Exception as e:
            logging.error(f"Error stopping listener for {reader_id}: {str(e)}")
    
    # Clear the active listeners dict
    active_listeners.clear()
    logging.info("Stopped all RFID reader listeners")