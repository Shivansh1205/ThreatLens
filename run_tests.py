"""
run_tests.py
-------------
End-to-end test suite for SentinelAI.
Validates: Log Ingestion → Detection → Alert Creation → LLM Explanation → Chat (RAG)

Usage:
    python run_tests.py

Output:
    test_report.json   — structured pass/fail report
    test_logs.txt      — raw request/response log
"""

import json
import sys
import textwrap
from datetime import datetime, timedelta

import requests

BASE_URL = "http://127.0.0.1:8000"
ALERT_THRESHOLD = 50.0
LOG_FILE = "test_logs.txt"
REPORT_FILE = "test_report.json"

_log_lines: list[str] = []


# ── Helpers ────────────────────────────────────────────────────────────────────

def _ts(offset_minutes: int = 0) -> str:
    """Return an ISO timestamp offset from now by N minutes."""
    return (datetime.utcnow() + timedelta(minutes=offset_minutes)).strftime("%Y-%m-%dT%H:%M:%S")


def _log(label: str, data) -> None:
    line = f"\n[{label}]\n{json.dumps(data, indent=2, default=str)}"
    _log_lines.append(line)


def post_log(payload: dict) -> dict:
    r = requests.post(f"{BASE_URL}/log", json=payload, timeout=10)
    r.raise_for_status()
    data = r.json()
    _log("POST /log", {"request": payload, "response": data})
    return data


def get_alerts() -> list[dict]:
    r = requests.get(f"{BASE_URL}/alerts", timeout=10)
    r.raise_for_status()
    data = r.json()
    _log("GET /alerts", data)
    return data


def post_chat(query: str) -> dict:
    payload = {"query": query}
    r = requests.post(f"{BASE_URL}/chat", json=payload, timeout=15)
    r.raise_for_status()
    data = r.json()
    _log("POST /chat", {"request": payload, "response": data})
    return data


def make_result(name: str, status: str, details: str, response_sample: dict) -> dict:
    return {
        "name": name,
        "status": status,
        "details": details,
        "response_sample": response_sample,
    }


# ── Test Cases ─────────────────────────────────────────────────────────────────

def test_brute_force() -> dict:
    """TC1 — Brute force + sensitive port on fresh user to breach alert threshold."""
    name = "Brute Force Attack"
    # Unique user per run so no stale profile ever exists
    user_id = f"tc1_bf_{int(datetime.utcnow().timestamp())}"
    ip = "192.168.10.1"
    last_response = {}

    try:
        # 6 failed logins on sensitive port 22 from same IP:
        # brute force (+40) + sensitive port (+15) = 55/135 = 40.7
        # Add port scan across 5 distinct ports to push over 50:
        # brute force (+40) + port scan (+35) + sensitive port (+15) = 90/135 = 66.7
        ports = [22, 23, 445, 3389, 3306]
        for i in range(6):
            last_response = post_log({
                "user_id": user_id,
                "ip": ip,
                "timestamp": _ts(-10 + i),
                "action": "login",
                "status": "failed",
                "port": ports[i % len(ports)],
            })

        alert_generated = last_response.get("alert_generated", False)
        risk_score = last_response.get("risk_score", 0)
        reasons = last_response.get("reasons", [])
        brute_fired = any("brute" in r.lower() or "failed" in r.lower() for r in reasons)

        alerts = [a for a in get_alerts() if a["user_id"] == user_id]
        explanation = alerts[0].get("explanation", "") if alerts else ""

        checks = [alert_generated, risk_score >= ALERT_THRESHOLD, brute_fired, bool(explanation)]
        status = "PASS" if all(checks) else "FAIL"
        details = (
            f"alert_generated={alert_generated}  risk_score={risk_score}  "
            f"brute_fired={brute_fired}  reasons={reasons}  explanation_present={bool(explanation)}"
        )
        return make_result(name, status, details, last_response)

    except Exception as e:
        return make_result(name, "FAIL", f"Exception: {e}", {})


