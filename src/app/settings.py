from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    LANGFUSE_SECRET_KEY: str
    LANGFUSE_PUBLIC_KEY: str

    class Config:
        env_file = ".env"


settings = Settings()
