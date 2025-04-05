import os

LOG_DIR = "logs"

def view_logs(log_type: str):
    """View logs of a specific type."""
    log_file = os.path.join(LOG_DIR, f"{log_type}.log")
    if not os.path.exists(log_file):
        print(f"No logs found for type: {log_type}")
        return

    with open(log_file, "r") as f:
        print(f.read())
