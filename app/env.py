from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Use this to build paths inside the project
BASE_DIR = Path(__file__).resolve().parent


class EnvSettings(BaseSettings):
    """Class to hold application's config values."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR.parent / ".env", extra="ignore", env_ignore_empty=True
    )
    ALLOWED_ORIGINS: list[str] = []

    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRY: int = 5  # in minutes
    REFRESH_TOKEN_EXPIRY: int = 2  # in days

    DB_HOST: str = ""
    DB_PORT: int = 5432
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_NAME: str = ""

    REDIS_URL: str = ""

    B2_APP_KEY_ID: str = ""
    B2_APP_KEY: str = ""
    B2_BUCKET_NAME: str = ""

    RESEND_API_KEY: str = ""
    RESEND_EMAIL: str = ""

    GOOGLE_CLIENT_ID: str = ""

    FRONTEND_URL: str = ""


settings = EnvSettings()
