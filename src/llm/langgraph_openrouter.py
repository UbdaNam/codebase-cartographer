"""LangChain chat-model adapter for OpenRouter-backed LangGraph flows."""

from __future__ import annotations

from typing import Any

from src.config import AppSettings


def build_langgraph_chat_model(settings: AppSettings, *, model_name: str | None = None):
    """Build a ChatOpenAI-compatible model over OpenRouter when configured."""

    if not settings.semantic_provider_enabled or not settings.openrouter_api_key:
        return None
    try:
        from langchain_openai import ChatOpenAI
    except ModuleNotFoundError:
        return None
    headers: dict[str, Any] = {"X-Title": settings.openrouter_app_name}
    if settings.openrouter_referer:
        headers["HTTP-Referer"] = settings.openrouter_referer
    return ChatOpenAI(
        model=model_name or settings.navigator_agent_model,
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
        temperature=0,
        timeout=30,
        default_headers=headers,
    )
