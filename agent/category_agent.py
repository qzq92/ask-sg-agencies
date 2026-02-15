"""Unified category agent: runs the appropriate category specialist."""

from prompt.registry import get_prompt
from src.agent_runner import run_category_agent_with_tools


def run_category_agent(category_key: str, user_query: str) -> str:
    """Run the category agent for the given key and return recommendations."""
    prompt = get_prompt(category_key)
    return run_category_agent_with_tools(prompt, user_query)
