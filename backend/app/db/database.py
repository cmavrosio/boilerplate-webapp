from sqlmodel import SQLModel, Session, create_engine, select
from app.core.security import get_password_hash
from app.models.models import User
from app.core.config import settings

# Database engine
engine = create_engine(settings.DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    # Create the database and tables if they don't exist
    SQLModel.metadata.create_all(engine)

    # Create the initial admin user if it doesn't exist
    with Session(engine) as session:
        # Check if an admin user already exists
        statement = select(User).where(User.is_admin == True)
        admin_user = session.exec(statement).first()
        
        if not admin_user:
            # Create an admin user
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
            print("Admin user created with email 'admin@example.com' and password 'admin'")
        else:
            print("Admin user already exists")
