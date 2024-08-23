from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:////app/data/database.db"
    STRIPE_API_KEY: str = os.getenv("STRIPE_API_KEY")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ENDPOINT_SECRET: str = os.getenv("ENDPOINT_SECRET")

    class Config:
        env_file = ".env"

settings = Settings()
