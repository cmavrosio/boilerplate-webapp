from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict

# User Models

class UserCreate(SQLModel):
    email: str
    full_name: str
    password: str  # Plain text password for registration


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    full_name: str
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False  # New field to indicate admin status
    stripe_customer_id: Optional[str] = None

    subscriptions: List["Subscription"] = Relationship(back_populates="user")


class UserResponse(SQLModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    stripe_customer_id: Optional[str] = None

# Product Models

class ProductCreate(SQLModel):
    name: str


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    stripe_product_id: str

    subscriptions: List["Subscription"] = Relationship(back_populates="product")



class Recurring(SQLModel):
    aggregate_usage: Optional[str] = None  # Usage type: null, sum, last_during_period, or last_ever
    interval: str  # Billing interval, e.g., "month"
    interval_count: int  # Number of intervals between billings
    trial_period_days: Optional[int] = None  # Number of trial period days, if any
    usage_type: str  # The usage type: metered or licensed

class PriceResponse(SQLModel):
    id: str  # Stripe price ID
    object: str  # Should always be "price"
    active: bool  # Indicates if the price is active
    billing_scheme: str  # Pricing scheme: per_unit or tiered
    created: int  # Timestamp of price creation
    currency: str  # Currency code (e.g., "usd")
    custom_unit_amount: Optional[Dict[str, Optional[int]]] = None  # Custom unit amount object
    livemode: bool  # Indicates if the price is in live mode
    lookup_key: Optional[str] = None  # Lookup key for the price
    metadata: Dict[str, str] = {}  # Metadata from Stripe (key-value pairs)
    nickname: Optional[str] = None  # Nickname of the price
    product: str  # The product ID this price is associated with
    recurring: Optional[Recurring] = None  # Recurrence details
    tax_behavior: str  # Tax behavior (e.g., "inclusive", "exclusive", "unspecified")
    tiers_mode: Optional[str] = None  # Pricing tiers mode, if any
    transform_quantity: Optional[Dict[str, Optional[int]]] = None  # Transform quantity object
    type: str  # Type of price: one_time or recurring
    unit_amount: Optional[int] = None  # Unit amount in the smallest currency unit (e.g., cents)
    unit_amount_decimal: Optional[str] = None  # Unit amount as a decimal string

class ProductResponse(SQLModel):
    id: str  # Stripe product ID (string format)
    object: str  # Should always be "product"
    active: bool  # Indicates if the product is active on Stripe
    created: int  # Timestamp of product creation
    default_price: Optional[str] = None  # The default price ID, if any
    description: Optional[str] = None  # Description of the product
    images: List[str] = []  # List of image URLs
    marketing_features: List[str] = []  # Marketing features of the product
    livemode: bool  # Indicates if the product is in live mode
    metadata: Dict[str, str] = {}  # Metadata from Stripe (key-value pairs)
    name: str  # Name of the product
    package_dimensions: Optional[Dict[str, float]] = None  # Dimensions of the product package, if any
    shippable: Optional[bool] = None  # Indicates if the product is shippable
    statement_descriptor: Optional[str] = None  # Extra statement descriptor for the product
    tax_code: Optional[str] = None  # Tax code associated with the product
    unit_label: Optional[str] = None  # Label to display on the pricing unit
    updated: int  # Timestamp of the last product update
    url: Optional[str] = None  # URL of the product, if any
    price_info: Optional[PriceResponse] = None


class SubscriptionCreate(SQLModel):
    product_id: int


class Subscription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    stripe_subscription_id: str

    user: Optional[User] = Relationship(back_populates="subscriptions")
    product: Optional[Product] = Relationship(back_populates="subscriptions")


class SubscriptionResponse(SQLModel):
    id: int
    user_id: int
    product_id: int
    stripe_subscription_id: str
