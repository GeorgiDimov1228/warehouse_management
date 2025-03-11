#!/usr/bin/env python3
import os
import argparse
import logging
import atexit
import signal
import sys

def create_parser():
    """Create the command line argument parser"""
    parser = argparse.ArgumentParser(description='Warehouse Management System')
    parser.add_argument(
        '--env', 
        choices=['development', 'production', 'testing'],
        default=os.getenv('FLASK_ENV', 'development'),
        help='The environment to run in'
    )
    parser.add_argument(
        '--host', 
        default=os.getenv('FLASK_HOST', '127.0.0.1'),
        help='The host IP to bind to'
    )
    parser.add_argument(
        '--port', 
        type=int,
        default=int(os.getenv('FLASK_PORT', '5000')),
        help='The port to bind to'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        default=os.getenv('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes'),
        help='Run the server in debug mode'
    )
    return parser

def cleanup():
    """Clean up resources when the application exits"""
    try:
        from app.services.rfid_listener import stop_all_rfid_listeners
        stop_all_rfid_listeners()
        logging.info("Successfully cleaned up RFID listeners during shutdown")
    except Exception as e:
        logging.error(f"Error during cleanup: {str(e)}")

def signal_handler(sig, frame):
    """Handle interrupt signals gracefully"""
    logging.info(f"Received signal {sig}, shutting down...")
    cleanup()
    sys.exit(0)

if __name__ == '__main__':
    # Parse command line arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Set environment variables
    os.environ['FLASK_ENV'] = args.env
    os.environ['FLASK_DEBUG'] = '1' if args.debug else '0'
    
    # Register cleanup handlers
    atexit.register(cleanup)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create the app
    try:
        # Import the app only after setting environment variables
        from app import create_app
        
        # Choose the configuration class based on environment
        config_class = None
        if args.env == 'production':
            from app.config import ProductionConfig
            config_class = ProductionConfig
            if args.debug:
                print("WARNING: Debug mode should not be enabled in production")
        elif args.env == 'testing':
            from app.config import TestingConfig
            config_class = TestingConfig
        else:  # development
            from app.config import DevelopmentConfig
            config_class = DevelopmentConfig
        
        app = create_app(config_class)
        
        # Additional production checks
        if args.env == 'production':
            if args.host == '127.0.0.1':
                print("WARNING: In production, consider binding to '0.0.0.0' instead of '127.0.0.1'")
            
            # In production, validate that key environment variables are set
            try:
                config_class.validate()
            except Exception as e:
                print(f"ERROR: {str(e)}")
                sys.exit(1)
        
        # Run the application
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug,
            use_reloader=args.debug  # Disable reloader in production
        )
    except ImportError as e:
        print(f"ERROR: Failed to import app: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)