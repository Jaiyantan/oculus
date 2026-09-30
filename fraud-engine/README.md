# 🔍 Oculus — Fraud Rule Engine with Review Console

**Acentra Build to Care Hackathon**

Real-time fraud detection system with explainable risk scoring, a Policy-as-Code rule engine, and an interactive reviewer console.

## Architecture

- **Style**: Modular Monolith (sub-10ms latency budget for Tier-1 rules)
- **Backend**: FastAPI (Python) with PostgreSQL + Redis
- **Frontend**: React (Vite) with 2-second polling for real-time feel
- **Notifications**: AWS SNS + SES with circuit breaker protection

## Quick Start

### 1. Start Infrastructure
```bash
docker-compose up -d
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
# Create tables & seed demo data
python seed/seed_demo_data.py
# Start the API
uvicorn main:app --reload --port 8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Open in Browser
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

## Demo Scenarios

| Scenario | Trigger | Expected Score | Expected Tier |
|----------|---------|---------------|---------------|
| ⚡ Velocity Attack | 6 rapid transactions | 0.48 – 0.60 | flag_for_review |
| 💰 Amount Anomaly | $9,500 (baseline $48) | 0.65 – 0.80 | flag_for_review |
| 🌍 Impossible Travel | NYC→London in 3min + $8K | 0.87 – 0.95 | auto_block |

## Key Features

- **Policy-as-Code**: New rule = new Python file. Engine never changes.
- **Explainable Scores**: 0.0–1.0 with per-rule contribution breakdown
- **State Machine Reviews**: Enforced valid transitions (422 on invalid)
- **Append-Only Audit**: DPDP compliant, doubles as ML training data
- **Circuit Breaker**: AWS outage won't crash the transaction path
