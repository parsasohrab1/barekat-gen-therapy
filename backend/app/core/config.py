from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    PROJECT_NAME: str = "Barekat Gen Therapy"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    API_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480
    AUTH_ENABLED: bool = True

    DATABASE_URL: str = "postgresql+psycopg://barekat:barekat@localhost:5432/barekat_gen_therapy"
    REDIS_URL: str = "redis://localhost:6379/0"

    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "barekat"
    MINIO_SECRET_KEY: str = "barekat_minio"
    MINIO_BUCKET: str = "barekat-artifacts"
    MINIO_SECURE: bool = False

    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    MLFLOW_ENABLED: bool = True

    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "lipid_molecules"
    QDRANT_ENABLED: bool = True

    MQTT_BROKER_HOST: str = "localhost"
    MQTT_BROKER_PORT: int = 1883
    MQTT_TOPIC_SYNTHESIS: str = "barekat/lab/synthesis/commands"
    MQTT_ENABLED: bool = True

    LIMS_BASE_URL: str = "http://localhost:8000/api/v1/lab/lims/mock"
    LIMS_ENABLED: bool = True

    SENTRY_DSN: str = ""
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
