from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from app.core.dependencies import get_db_session
from app.core.auth import get_current_user
from app.core.stripe_client import has_active_subscription, has_purchased_lifetime_product
from app.models.models import User
import stripe
from pydantic import BaseModel
from app.core.config import settings

class CheckoutSessionRequest(BaseModel):
    price_id: str
    mode: str
    product_id: str

router = APIRouter(
    prefix="/subscriptions",  
    tags=["subscriptions"],  
)

endpoint_secret = settings.ENDPOINT_SECRET

@router.get("/status")
def get_subscription_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db_session)):
    # Check the subscription status using the stripe client
    subscription_status = has_active_subscription(current_user.stripe_customer_id)
    lifetime_status = has_purchased_lifetime_product(current_user.stripe_customer_id, "prod_Qi3UDIiNl31PYj")

    return {"subscription_status": subscription_status or lifetime_status}

@router.post("/create-checkout-session")
async def create_checkout_session(
    request_body: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    price_id = request_body.price_id
    mode = request_body.mode
    product_id = request_body.product_id

    if not price_id:
        raise HTTPException(status_code=400, detail="Price ID is required")
    try:
        if mode == 'subscription':
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                customer=current_user.stripe_customer_id,
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    },
                ],
                mode=mode,
                success_url="http://localhost:8080/dashboard.html",
                cancel_url="http://localhost:8080/cancel",
                subscription_data={"metadata": {"product_id": product_id}}
            )
        if mode == 'payment':
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                customer=current_user.stripe_customer_id,
                line_items=[
                    {
                        "price": price_id,
                        "quantity": 1,
                    },
                ],
                mode=mode,
                success_url="http://localhost:8080/dashboard.html",
                cancel_url="http://localhost:8080/cancel",
                payment_intent_data={"metadata": {"product_id": product_id}}
            )
        print("Checkout Session created:", session.metadata)

        return {"sessionId": session["id"]}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        print("Invalid payload:", e)
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        print("Invalid signature:", e)
        raise HTTPException(status_code=400, detail="Invalid signature")

    try:
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            print("Processing checkout.session.completed:", session)

            if session['mode'] == 'payment':
                payment_intent_id = session.get('payment_intent')
                
                if not payment_intent_id:
                    print("Payment intent ID not found in session.")
                    raise HTTPException(status_code=400, detail="Payment intent ID missing in session.")

                try:
                    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                    print(f"Retrieved payment intent: {payment_intent}")
                except stripe.error.StripeError as e:
                    print(f"Error retrieving payment intent {payment_intent_id}: {e}")
                    raise HTTPException(status_code=500, detail=f"Error retrieving payment intent: {str(e)}")

                if 'charges' in payment_intent and payment_intent['charges']['data']:
                    charge_id = payment_intent['charges']['data'][0]['id']
                    customer_id = session['customer']
                    print("Creating invoice for charge:", charge_id)

                    # Create an invoice item for the charge
                    stripe.InvoiceItem.create(
                        customer=customer_id,
                        amount=payment_intent['amount'],
                        currency=payment_intent['currency'],
                        description="One-time product/service",
                        metadata={"charge_id": charge_id}
                    )

                    # Create and finalize the invoice
                    invoice = stripe.Invoice.create(
                        customer=customer_id,
                        auto_advance=True,  # Automatically finalize the invoice
                    )

                    invoice = stripe.Invoice.finalize_invoice(invoice.id)
                    print(f"Invoice created and finalized: {invoice.id} with status {invoice.status}")
                else:
                    print("Charges data not found in payment intent. Deferring to payment_intent.succeeded event.")
                    # Optionally defer handling to another event

        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            print(f"Handling payment_intent.succeeded: {payment_intent}")

            if 'charges' in payment_intent and payment_intent['charges']['data']:
                charge_id = payment_intent['charges']['data'][0]['id']
                customer_id = payment_intent['customer']
                print("Creating invoice for charge:", charge_id)

                # Create an invoice item for the charge
                stripe.InvoiceItem.create(
                    customer=customer_id,
                    amount=payment_intent['amount'],
                    currency=payment_intent['currency'],
                    description="One-time product/service",
                    metadata={"charge_id": charge_id}
                )

                # Create and finalize the invoice
                invoice = stripe.Invoice.create(
                    customer=customer_id,
                    auto_advance=True,  # Automatically finalize the invoice
                )

                invoice = stripe.Invoice.finalize_invoice(invoice.id)
                print(f"Invoice created and finalized: {invoice.id} with status {invoice.status}")

        return {"status": "success"}

    except Exception as e:
        print("Error processing webhook:", e)
        raise HTTPException(status_code=500, detail=str(e))
