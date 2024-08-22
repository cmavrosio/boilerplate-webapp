import stripe
from app.core.config import settings

stripe.api_key = settings.STRIPE_API_KEY

def create_stripe_product(name: str) -> str:
    product = stripe.Product.create(name=name)
    return product.id

def create_stripe_subscription(customer_id: str, price_id: str) -> str:
    subscription = stripe.Subscription.create(
        customer=customer_id,
        items=[{"price": price_id}],
    )
    return subscription.id
