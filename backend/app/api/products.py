
from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.core.stripe_client import get_all_products_with_prices
from app.models.models import ProductResponse, User
from app.core.dependencies import get_db_session
from app.core.auth import get_current_user


router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.get("/", response_model=list[ProductResponse])
async def get_products( db: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    return get_all_products_with_prices()