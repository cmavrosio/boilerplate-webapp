from fastapi import Depends
from app.db.database import get_session
from sqlmodel import Session

def get_db_session() -> Session:
    return next(get_session())
