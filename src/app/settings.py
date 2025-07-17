from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    GOOGLE_API_KEY: str
    MISTRAL_API_KEY: str
    LANGFUSE_SECRET_KEY: str
    LANGFUSE_PUBLIC_KEY: str
    LLM_PROVIDER: str = 'google'
    GOOGLE_MODEL: str = 'gemini-2.5-flash'
    MISTRAL_MODEL: str = 'mistral-large-latest'

    class Config:
        env_file = ".env"


settings = Settings()
