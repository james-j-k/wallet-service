from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import engine, Base
from app import schemas, crud, models
from app.dependencies import get_db
from decimal import Decimal
from fastapi import Request
from app.logger import logger

app = FastAPI()

Base.metadata.create_all(bind=engine)


@app.post("/users", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    created_user = crud.create_user(db, user.email, user.password)

    if created_user is None:
        raise HTTPException(status_code=400, detail="Email already registered")

    return created_user


@app.post("/wallet", response_model=schemas.WalletResponse)
def create_wallet(request: schemas.WalletCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == request.user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.wallet:
        raise HTTPException(status_code=400, detail="Wallet already exists")

    return crud.create_wallet(db, user.id)


@app.post("/wallet/{wallet_id}/credit", response_model=schemas.WalletResponse)
def credit(wallet_id: str, request: schemas.AmountRequest, db: Session = Depends(get_db)):
    wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    return crud.credit_wallet(db, wallet, request.amount)


@app.post("/wallet/{wallet_id}/debit", response_model=schemas.WalletResponse)
def debit(wallet_id: str, request: schemas.AmountRequest, db: Session = Depends(get_db)):
    wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    updated = crud.debit_wallet(db, wallet, request.amount)
    if updated is None:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    return updated


@app.get("/wallet/{wallet_id}/balance")
def get_balance(wallet_id: str, db: Session = Depends(get_db)):
    wallet = db.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    return {"balance": wallet.balance}


@app.get("/wallet/{wallet_id}/ledger")
def get_ledger(wallet_id: str, db: Session = Depends(get_db)):
    entries = (
        db.query(models.LedgerEntry)
        .filter(models.LedgerEntry.wallet_id == wallet_id)
        .order_by(models.LedgerEntry.created_at.desc())
        .all()
    )
    return entries

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )