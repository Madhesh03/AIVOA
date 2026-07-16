from langchain_groq import ChatGroq

from app.core.config import get_settings


def get_groq_client() -> ChatGroq:
    settings = get_settings()
    return ChatGroq(
        model=settings.groq_model,
        temperature=0.3,
        api_key=settings.groq_api_key,
        max_tokens=2048,
        timeout=30,
    )
