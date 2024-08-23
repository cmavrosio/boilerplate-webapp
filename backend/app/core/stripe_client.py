import stripe
from app.core.config import settings
from fastapi import HTTPException, status

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

def create_stripe_customer(email: str, name: str):
    customer = stripe.Customer.create(
        email=email,
        name=name,
    )
    return customer.id


def get_all_products_with_prices() -> list:
    try:
        products = [] 
        stripe_products = stripe.Product.list()
        for product in stripe_products.get("data"):
            product_price_data = stripe.Price.retrieve(product.get('default_price'))
            product['price_info'] = product_price_data
            products.append(product)
        return products
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