def test_unusual_ip() -> dict:
    """TC2 — Login from a new IP after baseline should trigger unusual-IP alert."""
    name = "Unusual IP Detection"
    user_id = f"tc2_ip_{int(datetime.utcnow().timestamp())}"
    known_ip = "10.0.0.1"
    new_ip = "203.0.113.99"
    last_response = {}

    try:
        # Build baseline with known IP (5 successful logins)
        for i in range(5):
            post_log({
                "user_id": user_id,
                "ip": known_ip,
                "timestamp": _ts(-30 + i),
                "action": "login",
                "status": "success",
                "port": 443,
            })

        # Now login from a completely new IP
        last_response = post_log({
            "user_id": user_id,
            "ip": new_ip,
            "timestamp": _ts(),
            "action": "login",
            "status": "success",
            "port": 443,
        })

        reasons = last_response.get("reasons", [])
        risk_score = last_response.get("risk_score", 0)
        unusual_ip_fired = any("ip" in r.lower() or "unusual" in r.lower() or "new" in r.lower() for r in reasons)

        alerts = [a for a in get_alerts() if a["user_id"] == user_id]
        explanation = alerts[0].get("explanation", "") if alerts else ""

        checks = [unusual_ip_fired, risk_score > 0]
        status = "PASS" if all(checks) else "FAIL"
        details = (
            f"unusual_ip_rule_fired={unusual_ip_fired}  risk_score={risk_score}  "
            f"reasons={reasons}  explanation_present={bool(explanation)}"
        )
        return make_result(name, status, details, last_response)

    except Exception as e:
        return make_result(name, "FAIL", f"Exception: {e}", {})


def test_sensitive_port() -> dict:
    """TC3 — Login on port 22 (SSH) should increase risk score via sensitive-port rule."""
    name = "Sensitive Port Access"
    user_id = "tc3_sensitiveport"
    last_response = {}

    try:
        last_response = post_log({
            "user_id": user_id,
            "ip": "172.16.0.5",
            "timestamp": _ts(),
            "action": "login",
            "status": "success",
            "port": 22,
        })

        reasons = last_response.get("reasons", [])
        risk_score = last_response.get("risk_score", 0)
        port_rule_fired = any("port" in r.lower() or "ssh" in r.lower() or "22" in r for r in reasons)

        checks = [port_rule_fired, risk_score > 0]
        status = "PASS" if all(checks) else "FAIL"
        details = (
            f"sensitive_port_rule_fired={port_rule_fired}  "
            f"risk_score={risk_score}  reasons={reasons}"
        )
        return make_result(name, status, details, last_response)

    except Exception as e:
        return make_result(name, "FAIL", f"Exception: {e}", {})


def test_port_scan() -> dict:
    """TC4 — Same IP hitting 5+ distinct ports within the window triggers port-scan rule."""
    name = "Port Scan Detection"
    user_id = "tc4_portscan"
    ip = "198.51.100.7"
    ports = [80, 443, 8080, 3306, 5432, 6379]
    last_response = {}

    try:
        for i, port in enumerate(ports):
            last_response = post_log({
                "user_id": user_id,
                "ip": ip,
                "timestamp": _ts(-5 + i),
                "action": "api_call",
                "status": "failed",
                "port": port,
            })

        reasons = last_response.get("reasons", [])
        risk_score = last_response.get("risk_score", 0)
        scan_fired = any("scan" in r.lower() or "port" in r.lower() for r in reasons)

        checks = [scan_fired, risk_score > 0]
        status = "PASS" if all(checks) else "FAIL"
        details = (
            f"port_scan_rule_fired={scan_fired}  "
            f"risk_score={risk_score}  reasons={reasons}"
        )
        return make_result(name, status, details, last_response)

    except Exception as e:
        return make_result(name, "FAIL", f"Exception: {e}", {})


