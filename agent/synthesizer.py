"""Synthesizer agent: aggregates category results into final response."""

from langchain_core.messages import HumanMessage, SystemMessage

from prompt.synthesizer import SYNTHESIZER_SYSTEM_PROMPT
from config.config import llm
from src.state import AgentState


def synthesizer_node(state: AgentState) -> dict:
    """Combine category results into a unified recommendation."""
    user_query = state.get("user_query", "")
    conversation_context = state.get("conversation_context", "")
    category_results = state.get("category_results", {})
    if not category_results:
        return {"final_response": "No datasets were found for your query."}

    parts = []
    if conversation_context:
        parts.append(f"Conversation so far:\n{conversation_context}\n")
    parts.append(f"User problem: {user_query}\n\nCategory recommendations:\n")
    for cat, rec in category_results.items():
        parts.append(f"--- {cat} ---\n{rec}\n")
    combined = "\n".join(parts)

    response = llm.invoke(
        [
            SystemMessage(content=SYNTHESIZER_SYSTEM_PROMPT),
            HumanMessage(content=combined),
        ]
    )
    content = response.content if hasattr(response, "content") else str(response)
    return {"final_response": content}
