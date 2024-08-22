from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta

from app.core.jwt import create_access_token
from app.core.config import settings
from app.core.auth import authenticate_user, get_current_user
from app.core.dependencies import get_db_session
from app.models.models import User
from app.core.security import get_password_hash

router = APIRouter()

@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_db_session)):
    user = authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register/", response_model=User)
def register_user(user: User, session: Session = Depends(get_db_session)):
    user.hashed_password = get_password_hash(user.hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/me/", response_model=User)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
