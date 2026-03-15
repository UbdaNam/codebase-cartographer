import pytest

from src.llm.budget import BudgetExceededError, ContextWindowBudget


def test_context_window_budget_tracks_requests() -> None:
    budget = ContextWindowBudget(max_prompt_tokens=100, max_completion_tokens=100, max_requests=2)

    budget.reserve("short prompt", 10)

    assert budget.snapshot.request_count == 1
    assert budget.snapshot.estimated_prompt_tokens > 0


def test_context_window_budget_raises_when_exhausted() -> None:
    budget = ContextWindowBudget(max_prompt_tokens=1, max_completion_tokens=1, max_requests=1)

    with pytest.raises(BudgetExceededError):
        budget.reserve("this prompt is too large", 10)

    assert budget.snapshot.exhausted is True
