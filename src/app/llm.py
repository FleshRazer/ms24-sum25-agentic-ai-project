from langchain_google_genai import ChatGoogleGenerativeAI

from app.settings import settings

if settings.LLM_PROVIDER not in ["google", "mistral"]:
    raise ValueError(f"Invalid LLM_PROVIDER: {settings.LLM_PROVIDER}")

if settings.LLM_PROVIDER == "google":
    if not settings.GOOGLE_API_KEY:
        raise ValueError(
            "GOOGLE_API_KEY is required for Google provider. Please set it in the environment."
        )
    from langchain_google_genai import ChatGoogleGenerativeAI

    llm = ChatGoogleGenerativeAI(
        model=settings.GOOGLE_MODEL, google_api_key=settings.GOOGLE_API_KEY
    )
    model = settings.GOOGLE_MODEL
elif settings.LLM_PROVIDER == "mistral":
    if not settings.MISTRAL_API_KEY:
        raise ValueError(
            "MISTRAL_API_KEY is required for Mistral provider. Please set it in the environment."
        )
    from langchain_mistralai import ChatMistralAI

    llm = ChatMistralAI(model=settings.MISTRAL_MODEL, api_key=settings.MISTRAL_API_KEY)
    model = settings.MISTRAL_MODEL
