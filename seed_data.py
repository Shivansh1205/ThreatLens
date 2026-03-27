"""
seed_data.py
------------
Injects realistic log data into SentinelAI to generate alerts visible on the frontend.
Run with: python seed_data.py
"""
import requests
from datetime import datetime, timedelta

BASE = "http://127.0.0.1:8000"

def ts(offset_minutes=0):
    return (datetime.utcnow() + timedelta(minutes=offset_minutes)).strftime("%Y-%m-%dT%H:%M:%S")

def log(user_id, ip, action, status, port, offset=0):
    r = requests.post(f"{BASE}/log", json={
        "user_id": user_id,
        "ip": ip,
        "timestamp": ts(offset),
        "action": action,
        "status": status,
        "port": port,
    })
    data = r.json()
    print(f"  [{user_id}] score={data.get('risk_score')} alerted={data.get('alert_generated')} reasons={data.get('reasons','')}")
    return data

print("\n=== Seeding SentinelAI with threat data ===\n")

# ── Scenario 1: alice — brute force + unusual IP + sensitive port ──────────
print("Scenario 1: alice — brute force attack on SSH")
# Establish baseline (known IP)
for i in range(3):
    log("alice", "192.168.1.10", "login", "success", 443, offset=-60+i)

# 6 failed logins from new IP on port 22 → brute force + unusual IP + sensitive port
for i in range(6):
    log("alice", "10.99.0.1", "login", "failed", 22, offset=-8+i)

# ── Scenario 2: bob — multiple failed logins + risky port ─────────────────
print("\nScenario 2: bob — credential stuffing on RDP")
for i in range(3):
    log("bob", "172.16.0.5", "login", "success", 443, offset=-90+i)

for i in range(5):
    log("bob", "203.0.113.42", "login", "failed", 3389, offset=-5+i)

# ── Scenario 3: charlie — unusual IP + sensitive port ─────────────────────
print("\nScenario 3: charlie — suspicious access from new IP on MySQL")
log("charlie", "10.0.0.1", "login", "success", 443, offset=-120)
log("charlie", "10.0.0.1", "login", "success", 443, offset=-100)
log("charlie", "198.51.100.99", "login", "failed", 3306, offset=-2)
log("charlie", "198.51.100.99", "api_call", "failed", 3306, offset=-1)
log("charlie", "198.51.100.99", "login", "failed", 22, offset=0)

# ── Scenario 4: sysadmin — normal activity (low risk, no alert) ───────────
print("\nScenario 4: sysadmin — normal activity (should NOT alert)")
for i in range(4):
    log("sysadmin", "10.10.0.1", "login", "success", 443, offset=-30+i)

print("\n=== Done. Check http://localhost:5173 ===\n")
