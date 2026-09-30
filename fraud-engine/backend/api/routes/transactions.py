"""
Transaction route — POST /api/v1/transactions

The hot path. Receives a transaction, runs the rule engine, returns the risk assessment.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.deps import get_db, get_redis
from schemas.transaction import TransactionCreate, TransactionResponse
from services.transaction_service import process_transaction

router = APIRouter(prefix="/api/v1/transactions", tags=["transactions"])


@router.post("", response_model=TransactionResponse)
def create_transaction(
    tx_data: TransactionCreate,
    db: Session = Depends(get_db),
    redis_client=Depends(get_redis),
):
    """
    Process a new transaction through the fraud rule engine.

    Returns the risk score, risk tier, per-rule breakdown,
    and optional fraud flag ID if the transaction was flagged.
    """
    try:
        result = process_transaction(db, redis_client, tx_data.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
