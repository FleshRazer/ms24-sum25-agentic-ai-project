from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    LLM_PROVIDER: Literal["google", "mistral"] = "google"

    GOOGLE_API_KEY: str | None = None
    GOOGLE_MODEL: str = "gemini-2.5-flash"

    MISTRAL_API_KEY: str | None = None
    MISTRAL_MODEL: str = "mistral-large-latest"

    LANGFUSE_SECRET_KEY: str | None = None
    LANGFUSE_PUBLIC_KEY: str | None = None

    ENABLE_REVIEWER: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
