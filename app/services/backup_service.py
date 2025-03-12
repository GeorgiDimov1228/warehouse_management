import os
import time
import shutil
import logging
import threading
from flask import current_app

def backup_database():
    """Create a backup of the database with error handling and rotation"""
    try:
        backup_dir = current_app.config['BACKUP_DIR']
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_file = os.path.join(backup_dir, f"backup_{time.strftime('%Y%m%d%H%M%S')}.db")
        shutil.copy(current_app.config['DATABASE'], backup_file)
        logging.info(f"Database backup created: {backup_file}")
        
        # Rotate backups to keep only the latest 10
        backups = sorted([f for f in os.listdir(backup_dir) if f.startswith("backup_")])
        while len(backups) > 10:
            oldest = backups.pop(0)
            os.remove(os.path.join(backup_dir, oldest))
            logging.info(f"Removed old backup: {oldest}")
        
        return backup_file
    except PermissionError as e:
        logging.error(f"Permission denied creating backup: {str(e)}")
        raise
    except Exception as e:
        logging.error(f"Failed to create backup: {str(e)}")
        raise

def schedule_backup():
    """Schedule automatic database backups"""
    while True:
        time.sleep(current_app.config['BACKUP_INTERVAL'])
        try:
            backup_database()
        except Exception as e:
            logging.error(f"Backup failed, will retry: {str(e)}")

def start_backup_thread():
    """Start the backup thread as a daemon"""
    backup_thread = threading.Thread(target=schedule_backup, daemon=True)
    backup_thread.start()
    logging.info("Database backup service started")
    return backup_thread