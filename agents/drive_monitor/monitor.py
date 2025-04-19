"""
monitor.py

Detects new file uploads with metadata, evaluates them via LLM,
generates a polished email, and sends notifications.
Stores full metadata (including status & feedback) in state.
"""

import json
import time
import signal
import sys
from pathlib import Path

from agents.drive_monitor.google_drive_service import (
    list_files,
    get_file_metadata,
    download_file,
    download_file_text
)
from agents.drive_monitor.state_manager import (
    load_known_files,
    save_known_files
)
from agents.critique_agent.llm_critique import (
    load_scope,
    evaluate_document,
    generate_email_content
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
    cfg = json.loads(
        (root / 'agentic_learning' / 'config' / 'drive_folder.json').read_text()
    )
    folder_id   = cfg['folder_id']
    interval    = cfg.get('poll_interval_seconds', 60)
    recipients  = cfg.get('notification_emails', [])

    scope_cfg = load_scope(root / 'agentic_learning' / 'config' / 'scope.json')

    print(f"▶️  Starting Drive Monitor (poll every {interval}s).")
    known_meta = load_known_files()  # file_id -> metadata dict

    while True:
        current_ids = list(list_files(folder_id).keys())
        new_ids     = [fid for fid in current_ids if fid not in known_meta]

        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        if new_ids:
            for fid in new_ids:
                meta = get_file_metadata(fid)
                print(f"\n🔔 [{timestamp}] Detected upload: {meta['name']} by {meta['owners'][0]['email']}")

                # Download & stream text
                local_path = download_file(fid, meta['name'])
                text       = download_file_text(fid)

                # LLM evaluation
                status, feedback = evaluate_document(text, scope_cfg)
                print(f"   • Verdict: {status}")

                # Generate email content
                subject, body = generate_email_content(meta, status, feedback)
                drive_link = f"https://drive.google.com/file/d/{fid}/view"
                
                # Add the drive link to the body with markdown formatting
                formatted_body = f"{body}\n\n🔗 [Drive Link - Resources & Examples]({drive_link})"

                # Choose recipients
                if status == "NEEDS_IMPROVEMENT":
                    to_list = [meta['owners'][0]['email']]
                else:
                    to_list = recipients

                # Send email with HTML formatting support
                send_email(
                    to_list,
                    subject,
                    formatted_body,
                    attachment_path=local_path if status == "APPROVED" else None
                )

                # Record status & feedback in state
                meta['status']   = status
                meta['feedback'] = feedback
                known_meta[fid]  = meta
                save_known_files(known_meta)
        else:
            print(f"[{timestamp}] ✅ No new uploads.")

        time.sleep(interval)


if __name__ == '__main__':
    main()