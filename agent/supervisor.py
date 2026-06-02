"""Supervisor agent: classifies user query and routes to category agents."""

from __future__ import annotations

import json
import re

from langchain_core.messages import HumanMessage, SystemMessage

from config.agency_mapping import get_categories_for_agencies
from config.config import llm
from config.llm_errors import invoke_llm
from config.routing import MAX_ROUTED_CATEGORIES
from prompt.registry import CATEGORY_KEYS
from prompt.supervisor import SUPERVISOR_SYSTEM_PROMPT
from src.state import AgentState, AgentStateUpdate

VALID_CATEGORIES = set(CATEGORY_KEYS)


def supervisor_node(state: AgentState) -> AgentStateUpdate:
    """Classify user query and set routed_categories."""
    user_query = state.get("user_query", "")
    if not user_query:
        return {
            "routed_categories": [],
            "routed_category": "",
            "final_response": (
                "I'd be happy to help you find datasets from Singapore's Open Data Portal. "
                "Could you please tell me what kind of data you're looking for?"
            ),
        }

    context = state.get("conversation_context", "")
    if context:
        content = f"Conversation so far:\n{context}\n\nCurrent query: {user_query}"
    else:
        content = f"User problem: {user_query}"

    response = invoke_llm(
        llm,
        [
            SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT),
            HumanMessage(content=content),
        ],
    )
    response_content = (
        response.content if isinstance(response.content, str) else str(response.content)
    )
    llm_categories, clarification = _parse_categories(response_content)
    agency_categories = get_categories_for_agencies(user_query)
    categories = _merge_categories(llm_categories, agency_categories)

    if not categories:
        return {
            "routed_categories": [],
            "routed_category": "",
            "final_response": clarification
            or (
                "I'm not sure what kind of data you're looking for. Could you please "
                "describe your data needs or the problem you're trying to solve?"
            ),
        }

    return {
        "routed_categories": categories,
        "routed_category": categories[0],
    }


def _parse_categories(content: str) -> tuple[list[str], str]:
    """Extract category list and optional clarification from LLM response."""
    content = content.strip()
    try:
        match = re.search(r"\{.*\}", content, re.DOTALL)
        if not match:
            return [], ""
        obj = json.loads(match.group(0))
        clarification = obj.get("clarification", "")

        raw: list[str] = []
        if isinstance(obj.get("categories"), list):
            raw = [str(item) for item in obj["categories"]]
        elif obj.get("category"):
            raw = [str(obj["category"])]

        valid = [cat for cat in raw if cat in VALID_CATEGORIES]
        return valid[:MAX_ROUTED_CATEGORIES], clarification
    except (json.JSONDecodeError, TypeError, ValueError):
        return [], ""


def _merge_categories(llm_categories: list[str], agency_categories: list[str]) -> list[str]:
    """Merge LLM and agency-detected categories, preserving order and deduplicating."""
    merged: list[str] = []
    seen: set[str] = set()
    for category in [*llm_categories, *agency_categories]:
        if category in VALID_CATEGORIES and category not in seen:
            merged.append(category)
            seen.add(category)
        if len(merged) >= MAX_ROUTED_CATEGORIES:
            break
    return merged
