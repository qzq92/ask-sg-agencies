"""Supervisor agent: classifies user query and routes to category agents."""

import json
import re

from langchain_core.messages import HumanMessage, SystemMessage

from prompt.registry import CATEGORY_KEYS
from prompt.supervisor import SUPERVISOR_SYSTEM_PROMPT
from config.config import llm
from src.state import AgentState

VALID_CATEGORIES = set(CATEGORY_KEYS)


def supervisor_node(state: AgentState) -> dict:
    """Classify user query and set routed_categories."""
    user_query = state.get("user_query", "")
    if not user_query:
        return {"routed_categories": ["economy"]}

    context = state.get("conversation_context", "")
    if context:
        content = f"Conversation so far:\n{context}\n\nCurrent query: {user_query}"
    else:
        content = f"User problem: {user_query}"

    response = llm.invoke(
        [
            SystemMessage(content=SUPERVISOR_SYSTEM_PROMPT),
            HumanMessage(content=content),
        ]
    )
    content = response.content if hasattr(response, "content") else str(response)
    categories = _parse_categories(content)
    return {"routed_categories": categories}


def _parse_categories(content: str) -> list[str]:
    """Extract category list from LLM response."""
    content = content.strip()
    match = re.search(r"\{[^}]*\"categories\"[^}]*\[[^\]]*\]", content, re.DOTALL)
    if match:
        try:
            obj = json.loads(match.group(0))
            cats = obj.get("categories", [])
            return [c for c in cats if c in VALID_CATEGORIES][:3]
        except json.JSONDecodeError:
            pass
    return ["economy"]
