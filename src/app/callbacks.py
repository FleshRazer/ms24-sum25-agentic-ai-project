from langfuse import Langfuse
from langfuse.langchain import CallbackHandler

from app.settings import settings

callbacks = []

if settings.LANGFUSE_SECRET_KEY and settings.LANGFUSE_PUBLIC_KEY:
    langfuse = Langfuse(
        secret_key=settings.LANGFUSE_SECRET_KEY,
        public_key=settings.LANGFUSE_PUBLIC_KEY,
        host="http://localhost:3000",
    )

    if langfuse.auth_check():
        print("Langfuse client is authenticated and ready!")
    else:
        print("Authentication failed. Please check your credentials and host.")

    langfuse_handler = CallbackHandler()
    callbacks.append(langfuse_handler)
