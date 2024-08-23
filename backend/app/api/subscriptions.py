from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select
from app.core.dependencies import get_db_session
from app.core.auth import get_current_user
from app.core.stripe_client import check_if_active_subscription
from app.models.models import User
import stripe
from pydantic import BaseModel
from app.core.config import settings

class CheckoutSessionRequest(BaseModel):
    price_id: str
    mode: str

router = APIRouter(
    prefix="/subscriptions",  
    tags=["subscriptions"],  
)

endpoint_secret = settings.ENDPOINT_SECRET

@router.get("/status")
def get_subscription_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db_session)):    
    return {"subscription_status": check_if_active_subscription(current_user.stripe_customer_id)}

@router.post("/create-checkout-session")
async def create_checkout_session(
    request_body: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session)
):
    price_id = request_body.price_id
    mode = request_body.mode

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
                subscription_data={"metadata": {"product_id": settings.SUBSCRIPTION_PRODUCT_ID}}
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
                payment_intent_data={"metadata": {"product_id": settings.LIFETIME_PRODUCT_ID}}
            )
        current_user.valid_subscription = True
        db.add(current_user)
        db.commit()
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
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    try:
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']

            if session['mode'] == 'payment':
                payment_intent_id = session.get('payment_intent')
                
                if not payment_intent_id:
                    raise HTTPException(status_code=400, detail="Payment intent ID missing in session.")

                try:
                    payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                except stripe.error.StripeError as e:
                    raise HTTPException(status_code=500, detail=f"Error retrieving payment intent: {str(e)}")

                if 'charges' in payment_intent and payment_intent['charges']['data']:
                    charge_id = payment_intent['charges']['data'][0]['id']
                    customer_id = session['customer']

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


        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']

            if 'charges' in payment_intent and payment_intent['charges']['data']:
                charge_id = payment_intent['charges']['data'][0]['id']
                customer_id = payment_intent['customer']

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

        return {"status": "success"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
