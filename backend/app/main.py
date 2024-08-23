from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
from app.api import users, products, auth, subscriptions
from app.db.database import init_db

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:8080",  # Frontend URL
    "http://127.0.0.1:8080",  # Another common frontend URL
    # Add more origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific origins
    allow_credentials=True,  # Allow cookies to be included in requests
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.on_event("startup")
def on_startup():
    init_db()

# Include routers without additional prefixes
app.include_router(auth.router, tags=["auth"])
app.include_router(users.router, tags=["users"])
app.include_router(products.router, tags=["products"])
app.include_router(subscriptions.router, tags=["subscriptions"])
