from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.models import SubscriptionCreate, Subscription, SubscriptionResponse, User, Product
from app.core.dependencies import get_db_session
from app.core.auth import get_current_user, admin_required
from app.core.stripe_client import create_stripe_subscription

router = APIRouter(
    prefix="/subscriptions",
    tags=["subscriptions"]
)

@router.post("/", response_model=SubscriptionResponse)
def create_subscription(subscription_create: SubscriptionCreate, session: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    product = session.get(Product, subscription_create.product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    stripe_subscription_id = create_stripe_subscription(current_user.id, product.stripe_product_id)
    
    subscription = Subscription(
        user_id=current_user.id,
        product_id=product.id,
        stripe_subscription_id=stripe_subscription_id
    )
    
    session.add(subscription)
    session.commit()
    session.refresh(subscription)
    
    return SubscriptionResponse.from_orm(subscription)

@router.get("/{subscription_id}", response_model=SubscriptionResponse)
def read_subscription(subscription_id: int, session: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    subscription = session.get(Subscription, subscription_id)
    if not subscription or (not current_user.is_admin and subscription.user_id != current_user.id):
        raise HTTPException(status_code=404, detail="Subscription not found or not authorized")
    
    return SubscriptionResponse.from_orm(subscription)

@router.get("/", response_model=list[SubscriptionResponse])
def list_subscriptions(session: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        subscriptions = session.exec(select(Subscription)).all()
    else:
        subscriptions = session.exec(select(Subscription).where(Subscription.user_id == current_user.id)).all()
    return [SubscriptionResponse.from_orm(subscription) for subscription in subscriptions]

@router.delete("/{subscription_id}", response_model=dict)
def cancel_subscription(subscription_id: int, session: Session = Depends(get_db_session), current_user: User = Depends(get_current_user)):
    subscription = session.get(Subscription, subscription_id)
    if not subscription or subscription.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Subscription not found or not authorized")
    
    session.delete(subscription)
    session.commit()
    return {"detail": "Subscription cancelled successfully"}
