"""
state_manager.py

Handles loading and saving known file state with full metadata,
including LLM status and feedback, to detect new uploads and track their review.

State schema:
{
  "<file_id>": {
    "id": "…",
    "name": "…",
    "owners": [ { "name": "…", "email": "…" }, … ],
    "createdTime": "…",
    "folder_names": [ "…", … ],
    "status": "APPROVED" | "NEEDS_IMPROVEMENT",
    "feedback": "…"
  },
  …
}
"""

import json
import os

STATE_DIR = 'state'
STATE_FILE = os.path.join(STATE_DIR, 'known_files.json')

def load_known_files() -> dict:
    """
    Load known files metadata dict from state file.
    Returns a dict mapping file_id -> metadata dict (including status & feedback).
    """
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_known_files(files_metadata: dict) -> None:
    """
    Save current files metadata dict to state file.
    files_metadata should follow the schema shown above.
    """
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(files_metadata, f, indent=2)
