from sqlalchemy.orm import Session
from app import models
from passlib.context import CryptContext
from app.logger import logger
from sqlalchemy.exc import IntegrityError
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(db: Session, email: str, password: str):
    try:
        password = password[:72]
        hashed = pwd_context.hash(password)

        user = models.User(email=email, hashed_password=hashed)
        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"User created: {user.id}")
        return user

    except IntegrityError:
        db.rollback()
        logger.warning(f"Duplicate email registration attempt: {email}")
        return None

    except Exception as e:
        db.rollback()
        logger.error(f"User creation failed: {str(e)}")
        raise


def create_wallet(db: Session, user_id):
    wallet = models.Wallet(user_id=user_id)
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


def credit_wallet(db: Session, wallet, amount):
    try:
        wallet.balance += amount

        entry = models.LedgerEntry(
            wallet_id=wallet.id,
            amount=amount,
            type="CREDIT"
        )

        db.add(entry)
        db.commit()
        db.refresh(wallet)

        logger.info(f"Credited {amount} to wallet {wallet.id}")

        return wallet

    except Exception as e:
        db.rollback()
        logger.error(f"Credit failed for wallet {wallet.id}: {str(e)}")
        raise


def debit_wallet(db: Session, wallet, amount):
    if wallet.balance < amount:
        logger.warning(f"Insufficient balance for wallet {wallet.id}")
        return None

    try:
        wallet.balance -= amount

        entry = models.LedgerEntry(
            wallet_id=wallet.id,
            amount=amount,
            type="DEBIT"
        )

        db.add(entry)
        db.commit()
        db.refresh(wallet)

        logger.info(f"Debited {amount} from wallet {wallet.id}")

        return wallet

    except Exception as e:
        db.rollback()
        logger.error(f"Debit failed for wallet {wallet.id}: {str(e)}")
        raise