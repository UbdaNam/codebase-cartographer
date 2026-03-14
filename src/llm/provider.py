"""Provider abstraction for Semanticist model-backed operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol


class ProviderError(RuntimeError):
    """Raised when a provider request fails."""


@dataclass(slots=True, frozen=True)
class ChatRequest:
    prompt: str
    model: str
    max_output_tokens: int
    temperature: float = 0.0


@dataclass(slots=True, frozen=True)
class ChatResult:
    text: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    model: str = ""
    raw_metadata: dict[str, object] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class EmbeddingRequest:
    texts: list[str]
    model: str


@dataclass(slots=True, frozen=True)
class EmbeddingResult:
    vectors: list[list[float]]
    prompt_tokens: int = 0
    model: str = ""
    raw_metadata: dict[str, object] = field(default_factory=dict)


class LLMProvider(Protocol):
    """Minimal interface used by Semanticist for chat and embeddings."""

    def is_available(self) -> bool:
        ...

    def generate_text(self, request: ChatRequest) -> ChatResult:
        ...

    def embed_texts(self, request: EmbeddingRequest) -> EmbeddingResult:
        ...


class NullProvider:
    """Deterministic fallback provider when remote access is unavailable."""

    def is_available(self) -> bool:
        return False

    def generate_text(self, request: ChatRequest) -> ChatResult:
        raise ProviderError(f"provider unavailable for model {request.model}")

    def embed_texts(self, request: EmbeddingRequest) -> EmbeddingResult:
        raise ProviderError(f"embedding provider unavailable for model {request.model}")
