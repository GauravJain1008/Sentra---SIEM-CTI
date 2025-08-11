import time
import json
import requests
import argparse
import os

API_URL = "http://127.0.0.1:8000/api/ingest/"  # Your Django API endpoint

def tail_f(filepath):
    with open(filepath, 'r') as f:
        f.seek(0, os.SEEK_END)  # Go to end of file
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.2)
                continue
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
        print(f"Error: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True, help="Log file path (e.g., /var/log/syslog)")
    parser.add_argument("--host", default=os.uname().nodename)
    parser.add_argument("--source", default="syslog")
    args = parser.parse_args()

    print(f"[+] Watching {args.file} for logs...")
    for line in tail_f(args.file):
        send_log(line, args.host, args.source)
