# Gunicorn configuration file for production deployment
import os
import multiprocessing

# Server socket
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:5000")
backlog = 2048

# Worker processes
workers = int(os.getenv("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Process naming
proc_name = 'warehouse-app'
pythonpath = '.'

# Server mechanics
daemon = False
pidfile = '/tmp/warehouse-app.pid'
umask = 0o027
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = os.getenv("GUNICORN_ERROR_LOG", '/var/log/warehouse/gunicorn-error.log')
accesslog = os.getenv("GUNICORN_ACCESS_LOG", '/var/log/warehouse/gunicorn-access.log')
access_log_format = '%({X-Forwarded-For}i)s %(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(L)s'
loglevel = os.getenv("GUNICORN_LOG_LEVEL", 'warning')

# Process hooks
def on_starting(server):
    pass

def on_reload(server):
    pass

def on_exit(server):
    # Clean up RFID listeners when Gunicorn exits
    try:
        from app.services.rfid_listener import stop_all_rfid_listeners
        stop_all_rfid_listeners()
    except Exception as e:
        server.log.error(f"Error during RFID listener cleanup: {str(e)}")

# Server hooks
def pre_fork(server, worker):
    pass

def post_fork(server, worker):
    # Start RFID listeners in each worker
    try:
        from app import create_app
        from app.config import ProductionConfig
        from app.services.rfid_listener import start_rfid_reader_listener
        
        app = create_app(ProductionConfig)
        with app.app_context():
            start_rfid_reader_listener()
    except Exception as e:
        server.log.error(f"Error starting RFID listeners in worker: {str(e)}")

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def pre_request(worker, req):
    worker.log.debug("%s %s" % (req.method, req.path))

def post_request(worker, req, environ, resp):
    pass

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def worker_abort(worker):
    worker.log.info("worker received SIGABRT signal")

def worker_exit(server, worker):
    # Clean up RFID listeners on worker exit
    try:
        from app.services.rfid_listener import stop_all_rfid_listeners
        stop_all_rfid_listeners()
    except Exception as e:
        server.log.error(f"Error during RFID listener cleanup: {str(e)}")