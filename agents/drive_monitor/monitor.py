"""
monitor.py

Detects new file uploads with metadata, evaluates them via LLM,
and sends notifications. Stores full metadata (including LLM status & feedback) in state.
"""

import json
import time
import signal
import sys
from pathlib import Path

from agents.drive_monitor.google_drive_service import (
    list_files, get_file_metadata, download_file, download_file_text
)
from agents.drive_monitor.state_manager import (
    load_known_files, save_known_files
)
from agents.critique_agent.llm_critique import (
    load_scope, evaluate_document
)
from agents.notification_agent.email_agent import (
    send_email
)

def graceful_exit(signum, frame):
    print("\n🔌 Exiting monitor.")
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, graceful_exit)

    # Determine project root
    root = Path(__file__).resolve().parents[3]
    cfg = json.loads((root / 'agentic_learning' / 'config' / 'drive_folder.json').read_text())
    folder_id = cfg['folder_id']
    interval = cfg.get('poll_interval_seconds', 60)
    scope_cfg = load_scope(root / 'agentic_learning' / 'config' / 'scope.json')
    recipients = cfg.get('notification_emails', [])

    print(f"▶️  Starting Drive Monitor (poll every {interval}s).")
    known_meta = load_known_files()    # file_id -> metadata dict

    while True:
        current_ids = list_files(folder_id).keys()
        new_ids = [fid for fid in current_ids if fid not in known_meta]

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if new_ids:
            for fid in new_ids:
                # 1) Fetch metadata
                meta = get_file_metadata(fid)

                print(f"\n🔔 [{timestamp}] Detected upload:")
                print(f"   • Name:     {meta['name']}")
                owner = meta['owners'][0]
                print(f"   • Uploader: {owner['email']} ({owner['name']})")
                print(f"   • When:     {meta['createdTime']}")
                print(f"   • Folder:   {', '.join(meta['folder_names'])}")

                # 2) Download & stream text
                local_path = download_file(fid, meta['name'])
                text = download_file_text(fid)

                # 3) LLM evaluation
                status, feedback = evaluate_document(text, scope_cfg)
                print(f"   • LLM verdict: {status}")

                # 4) Send appropriate email
                if status == "NEEDS_IMPROVEMENT":
                    send_email(
                        [owner['email']],
                        f"Please improve your notes: {meta['name']}",
                        feedback
                    )
                else:
                    summary = feedback.split('\n', 1)[1] if feedback.startswith("APPROVED") else feedback
                    send_email(
                        recipients,
                        f"New approved notes: {meta['name']}",
                        f"{summary}\n\nSee attached.",
                        attachment_path=local_path
                    )

                # 5) Record status & feedback in our state
                meta['status'] = status
                meta['feedback'] = feedback
                known_meta[fid] = meta
                save_known_files(known_meta)
        else:
            print(f"[{timestamp}] ✅ No new uploads.")

        time.sleep(interval)

if __name__ == '__main__':
    main()
