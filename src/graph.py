"""LangGraph workflow: supervisor -> category specialists -> optional synthesizer."""

from __future__ import annotations

from typing import Any

from agent.category_agent import run_category_agent
from agent.supervisor import supervisor_node
from agent.synthesizer import synthesizer_node
from config.routing import CATEGORY_LABELS
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from src.state import AgentState, AgentStateUpdate


def run_category_agents_node(state: AgentState) -> AgentStateUpdate:
    """Run one specialist per routed category and collect results."""
    user_query = state.get("user_query", "")
    conversation_context = state.get("conversation_context", "")
    routed_categories = state.get("routed_categories", [])

    if not routed_categories:
        return {}

    query = (
        f"{conversation_context}\n\nCurrent: {user_query}"
        if conversation_context
        else user_query
    )
    multi_category = len(routed_categories) > 1

    category_results: dict[str, str] = {}
    for category in routed_categories:
        category_results[category] = run_category_agent(
            category,
            query,
            multi_category=multi_category,
        )

    if len(routed_categories) == 1:
        return {
            "category_results": category_results,
            "final_response": category_results[routed_categories[0]],
        }

    return {"category_results": category_results}


def route_after_supervisor(state: AgentState) -> str:
    """Run specialists when categories were routed, otherwise end with clarification."""
    if state.get("routed_categories"):
        return "category_agents"
    return END


def route_after_category_agents(state: AgentState) -> str:
    """Synthesize when multiple categories ran; single-category already has final_response."""
    if len(state.get("routed_categories", [])) > 1:
        return "synthesizer"
    return END


async def build_graph_async() -> Any:
    """Build and compile the LangGraph workflow with memory checkpointing."""
    memory = MemorySaver()

    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("category_agents", run_category_agents_node)
    workflow.add_node("synthesizer", synthesizer_node)

    workflow.set_entry_point("supervisor")
    workflow.add_conditional_edges("supervisor", route_after_supervisor)
    workflow.add_conditional_edges("category_agents", route_after_category_agents)
    workflow.add_edge("synthesizer", END)

    return workflow.compile(checkpointer=memory)


_graph: Any | None = None


async def get_graph() -> Any:
    """Get or build the graph instance (async singleton pattern)."""
    global _graph
    if _graph is None:
        _graph = await build_graph_async()
    return _graph


def format_category_list(categories: list[str]) -> str:
    """Human-readable category names for UI status messages."""
    return ", ".join(CATEGORY_LABELS.get(cat, cat) for cat in categories)
