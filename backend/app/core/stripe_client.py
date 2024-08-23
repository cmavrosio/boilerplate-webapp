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
    
def has_active_subscription(customer_id: str) -> bool:
    subscriptions = stripe.Subscription.list(customer=customer_id, status='all')
    active_subscriptions = [sub for sub in subscriptions.auto_paging_iter() if sub.status in ['active', 'trialing']]
    return len(active_subscriptions) > 0


def has_purchased_lifetime_product(customer_id: str, lifetime_product_id: str) -> bool:
    charges = stripe.Charge.list(customer=customer_id)
    for charge in charges.auto_paging_iter():
        if charge.paid and charge.amount_refunded == 0:
            for line_item in charge.invoice.lines.data:
                if line_item.price.product == lifetime_product_id:
                    return True
    return False



