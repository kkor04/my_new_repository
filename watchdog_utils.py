from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from logging_utils import log

class FileMonitorHandler(FileSystemEventHandler):
    """Custom handler for file system events."""
    def on_modified(self, event):
        if not event.is_directory:
            log.log_info(f"File modified: {event.src_path}")

    def on_created(self, event):
        if not event.is_directory:
            log.log_info(f"File created: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            log.log_info(f"File deleted: {event.src_path}")

class FileMonitor:
    """File monitoring utility using watchdog."""
    def __init__(self, directory: str):
        self.directory = directory
        self.observer = Observer()

    def start(self):
        """Start monitoring the directory."""
        event_handler = FileMonitorHandler()
        self.observer.schedule(event_handler, self.directory, recursive=True)
        self.observer.start()
        log.log_info(f"Started monitoring directory: {self.directory}")

    def stop(self):
        """Stop monitoring the directory."""
        self.observer.stop()
        self.observer.join()
        log.log_info(f"Stopped monitoring directory: {self.directory}")

# Example usage
if __name__ == "__main__":
    monitor = FileMonitor(directory=".")
    try:
        monitor.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()
