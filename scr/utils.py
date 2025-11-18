# csv writer, logging helpers

# utils.py
import os
import csv
import json
from datetime import datetime

def ensure_dirs():
    os.makedirs("data/outputs", exist_ok=True)
    os.makedirs("data/raw_html", exist_ok=True)

def timestamp_str():
    return datetime.utcnow().strftime("%Y-%m-%dT%H%M%SZ")

def write_csv(rows, filename):
    if not rows:
        return
    keys = rows[0].keys()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

def save_raw_html(content, slug):
    path = f"data/raw_html/{slug}.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
