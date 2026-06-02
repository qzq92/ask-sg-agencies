"""Synthesizer agent: aggregates category results into final response."""

from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from config.config import llm
from config.llm_errors import invoke_llm
from prompt.synthesizer import SYNTHESIZER_SYSTEM_PROMPT
from src.state import AgentState, AgentStateUpdate


def synthesizer_node(state: AgentState) -> AgentStateUpdate:
    """Combine category results into a unified recommendation."""
    user_query = state.get("user_query", "")
    conversation_context = state.get("conversation_context", "")
    category_results = state.get("category_results", {})
    if not category_results:
        return {"final_response": "No datasets were found for your query."}

    parts: list[str] = []
    if conversation_context:
        parts.append(f"Conversation so far:\n{conversation_context}\n")
    parts.append(f"User problem: {user_query}\n\nCategory recommendations:\n")
    for category, recommendation in category_results.items():
        parts.append(f"--- {category} ---\n{recommendation}\n")
    combined = "\n".join(parts)

    response = invoke_llm(
        llm,
        [
            SystemMessage(content=SYNTHESIZER_SYSTEM_PROMPT),
            HumanMessage(content=combined),
        ],
    )
    content = response.content if isinstance(response.content, str) else str(response.content)
    return {"final_response": content}