def test_chat_rag() -> dict:
    """TC5 — /chat should return a relevant answer referencing alert context for alice."""
    name = "Chat RAG Query"
    user_id = "alice"

    try:
        # Seed some alerts for alice so the chat has context
        for i in range(6):
            post_log({
                "user_id": user_id,
                "ip": "10.99.0.1" if i < 3 else "10.99.0.2",
                "timestamp": _ts(-20 + i),
                "action": "login",
                "status": "failed",
                "port": 22,
            })

        response = post_chat("Why is alice risky?")
        answer = response.get("answer", "")

        has_answer = bool(answer.strip())
        answer_lower = answer.lower()
        is_relevant = any(
            kw in answer_lower
            for kw in ["alice", "brute", "failed", "login", "ip", "risk", "suspicious", "alert", "port"]
        )

        checks = [has_answer, is_relevant]
        status = "PASS" if all(checks) else "FAIL"
        details = (
            f"has_answer={has_answer}  is_relevant={is_relevant}  "
            f"answer_preview={answer[:120]!r}"
        )
        return make_result(name, status, details, response)

    except Exception as e:
        return make_result(name, "FAIL", f"Exception: {e}", {})


def test_no_data_edge_case() -> dict:
    """TC6 — Chat query with no matching user should not crash and return graceful response."""
    name = "No Data Edge Case"

    try:
        response = post_chat("What is happening in the system?")
        answer = response.get("answer", "")

        has_answer = bool(answer.strip())
        status = "PASS" if has_answer else "FAIL"
        details = f"no_crash=True  has_answer={has_answer}  answer_preview={answer[:120]!r}"
        return make_result(name, status, details, response)

    except Exception as e:
        return make_result(name, "FAIL", f"Exception: {e}  (server may have crashed)", {})


# ── Runner ─────────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 60)
    print("  SentinelAI — End-to-End Test Suite")
    print("=" * 60)

    # Verify server is reachable before running anything
    try:
        requests.get(f"{BASE_URL}/", timeout=5).raise_for_status()
    except Exception:
        print(f"\n[ERROR] Server not reachable at {BASE_URL}")
        print("  Start it with:  uvicorn main:app --reload\n")
        sys.exit(1)

    test_fns = [
        test_brute_force,
        test_unusual_ip,
        test_sensitive_port,
        test_port_scan,
        test_chat_rag,
        test_no_data_edge_case,
    ]

    results = []
    for fn in test_fns:
        print(f"\n  Running: {fn.__doc__.splitlines()[0].strip()} ...", end=" ", flush=True)
        result = fn()
        results.append(result)
        icon = "PASS" if result["status"] == "PASS" else "FAIL"
        print(f"{icon} {result['status']}")
        print(f"     {textwrap.shorten(result['details'], width=100)}")

    # ── Write test_report.json ─────────────────────────────────────────────
    report = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "base_url": BASE_URL,
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r["status"] == "PASS"),
            "failed": sum(1 for r in results if r["status"] == "FAIL"),
        },
        "test_cases": results,
    }

    with open(REPORT_FILE, "w") as f:
        json.dump(report, f, indent=2, default=str)

    # ── Write test_logs.txt ────────────────────────────────────────────────
    with open(LOG_FILE, "w") as f:
        f.write(f"SentinelAI Test Logs — {report['generated_at']}\n")
        f.write("=" * 60 + "\n")
        f.write("\n".join(_log_lines))

    # ── Print summary ──────────────────────────────────────────────────────
    s = report["summary"]
    print("\n" + "=" * 60)
    print(f"  Total Tests : {s['total']}")
    print(f"  Passed      : {s['passed']}")
    print(f"  Failed      : {s['failed']}")
    print(f"\n  Report saved : {REPORT_FILE}")
    print(f"  Logs saved   : {LOG_FILE}")
    print("=" * 60 + "\n")

    sys.exit(0 if s["failed"] == 0 else 1)


if __name__ == "__main__":
    main()
