import json
import os
from datetime import datetime

def write_json_log(event_type: str, payload: dict, logs_dir: str = "logs"):
    """
    Writes a single JSON log entry to the logs/ folder.

    Why this exists:
    - Helps you track the pipeline's behavior step-by-step
    - Makes debugging easier
    - Shows reviewers that you built proper observability

    Each log entry is appended to a single timestamped file.
    """

    # Ensure logs directory exists
    os.makedirs(logs_dir, exist_ok=True)

    # Log file is named by date-time for easy grouping
    log_file = os.path.join(logs_dir, f"run_{datetime.now().strftime('%Y%m%d')}.jsonl")

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "payload": payload
    }

    # Append the entry as a JSON line
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")
