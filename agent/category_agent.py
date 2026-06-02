"""Unified category agent: runs the appropriate category specialist."""

from __future__ import annotations

from config.routing import CATEGORY_LABELS
from prompt.registry import get_prompt
from src.agent_runner import run_category_agent_with_tools


def run_category_agent(
    category_key: str,
    user_query: str,
    *,
    multi_category: bool = False,
) -> str:
    """Run the category agent for the given key and return recommendations."""
    prompt = get_prompt(category_key)
    query = user_query

    if multi_category:
        label = CATEGORY_LABELS.get(category_key, category_key)
        query = (
            f"This query spans multiple data domains; other specialists handle other topics. "
            f"Focus only on {label} datasets that are relevant to the user.\n\n{user_query}"
        )

    return run_category_agent_with_tools(prompt, query)
