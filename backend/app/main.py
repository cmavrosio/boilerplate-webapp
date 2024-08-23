from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Import CORSMiddleware
from app.api import users, products, auth, subscriptions
from app.db.database import init_db

app = FastAPI()

origins = [
    "http://localhost:8080",  
    "http://127.0.0.1:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(auth.router, tags=["auth"])
app.include_router(users.router, tags=["users"])
app.include_router(products.router, tags=["products"])
app.include_router(subscriptions.router, tags=["subscriptions"])
