"""LangGraph state definition."""

from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """State passed through the LangGraph workflow."""

    messages: Annotated[list[BaseMessage], add_messages]
    user_query: str
    conversation_context: str
    routed_categories: list[str]
    routed_category: str
    category_results: dict[str, str]
    final_response: str


class AgentStateUpdate(TypedDict, total=False):
    """Partial state updates returned by graph nodes."""

    messages: Annotated[list[BaseMessage], add_messages]
    user_query: str
    conversation_context: str
    routed_categories: list[str]
    routed_category: str
    category_results: dict[str, str]
    final_response: str
