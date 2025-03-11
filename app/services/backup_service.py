import os
import time
import shutil
import logging
import threading
from flask import current_app

def backup_database():
    """Create a backup of the database"""
    backup_dir = current_app.config['BACKUP_DIR']
    os.makedirs(backup_dir, exist_ok=True)
    
    backup_file = os.path.join(backup_dir, f"backup_{time.strftime('%Y%m%d%H%M%S')}.db")
    shutil.copy(current_app.config['DATABASE'], backup_file)
    logging.info(f"Database backup created: {backup_file}")
    return backup_file

def schedule_backup():
    """Schedule automatic database backups"""
    while True:
        time.sleep(current_app.config['BACKUP_INTERVAL'])
        backup_database()

def start_backup_thread():
    """Start the backup thread as a daemon"""
    backup_thread = threading.Thread(target=schedule_backup, daemon=True)
    backup_thread.start()
    logging.info("Database backup service started")
    return backup_thread
