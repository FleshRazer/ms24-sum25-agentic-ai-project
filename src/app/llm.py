from langchain_google_genai import ChatGoogleGenerativeAI

from app.settings import settings

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", google_api_key=settings.GOOGLE_API_KEY
)
