"""
Oculus Fraud Engine — FastAPI Application Entry Point

A real-time fraud detection system with:
- Policy-as-Code rule engine (decorator registry pattern)
- Per-user statistical baselines (Welford's algorithm)
- Tiered risk scoring (0.0 to 1.0) with per-rule contribution breakdown
- State machine-driven review workflow
- Circuit-breaker-protected AWS SNS/SES notifications
- Append-only audit trail (DPDP compliant)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import rule modules to trigger @register_rule decorators
import core.rules  # noqa: F401

from api.routes import transactions, fraud_flags, reviews, health


app = FastAPI(
    title="Oculus Fraud Engine",
    description="Real-time fraud detection with explainable risk scoring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — allow frontend in development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock down in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routes
app.include_router(transactions.router)
app.include_router(fraud_flags.router)
app.include_router(reviews.router)
app.include_router(health.router)

from db.session import engine
from db.base import Base

@app.on_event("startup")
def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Database table creation warning: {e}")


@app.get("/")
def root():
    return {
        "name": "Oculus Fraud Engine",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }
