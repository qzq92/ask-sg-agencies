"""Supervisor agent: classifies user query and routes to a category agent."""

import json
import re

from langchain_core.messages import HumanMessage, SystemMessage

from prompt.registry import CATEGORY_KEYS
from prompt.supervisor import SUPERVISOR_SYSTEM_PROMPT
from config.config import llm
from config.agency_mapping import get_categories_for_agencies
from config.llm_errors import invoke_llm
from src.state import AgentState

VALID_CATEGORIES = set(CATEGORY_KEYS)


def supervisor_node(state: AgentState) -> dict:
    """Classify user query and set routed_category."""
    user_query = state.get("user_query", "")
    if not user_query:
        return {
            "routed_category": "",
            "final_response": "I'd be happy to help you find datasets from Singapore's Open Data Portal. Could you please tell me what kind of data you're looking for?",
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
    response_content = response.content if hasattr(response, "content") else str(response)
    category, clarification = _parse_category(response_content)
    
    agency_category = get_categories_for_agencies(user_query)
    if agency_category:
        category = agency_category[0]
    
    if not category:
        return {
            "routed_category": "",
            "final_response": clarification or "I'm not sure what kind of data you're looking for. Could you please describe your data needs or the problem you're trying to solve?",
        }
    
    return {"routed_category": category}


def _parse_category(content: str) -> tuple[str, str]:
    """Extract category and optional clarification from LLM response.
    
    Returns (category, clarification). Category is empty string if invalid/unclear.
    """
    content = content.strip()
    try:
        match = re.search(r"\{[^}]*\}", content, re.DOTALL)
        if match:
            obj = json.loads(match.group(0))
            cat = obj.get("category", "")
            clarification = obj.get("clarification", "")
            if cat and cat in VALID_CATEGORIES:
                return cat, ""
            return "", clarification
    except json.JSONDecodeError:
        pass
    return "", ""
