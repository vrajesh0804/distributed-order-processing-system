"""
Application configuration.

This file centralizes environment variables so database, Redis, and Kafka
settings are not hardcoded inside route or service files.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Loads project configuration from .env or system environment variables."""

    PROJECT_NAME: str = "Distributed Event-Driven Order Processing System"
    DATABASE_URL: str = "postgresql://postgres:123456@localhost:5432/distributed_order_system"
    REDIS_URL: str = "redis://localhost:6379/0"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    ORDER_CREATED_TOPIC: str = "order_created"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
