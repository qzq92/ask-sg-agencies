"""LangGraph state definition."""

from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State passed through the LangGraph workflow."""

    messages: Annotated[list, add_messages]
    user_query: str
    conversation_context: str
    routed_categories: list[str]
    category_results: dict[str, str]
    final_response: str
