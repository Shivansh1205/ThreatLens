# ThreatLens Backend

Adaptive Behavior-Based Intrusion Detection and Threat Analysis System using FastAPI.

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies.
3. Run the API server.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The SQLite database file `threatlens.db` is created at the project root on first run.

## Example Requests

Ingest a log:

```bash
curl -X POST http://127.0.0.1:8000/log ^
  -H "Content-Type: application/json" ^
  -d "{\"user_id\":\"u123\",\"ip\":\"203.0.113.10\",\"timestamp\":\"2026-03-19T10:15:30Z\",\"action\":\"login\",\"status\":\"failed\",\"port\":22}"
```

Get all alerts:

```bash
curl http://127.0.0.1:8000/alerts
```

Get recent alerts (last 24 hours):

```bash
curl "http://127.0.0.1:8000/alerts/recent?hours=24"
```
