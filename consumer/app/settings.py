from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="APP_", extra="ignore")

    db_dsn: str = "postgresql+psycopg://app:app@localhost:5432/app"
    rmq_url: str = "amqp://app:app@localhost:5672/"

    rmq_exchange: str = "orders"
    rmq_queue: str = "orders.created.q"
    rmq_routing_key_created: str = "order.created"

    prefetch_count: int = 10


settings = Settings()
