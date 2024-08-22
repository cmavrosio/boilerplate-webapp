from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.models.models import ProductCreate, Product, ProductResponse, User
from app.core.dependencies import get_db_session
from app.core.auth import get_current_user
from app.core.stripe_client import create_stripe_product
from app.core.auth import admin_required  # Import the admin check dependency

router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@router.post("/", response_model=ProductResponse)
def create_product(product_create: ProductCreate, session: Session = Depends(get_db_session), current_user: User = Depends(admin_required)):
    stripe_product_id = create_stripe_product(product_create.name)
    product = Product(
        name=product_create.name,
        stripe_product_id=stripe_product_id
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return ProductResponse.from_orm(product)

@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, updated_product: ProductCreate, session: Session = Depends(get_db_session), current_user: User = Depends(admin_required)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.name = updated_product.name
    session.add(product)
    session.commit()
    session.refresh(product)
    return ProductResponse.from_orm(product)

@router.delete("/{product_id}", response_model=dict)
def delete_product(product_id: int, session: Session = Depends(get_db_session), current_user: User = Depends(admin_required)):
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    session.delete(product)
    session.commit()
    return {"detail": "Product deleted successfully"}
