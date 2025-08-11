import subprocess
import threading
import time
import requests
import os
import glob
import re
from datetime import datetime
API_URL = "http://127.0.0.1:8000/api/ingest/"  # <-- trailing slash
HOST = os.uname().nodename

SESSION = requests.Session()


JOURNAL_REGEX = re.compile(
    r"^(?P<time>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[-+]\d{2}:\d{2}) (?P<host>\S+) (?P<source>[^:]+): (?P<msg>.*)$"
)

def parse_journal_line(line):
    try:
        parts = line.split(" ", 2)
        ts = parts[0]
        msg = parts[2] if len(parts) > 2 else line
        return ts, msg
    except Exception:
        return datetime.utcnow().isoformat(), line


def send_log(source, message, log_time=None):
    log = {
        "ts": log_time or datetime.utcnow().isoformat(),
        "host": HOST,
        "source": source,
        "level": "INFO",
        "message": message.strip()
    }
    try:
        r = requests.post(API_URL, json=log, timeout=2)
        if r.status_code != 200:
            print(f"[!] Server response: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"[!] Error sending log: {e}")

def stream_journal():
    process = subprocess.Popen(
        ["journalctl", "-f", "-o", "short-iso"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    for line in iter(process.stdout.readline, ''):
        if line:
            ts, msg = parse_journal_line(line)
            send_log("journalctl", msg, ts)


def tail_file(filepath):
    try:
        with open(filepath, 'r', errors='ignore') as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if line:
                    send_log(os.path.basename(filepath), line)
                else:
                    time.sleep(0.2)
    except PermissionError:
        print(f"[!] Skipping {filepath} (permission denied)")
    except FileNotFoundError:
        pass

def watch_log_files():
    # grab a bunch of common logs, skip those you can't read
    candidates = [
        "/var/log/*.log",
        "/var/log/*/*.log",
    ]
    files = set()
    for pat in candidates:
        files.update(glob.glob(pat))

    for log_file in sorted(files):
        t = threading.Thread(target=tail_file, args=(log_file,), daemon=True)
        t.start()

if __name__ == "__main__":
    print("[+] Streaming logs from journalctl and /var/log/**/*.log ...")
    threading.Thread(target=stream_journal, daemon=True).start()
    watch_log_files()
    while True:
        time.sleep(1)
