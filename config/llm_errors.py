"""OpenAI / LLM error detection and user-facing fallback responses."""

import os
from typing import Any

DATA_GOV_SG_URL = "https://data.gov.sg/"

FALLBACK_RESPONSE = f"""I'm temporarily unable to process your request. This can happen when the AI service is unavailable, your API key is missing or invalid, or OpenAI is experiencing an outage.

You can still browse and search datasets directly on Singapore's open data portal:

**[{DATA_GOV_SG_URL}]({DATA_GOV_SG_URL})**

There you'll find 4,500+ datasets from 70+ government agencies across housing, transport, health, education, and more."""


class LLMServiceUnavailable(Exception):
    """Raised when OpenAI cannot be reached or the API key is invalid."""


def is_api_key_configured() -> bool:
    """Return True if OPENAI_API_KEY is set and non-empty."""
    key = os.getenv("OPENAI_API_KEY", "").strip()
    return bool(key)


def is_llm_service_error(exc: BaseException) -> bool:
    """Return True if the exception indicates OpenAI is down or misconfigured."""
    if isinstance(exc, LLMServiceUnavailable):
        return True

    try:
        from openai import (
            APIConnectionError,
            APIStatusError,
            APITimeoutError,
            AuthenticationError,
            InternalServerError,
            RateLimitError,
        )

        if isinstance(
            exc,
            (
                AuthenticationError,
                APIConnectionError,
                APITimeoutError,
                InternalServerError,
                RateLimitError,
            ),
        ):
            return True
        if isinstance(exc, APIStatusError) and getattr(exc, "status_code", 0) >= 500:
            return True
    except ImportError:
        pass

    message = str(exc).lower()
    error_markers = (
        "api key",
        "authentication",
        "incorrect api key",
        "invalid api key",
        "unauthorized",
        "connection error",
        "connect error",
        "timeout",
        "timed out",
        "service unavailable",
        "internal server error",
        "bad gateway",
        "502",
        "503",
        "504",
        "openai",
    )
    if any(marker in message for marker in error_markers):
        return True

    if exc.__cause__ is not None:
        return is_llm_service_error(exc.__cause__)

    return False


def get_fallback_response() -> str:
    """User-facing message when the LLM service is unavailable."""
    return FALLBACK_RESPONSE


def invoke_llm(llm: Any, messages: list) -> Any:
    """Invoke the LLM, raising LLMServiceUnavailable on auth/outage errors."""
    if not is_api_key_configured():
        raise LLMServiceUnavailable("OPENAI_API_KEY is not configured")

    try:
        return llm.invoke(messages)
    except LLMServiceUnavailable:
        raise
    except Exception as exc:
        if is_llm_service_error(exc):
            raise LLMServiceUnavailable(str(exc)) from exc
        raise
