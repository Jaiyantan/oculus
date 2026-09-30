# Oculus

E-commerce fraud prevention engine. Analyzes checkout transactions in real-time, blocks fraudulent activity instantly, and provides an ultra-premium Review Console for analysts.

## What it does

Monitors e-commerce checkout traffic in real-time. When it spots something suspicious—impossible travel, velocity attacks, extreme cart totals—it evaluates the risk and either blocks the transaction immediately or flags it for manual review.

**Core features:**
- Real-time Redis-backed rules engine (sub-50ms evaluation)
- Deep transaction context parsing and risk scoring
- Interactive Launch Console and Simulator for risk analysts
- Automated AWS SNS/SES email alerts for critical flags

## Stack

**Backend:** Python (FastAPI, SQLAlchemy, Redis)  
**Frontend:** React + Vite + Recharts  
**Protection:** Strict Rules Engine & AWS Webhooks

## Quick start

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
# Populate .env file with your PostgreSQL, Redis, and AWS credentials
python main.py

# Frontend
cd frontend
npm install && npm run dev
```

Dashboard: `http://localhost:5173`
Landing Page: `http://localhost:3333`

## Architecture

```
Transaction Payload → Rules Engine → Risk Assessor
                                      ↓
                         Redis Event Bus + Postgres DB
                                      ↓
                                  FastAPI API
                                      ↓
                              React Launch Console
```

## Security modules

- **Velocity Monitor:** Tracks rapid successive transactions from identical IPs or user IDs
- **Amount Anomaly:** Flags massive deviations from baseline cart values
- **Geo-Tracker:** Identifies impossible travel scenarios (e.g. login from NY and checkout from Tokyo 5 minutes later)
- **Review Pipeline:** Provides a seamless UI for human analysts to clear or block flagged items

## Team

Jaiyantan S, Ranen Joseph Solomon

Built for securing high-volume e-commerce infrastructure.

MIT License

---

## 🚀 Development Sprint

**Total Duration**: Intensive MVP Approach

| Sprint | Components | Status |
|--------|------------|--------|
| **Sprint 1** | Rules Engine + Database Schema | 🎯 Core Foundation |
| **Sprint 2** | FastAPI Backend + AWS Integration | 🛡️ Infrastructure |
| **Sprint 3** | Landing Page + Simulator | 🎭 Visualization |
| **Sprint 4** | Console Dashboard + Integration | 📊 Analytics |

### Implementation Strategy

**Parallel Development Tracks**:
- **Track 1**: Backend core (Rules Engine + Risk Assessor)
- **Track 2**: Real-time Analytics (Redis + Charts)
- **Track 3**: Frontend Launch Console (React + Vite)
