import os
from pydantic import BaseModel, Field
try:  # Pydantic v2 optional dependency
    from pydantic_settings import BaseSettings, SettingsConfigDict
except ModuleNotFoundError:  # fallback when pydantic-settings isn't installed
    BaseSettings = BaseModel

    def SettingsConfigDict(*args, **kwargs):
        return {}


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    mongodb_uri: str = Field(
        default_factory=lambda: os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    )
    mongodb_db_name: str = Field(
        default_factory=lambda: os.getenv("MONGODB_DB_NAME", "plant_tracker")
    )
    session_secret_key: str = Field(
        default_factory=lambda: os.getenv("SESSION_SECRET_KEY", "a-strong-fallback-secret")
    )
    allowed_origins: list[str] = Field(
        default_factory=lambda: os.getenv("ALLOWED_ORIGINS", "http://localhost:8080").split(",")
    )
    plant_id_api_key: str | None = Field(default_factory=lambda: os.getenv("PLANT_ID_API_KEY"))
    plantnet_api_key: str | None = Field(default_factory=lambda: os.getenv("PLANTNET_API_KEY"))
    perenual_api_key: str | None = Field(default_factory=lambda: os.getenv("PERENUAL_API_KEY"))
    google_client_id: str | None = Field(default_factory=lambda: os.getenv("GOOGLE_CLIENT_ID"))
    google_client_secret: str | None = Field(default_factory=lambda: os.getenv("GOOGLE_CLIENT_SECRET"))
    jwt_secret: str = Field(default_factory=lambda: os.getenv("JWT_SECRET", "secret"))
    frontend_url: str = Field(
        default_factory=lambda: os.getenv("FRONTEND_URL", "http://localhost:8080/")
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

