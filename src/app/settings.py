from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    LANGFUSE_SECRET_KEY: str | None
    LANGFUSE_PUBLIC_KEY: str | None
    ENABLE_REVIEWER: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
