"""LLM factory: returns a Claude model with structured output binding.

Key resolution order (first non-empty wins):
    1. ANTHROPIC_API_KEY
    2. ANTHROPIC_API_KEY_DISCORD  (fallback for shared workspace keys)

Fails loud if neither is present.

Note: Claude Opus 4.7 deprecated the `temperature` parameter, so we omit it
by default and only pass it for the cheap (Haiku) model where it's still valid.
"""

from __future__ import annotations

import os
from typing import TypeVar

from langchain_anthropic import ChatAnthropic
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

# Sonnet handles structured-output design just fine at ~1/5 of Opus cost.
_DEFAULT_MODEL = "claude-sonnet-4-6"
_OPUS_MODEL = "claude-opus-4-7"  # available via get_llm(_OPUS_MODEL)
_CHEAP_MODEL = "claude-haiku-4-5-20251001"

_KEY_ENV_CANDIDATES = ("ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY_DISCORD")
_TEMPERATURE_SUPPORTED = {_CHEAP_MODEL}


def _resolve_key() -> str:
    for name in _KEY_ENV_CANDIDATES:
        v = os.environ.get(name, "").strip()
        if v:
            return v
    raise RuntimeError(
        f"No Anthropic API key found. Set one of: {', '.join(_KEY_ENV_CANDIDATES)}"
    )


def get_llm(model: str = _DEFAULT_MODEL, temperature: float = 0.2) -> ChatAnthropic:
    kwargs: dict = {
        "model": model,
        "max_tokens": 4096,
        "api_key": _resolve_key(),
    }
    if model in _TEMPERATURE_SUPPORTED:
        kwargs["temperature"] = temperature
    return ChatAnthropic(**kwargs)


def get_structured_llm(schema: type[T], *, cheap: bool = False) -> ChatAnthropic:
    """Return a Claude instance bound to a Pydantic schema for structured output."""
    model = _CHEAP_MODEL if cheap else _DEFAULT_MODEL
    return get_llm(model=model).with_structured_output(schema)
