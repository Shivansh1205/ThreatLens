# ThreatLens

**Adaptive Behavior-Based Intrusion Detection and Threat Analysis System**

ThreatLens is a full-stack cybersecurity platform that ingests system logs, detects threats in real time, learns user behavior dynamically, and lets you query the system using a local LLM (Ollama Mistral) via a conversational chat interface.

---

## What It Does

- **Log Ingestion** — Accepts structured logs (user, IP, action, port, status) via REST API
- **Real-Time Threat Detection** — Scores each log for risk using rule-based detection (brute-force, unusual IP, sensitive ports, off-hours login)
- **Adaptive Behavior Learning** — Builds a behavioral profile per user and dynamically classifies them as `normal`, `suspicious`, or `high-risk` based on evolving patterns
- **Live Dashboard** — React frontend showing system overview, hot threats, user behavior panel, and live alert feed via WebSocket
- **LLM-Powered Chat** — Conversational threat assistant powered by Ollama (Mistral) running fully offline — ask questions like "Why is alice risky?" or "Which IPs are suspicious?"
- **PostgreSQL Backend** — Production-ready database replacing SQLite

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) |
| Database | PostgreSQL + SQLAlchemy |
| LLM | Ollama (Mistral) — local, offline |
| Frontend | React + Vite |
| HTTP Client | Axios |
| Real-Time | WebSocket |

---

## Project Structure

```
ThreatLens/
├── app/
│   ├── database/        # DB session, init, models
│   ├── models/          # SQLAlchemy ORM models
│   ├── routes/          # FastAPI route handlers (logs, alerts, chat, dashboard)
│   ├── schemas/         # Pydantic request/response schemas
│   ├── services/        # Business logic (detection, profiling, LLM)
│   └── main.py          # App entry point
├── sentinelai-frontend/
│   ├── src/
│   │   ├── components/  # React components (Chat, Alerts, HotThreats, Dashboard)
│   │   ├── App.jsx
│   │   └── api.js
│   └── package.json
├── seed_data.py         # Populate DB with test scenarios
├── requirements.txt
└── .env                 # Database URL (not committed)
```

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 17
- [Ollama](https://ollama.com/download) with Mistral model

---

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/your-username/ThreatLens.git
cd ThreatLens
```

### 2. Set up Python environment

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 3. Set up PostgreSQL

Create the database:

```bash
psql -U postgres -c "CREATE DATABASE sentinelai;"
```

Create a `.env` file in the project root:

```
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/sentinelai
```

### 4. Start Ollama (Mistral)

```bash
ollama pull mistral
ollama run mistral
```

Keep this running in a separate terminal.

### 5. Start the backend

```bash
uvicorn app.main:app --reload
```

Backend runs at: http://127.0.0.1:8000
API docs at: http://127.0.0.1:8000/docs

### 6. Seed test data (optional)

```bash
python seed_data.py
```

### 7. Start the frontend

```bash
cd sentinelai-frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:5173

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/log` | Ingest a log entry |
| GET | `/alerts` | Get all alerts |
| GET | `/alerts/recent` | Get alerts from last N hours |
| GET | `/dashboard` | System overview stats |
| POST | `/chat` | LLM-powered threat chat |
| WS | `/ws/alerts` | WebSocket live alert feed |

### Example — Ingest a log

```bash
curl -X POST http://127.0.0.1:8000/log \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":\"alice\",\"ip\":\"10.99.0.1\",\"timestamp\":\"2026-03-19T02:15:30Z\",\"action\":\"login\",\"status\":\"failed\",\"port\":22}"
```

### Example — Chat

```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"Why is alice risky?\",\"context\":\"💬 Ask a custom question\"}"
```

---

## How Adaptive Learning Works

ThreatLens does not use heavy ML models. Instead it uses dynamic rule-based logic:

- Builds a baseline per user from login history (usual IP, typical login hours, average login frequency)
- Adjusts anomaly thresholds based on the user's own history — a user who frequently logs in at night gets less penalty for off-hours logins
- Classifies each user as `normal`, `suspicious`, or `high-risk` after every log ingestion
- Updates classification continuously as new logs arrive

---

## Chat Interface

The chat assistant is powered by Mistral running locally via Ollama. It works fully offline with no external API calls.

Start a conversation from the dashboard and choose from:

- Show high-risk users
- Summarise recent alerts
- Investigate a specific user
- Check risky IPs or ports
- Ask a custom question

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
