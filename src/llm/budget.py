"""Context-window and request-budget helpers for Semanticist."""

from __future__ import annotations

from dataclasses import dataclass, field


class BudgetExceededError(RuntimeError):
    """Raised when semantic provider budgets are exceeded."""


@dataclass(slots=True)
class BudgetSnapshot:
    request_count: int = 0
    estimated_prompt_tokens: int = 0
    estimated_completion_tokens: int = 0
    exhausted: bool = False
    warnings: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ContextWindowBudget:
    max_prompt_tokens: int
    max_completion_tokens: int
    max_requests: int
    snapshot: BudgetSnapshot = field(default_factory=BudgetSnapshot)

    @staticmethod
    def estimate_tokens(text: str) -> int:
        normalized = " ".join(text.split())
        return max(1, len(normalized) // 4) if normalized else 0

    def reserve(self, prompt: str, completion_tokens: int) -> tuple[int, int]:
        prompt_tokens = self.estimate_tokens(prompt)
        projected_requests = self.snapshot.request_count + 1
        projected_prompt = self.snapshot.estimated_prompt_tokens + prompt_tokens
        projected_completion = self.snapshot.estimated_completion_tokens + completion_tokens
        if (
            projected_requests > self.max_requests
            or projected_prompt > self.max_prompt_tokens
            or projected_completion > self.max_completion_tokens
        ):
            self.snapshot.exhausted = True
            self.snapshot.warnings.append("semantic_budget_exhausted")
            raise BudgetExceededError("semantic context window budget exhausted")
        self.snapshot.request_count = projected_requests
        self.snapshot.estimated_prompt_tokens = projected_prompt
        self.snapshot.estimated_completion_tokens = projected_completion
        return prompt_tokens, completion_tokens

    def record_usage(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        *,
        reserved_prompt_tokens: int,
        reserved_completion_tokens: int,
    ) -> None:
        actual_prompt = prompt_tokens or reserved_prompt_tokens
        actual_completion = completion_tokens or reserved_completion_tokens
        self.snapshot.estimated_prompt_tokens = max(
            0,
            self.snapshot.estimated_prompt_tokens - reserved_prompt_tokens + actual_prompt,
        )
        self.snapshot.estimated_completion_tokens = max(
            0,
            self.snapshot.estimated_completion_tokens - reserved_completion_tokens + actual_completion,
        )
