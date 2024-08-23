
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
import stripe
from app.models.models import Product, ProductResponse, User
from app.core.dependencies import get_db_session
from app.core.auth import get_current_user, admin_required
from app.core.config import settings  # Import settings to get your Stripe API key

# Initialize the Stripe client with your secret key
stripe.api_key = settings.STRIPE_API_KEY

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.get("/", response_model=list[ProductResponse])
async def get_products(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user)
):
    try:
        # Retrieve the list of products from Stripe
        products = [] 
        stripe_products = stripe.Product.list()
        for product in stripe_products.get("data"):
            product_price_data = stripe.Price.retrieve(product.get('default_price'))
            product['price_info'] = product_price_data
            products.append(product)
        return products
            

    except stripe.error.StripeError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    

# Additional routes for creating, updating, and deleting products would go here
