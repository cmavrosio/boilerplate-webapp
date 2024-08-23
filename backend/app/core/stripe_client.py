import stripe
from app.core.config import settings
from fastapi import HTTPException, status

stripe.api_key = settings.STRIPE_API_KEY

def create_stripe_customer(email: str, name: str) -> str:
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
    subscription_product_id = settings.SUBSCRIPTION_PRODUCT_ID
    subscriptions = stripe.Subscription.list(customer=customer_id, status='all')
    active_subscriptions = [sub for sub in subscriptions.auto_paging_iter() if sub.status in ['active', 'trialing']]
    active_subscriptions = [sub for sub in active_subscriptions if sub.plan.product == subscription_product_id]
    return len(active_subscriptions) > 0

def has_purchased_lifetime_product(customer_id: str) -> bool:
    lifetime_product_id = settings.LIFETIME_PRODUCT_ID
    try:
        charges = stripe.Charge.list(customer=customer_id)
        for charge in charges.auto_paging_iter():
            if charge.paid and charge.amount_refunded == 0:
                if charge.metadata and charge.metadata.get("product_id") == lifetime_product_id:
                    return True

                if charge.invoice:
                    invoice = stripe.Invoice.retrieve(charge.invoice)
                    if invoice.status in ['paid', 'open']:  # Ensure invoice is finalized
                        for line_item in invoice.lines.data:
                            if line_item.price.product == lifetime_product_id:
                                return True
        return False
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    
def check_if_active_subscription(customer_id: str) -> bool:
    return has_active_subscription(customer_id) or has_purchased_lifetime_product(customer_id)
