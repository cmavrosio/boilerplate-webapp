from sqlmodel import SQLModel, Session, create_engine, select
from app.core.security import get_password_hash
from app.models.models import User
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        statement = select(User).where(User.is_admin == True)
        admin_user = session.exec(statement).first()
        
        if not admin_user:
            admin = User(
                email="admin@example.com",
                full_name="Admin User",
                hashed_password=get_password_hash("admin"),
                is_active=True,
                is_admin=True
            )
            session.add(admin)
            session.commit()
            session.refresh(admin)
