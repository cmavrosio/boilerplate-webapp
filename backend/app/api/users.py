from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models.models import UserCreate, User, UserResponse
from app.core.dependencies import get_db_session
from app.core.security import get_password_hash
from app.core.auth import admin_required
from app.core.stripe_client import create_stripe_customer

router = APIRouter(
    prefix="/users", 
    tags=["users"]
)

@router.post("/", response_model=UserResponse)
def create_user(user_create: UserCreate, session: Session = Depends(get_db_session)):
    existing_user = session.exec(select(User).where(User.email == user_create.email)).all()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = get_password_hash(user_create.password)
    stripe_customer_id = create_stripe_customer(email=user_create.email, name=user_create.full_name)
    user = User(
        email=user_create.email,
        full_name=user_create.full_name,
        hashed_password=hashed_password,
        stripe_customer_id=stripe_customer_id
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return UserResponse.model_validate(user)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: Session = Depends(get_db_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user)

@router.get("/", response_model=List[UserResponse])
def get_all_users(session: Session = Depends(get_db_session), current_user: User = Depends(admin_required)):
    users = session.exec(select(User).order_by(User.id)).all()
    return [UserResponse.model_validate(user) for user in users]
