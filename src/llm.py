"""LLM factory: returns a Claude model with structured output binding.

Pulls the API key from ANTHROPIC_API_KEY env var. No fallback — fail loud
so misconfiguration is caught before the graph starts.
"""

from __future__ import annotations

import os
from typing import TypeVar

from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

_DEFAULT_MODEL = "claude-opus-4-7"  # Opus for design + validation reasoning
_CHEAP_MODEL = "claude-haiku-4-5-20251001"  # Haiku for parsing / routine


def _require_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Copy .env.example to .env and fill in your key."
        )
    return key


def get_llm(model: str = _DEFAULT_MODEL, temperature: float = 0.2) -> ChatAnthropic:
    _require_key()
    return ChatAnthropic(model=model, temperature=temperature, max_tokens=4096)


def get_structured_llm(schema: type[T], *, cheap: bool = False) -> ChatAnthropic:
    """Return a Claude instance bound to a Pydantic schema for structured output."""
    model = _CHEAP_MODEL if cheap else _DEFAULT_MODEL
    return get_llm(model=model).with_structured_output(schema)
