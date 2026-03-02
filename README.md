# Wallet Service

## Phase 1 Features
- User creation
- Wallet creation
- Credit
- Debit
- Balance retrieval
- Transaction ledger
- PostgreSQL persistence
- Validation & constraints
- Structured logging
- Error handling

## Tech Stack
- FastAPI
- PostgreSQL
- SQLAlchemy
- Pydantic

## How to Run Locally

1. Create virtual environment
2. Install dependencies:
   pip install -r requirements.txt
3. Create .env file with:
   DATABASE_URL=...
   SECRET_KEY=...
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
4. Run:
   uvicorn app.main:app --reload