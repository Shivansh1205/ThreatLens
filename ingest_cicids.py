"""
CICIDS Dataset Ingestion Script
Streams rows from all CSVs in MachineLearningCSV/ into the ThreatLens /log endpoint.

Usage:
    python ingest_cicids.py                  # all files, 100 rows each
    python ingest_cicids.py --limit 200      # 200 rows per file
    python ingest_cicids.py --delay 0.05     # faster streaming
    python ingest_cicids.py --file Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv
"""

import argparse
import glob
import os
import time
from datetime import datetime, timezone

import pandas as pd
import requests

BACKEND = "http://127.0.0.1:8000/log"
CSV_DIR = "MachineLearningCSV/MachineLearningCVE"

LABEL_MAP = {"BENIGN": "success"}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strip leading/trailing whitespace from all column names."""
    df.columns = df.columns.str.strip()
    return df


def make_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_log(row: pd.Series, idx: int) -> dict:
    label = str(row.get("Label", "BENIGN")).strip()
    status = LABEL_MAP.get(label, "failed")

    if status == "failed":
        user_id = "attacker_1"
        ip = "10.0.0.1"
    else:
        user_id = "normal_user"
        ip = "192.168.1.10"

    port = int(row.get("Destination Port", 0))
    if port < 0 or port > 65535:
        port = 0

    print(f"  [build] user={user_id} status={status} port={port} label={label}")

    return {
        "user_id": user_id,
        "ip": ip,
        "timestamp": make_timestamp(),
        "action": "login",
        "status": status,
        "port": port,
    }


def stream_file(path: str, limit: int, delay: float) -> tuple[int, int]:
    """Stream rows from one CSV. Returns (sent, alerted) counts."""
    print(f"\n📂 {os.path.basename(path)}")

    try:
        df = normalize_columns(pd.read_csv(path, low_memory=False))
    except Exception as e:
        print(f"  ✗ Failed to read: {e}")
        return 0, 0

    attack_df = df[df["Label"].str.strip() != "BENIGN"]
    benign_df = df[df["Label"].str.strip() == "BENIGN"]

    if attack_df.empty:
        print("  ⚠ No attack rows in this file, skipping.")
        return 0, 0

    n_attack = min(len(attack_df), (limit * 2) // 3)
    n_benign = min(len(benign_df), limit - n_attack)

    df = pd.concat([
        attack_df.sample(n=n_attack, replace=False),
        benign_df.sample(n=n_benign, replace=False) if n_benign > 0 else pd.DataFrame(),
    ]).sample(frac=1).reset_index(drop=True).head(limit)
    sent = alerted = 0

    for idx, (_, row) in enumerate(df.iterrows()):
        log = build_log(row, idx)

        try:
            res = requests.post(BACKEND, json=log, timeout=10)
            data = res.json()
            sent += 1

            label = str(row.get("Label", "BENIGN")).strip()
            alert_flag = "🚨" if data.get("alerted") else "  "
            alerted += int(data.get("alerted", False))

            print(
                f"  {alert_flag} [{idx+1:>4}/{len(df)}] "
                f"{log['user_id']:<28} port={log['port']:<6} "
                f"risk={data.get('risk_score', 0):<4} label={label}"
            )
        except requests.exceptions.ConnectionError:
            print("  ✗ Cannot reach backend. Is uvicorn running?")
            return sent, alerted
        except Exception as e:
            print(f"  ✗ Row {idx}: {e}")

        time.sleep(delay)

    return sent, alerted


def main():
    parser = argparse.ArgumentParser(description="Stream CICIDS dataset into ThreatLens")
    parser.add_argument("--limit", type=int, default=100, help="Rows per file (default: 100)")
    parser.add_argument("--delay", type=float, default=0.1, help="Seconds between rows (default: 0.1)")
    parser.add_argument("--file", type=str, default=None, help="Stream a single file by name")
    args = parser.parse_args()

    if args.file:
        files = [os.path.join(CSV_DIR, args.file)]
    else:
        files = sorted(glob.glob(os.path.join(CSV_DIR, "*.csv")))

    if not files:
        print(f"No CSV files found in {CSV_DIR}/")
        return

    print(f"🛡️  ThreatLens CICIDS Ingestion")
    print(f"   Files  : {len(files)}")
    print(f"   Limit  : {args.limit} rows/file")
    print(f"   Delay  : {args.delay}s between rows")
    print(f"   Backend: {BACKEND}\n")

    total_sent = total_alerted = 0
    for path in files:
        s, a = stream_file(path, args.limit, args.delay)
        total_sent += s
        total_alerted += a

    print(f"\n✅ Done — {total_sent} logs sent, {total_alerted} alerts generated")


if __name__ == "__main__":
    main()
