from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, Dict

class UserCreate(SQLModel):
    email: str
    full_name: str
    password: str 

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    full_name: str
    hashed_password: str
    is_active: bool = True
    is_admin: bool = False
    stripe_customer_id: Optional[str] = None
    valid_subscription: bool = False 

class UserResponse(SQLModel):
    id: int
    email: str
    full_name: str
    is_active: bool
    stripe_customer_id: Optional[str] = None
    valid_subscription: bool = False


class Recurring(SQLModel):
    aggregate_usage: Optional[str] = None
    interval: str
    interval_count: int
    trial_period_days: Optional[int] = None
    usage_type: str

class PriceResponse(SQLModel):
    id: str  
    object: str  
    active: bool  
    billing_scheme: str
    created: int
    currency: str
    custom_unit_amount: Optional[Dict[str, Optional[int]]] = None
    livemode: bool
    lookup_key: Optional[str] = None
    metadata: Dict[str, str] = {}
    nickname: Optional[str] = None
    product: str
    recurring: Optional[Recurring] = None
    tax_behavior: str
    tiers_mode: Optional[str] = None
    transform_quantity: Optional[Dict[str, Optional[int]]] = None
    type: str
    unit_amount: Optional[int] = None
    unit_amount_decimal: Optional[str] = None

class ProductResponse(SQLModel):
    id: str
    object: str
    active: bool
    created: int
    default_price: Optional[str] = None
    description: Optional[str] = None 
    images: List[str] = []
    marketing_features: List[str] = []
    livemode: bool
    metadata: Dict[str, str] = {}
    name: str
    package_dimensions: Optional[Dict[str, float]] = None
    shippable: Optional[bool] = None
    statement_descriptor: Optional[str] = None
    tax_code: Optional[str] = None
    unit_label: Optional[str] = None
    updated: int
    url: Optional[str] = None
    price_info: Optional[PriceResponse] = None
