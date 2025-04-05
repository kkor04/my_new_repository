from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
from typing import Callable

class WatchdogHandler(FileSystemEventHandler):
    def __init__(self, callback: Callable[[str, str], None]):
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory:
            self.callback(event.src_path, "modified")

    def on_created(self, event):
        if not event.is_directory:
            self.callback(event.src_path, "created")

    def on_deleted(self, event):
        if not event.is_directory:
            self.callback(event.src_path, "deleted")

class WatchdogUtils:
    def __init__(self, path: str, callback: Callable[[str, str], None]):
        self.path = path
        self.callback = callback
        self.observer = Observer()

    def start(self):
        event_handler = WatchdogHandler(self.callback)
        self.observer.schedule(event_handler, self.path, recursive=True)
        self.observer.start()
        print(f"Started monitoring: {self.path}")

    def stop(self):
        self.observer.stop()
        self.observer.join()
        print(f"Stopped monitoring: {self.path}")

# Example usage
if __name__ == "__main__":
    def log_change(file_path, change_type):
        print(f"File {file_path} was {change_type}")

    path_to_watch = "."
    watchdog = WatchdogUtils(path_to_watch, log_change)
    try:
        watchdog.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watchdog.stop()
