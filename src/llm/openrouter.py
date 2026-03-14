"""OpenRouter-backed provider implementation."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import TYPE_CHECKING

from src.llm.provider import ChatRequest, ChatResult, EmbeddingRequest, EmbeddingResult, ProviderError

if TYPE_CHECKING:
    import httpx


@dataclass(slots=True)
class OpenRouterProvider:
    api_key: str | None
    base_url: str
    app_name: str = "codebase-cartographer"
    referer: str | None = None
    timeout_seconds: float = 30.0

    def is_available(self) -> bool:
        return bool(self.api_key)

    def generate_text(self, request: ChatRequest) -> ChatResult:
        if not self.api_key:
            raise ProviderError("missing OpenRouter API key")
        payload = {
            "model": request.model,
            "messages": [{"role": "user", "content": request.prompt}],
            "temperature": request.temperature,
            "max_tokens": request.max_output_tokens,
        }
        data = self._post_json("/chat/completions", payload)
        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        usage = data.get("usage") or {}
        return ChatResult(
            text=(message.get("content") or "").strip(),
            prompt_tokens=int(usage.get("prompt_tokens") or 0),
            completion_tokens=int(usage.get("completion_tokens") or 0),
            model=str(data.get("model") or request.model),
            raw_metadata={"id": data.get("id")},
        )

    def embed_texts(self, request: EmbeddingRequest) -> EmbeddingResult:
        if not self.api_key:
            raise ProviderError("missing OpenRouter API key")
        payload = {
            "model": request.model,
            "input": request.texts,
        }
        data = self._post_json("/embeddings", payload)
        items = data.get("data") or []
        usage = data.get("usage") or {}
        vectors = [list(map(float, item.get("embedding") or [])) for item in items]
        return EmbeddingResult(
            vectors=vectors,
            prompt_tokens=int(usage.get("prompt_tokens") or 0),
            model=str(data.get("model") or request.model),
            raw_metadata={"object": data.get("object")},
        )

    def _post_json(self, path: str, payload: dict[str, object]) -> dict[str, object]:
        try:
            import httpx
        except ModuleNotFoundError as exc:
            raise ProviderError("httpx is required for OpenRouter provider support") from exc
        try:
            with httpx.Client(base_url=self.base_url.rstrip("/"), timeout=self.timeout_seconds) as client:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "X-Title": self.app_name,
                }
                if self.referer:
                    headers["HTTP-Referer"] = self.referer
                response = client.post(
                    path,
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as exc:
            body = _compact_error_text(exc.response.text)
            raise ProviderError(f"openrouter_http_{exc.response.status_code}:{body}") from exc
        except httpx.RequestError as exc:
            raise ProviderError(f"openrouter_request_error:{exc}") from exc


def _compact_error_text(value: str, *, limit: int = 240) -> str:
    return re.sub(r"\s+", " ", value).strip()[:limit] or "no_response_body"
