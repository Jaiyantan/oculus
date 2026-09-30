"""
Pydantic BaseSettings for Oculus Fraud Engine.
Reads from environment variables or .env file.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/fraud_engine"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # AWS
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    SNS_TOPIC_ARN: str = ""
    SES_SENDER_EMAIL: str = ""
    SES_RECIPIENT_EMAIL: str = ""

    # App
    APP_ENV: str = "development"
    SECRET_KEY: str = "oculus-dev-secret-key-change-in-production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
