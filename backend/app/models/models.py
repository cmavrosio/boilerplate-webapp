from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

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

    subscriptions: List["Subscription"] = Relationship(back_populates="user")



class UserResponse(SQLModel):
    id: int
    email: str
    full_name: str
    is_active: bool

# Product Models

class ProductCreate(SQLModel):
    name: str


class Product(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    stripe_product_id: str

    subscriptions: List["Subscription"] = Relationship(back_populates="product")


class ProductResponse(SQLModel):
    id: int
    name: str
    stripe_product_id: str

# Subscription Models

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
