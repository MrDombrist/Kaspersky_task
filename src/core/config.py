from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_TITLE: str = "Kaspersky Task API"
    DEBUG: bool = False

    # Processing
    MAX_WORKERS: int = Field(
        default=4, description="Thread pool workers for CPU-bound tasks"
    )
    TEMP_DIR: str = Field(
        default="/tmp/reports", description="Temp dir for uploaded/result files"
    )
    LRU_CACHE_SIZE: int = Field(
        default=100_000, description="LRU cache size for morphological forms"
    )

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379")
    REDIS_JOB_TTL: int = Field(default=3600, description="Job state TTL in seconds")

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = Field(default="localhost:9092")
    KAFKA_TOPIC_REPORTS: str = Field(default="report-jobs")
    KAFKA_GROUP_ID: str = Field(default="report-workers")

    # Feature flags
    USE_KAFKA: bool = Field(default=False, description="Route large jobs through Kafka")
    USE_REDIS_CACHE: bool = Field(default=False, description="Cache job state in Redis")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
