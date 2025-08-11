import subprocess
import requests
import time
import json
import os

API_URL = "http://127.0.0.1:8000/api/ingest/"

def stream_journal():
    cmd = ["journalctl", "-f", "-o", "short"]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    for line in iter(process.stdout.readline, ''):
        yield line.strip()

def send_log(line, host, source):
    payload = {
        "ts": time.strftime('%Y-%m-%dT%H:%M:%S'),
        "host": host,
        "source": source,
        "level": "INFO",
        "message": line,
    }
    try:
        r = requests.post(API_URL, json=payload)
        if r.status_code != 202:
            print(f"Failed: {r.status_code}, {r.text}")
    except Exception as e:
        print(f"Error sending log: {e}")

if __name__ == "__main__":
    host = os.uname().nodename
    print(f"[+] Streaming systemd logs from journalctl...")
    for log_line in stream_journal():
        send_log(log_line, host, "systemd")
