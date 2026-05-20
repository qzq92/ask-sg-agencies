"""LangGraph workflow: supervisor -> single category agent.

Simplified flow that routes to one category agent and returns directly.
"""

from agent.category_agent import run_category_agent
from agent.supervisor import supervisor_node
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from src.state import AgentState


def run_category_agent_node(state: AgentState) -> dict:
    """Run the routed category agent and return its response."""
    user_query = state.get("user_query", "")
    conversation_context = state.get("conversation_context", "")
    routed_category = state.get("routed_category", "")
    
    if not routed_category:
        return {}
    
    query = (
        f"{conversation_context}\n\nCurrent: {user_query}"
        if conversation_context
        else user_query
    )
    
    result = run_category_agent(routed_category, query)
    return {"final_response": result}


def should_run_category_agent(state: AgentState) -> str:
    """Determine whether to run category agent or end (for clarification)."""
    if state.get("routed_category"):
        return "category_agent"
    return END


async def build_graph_async():
    """Build and compile the LangGraph workflow with memory checkpointing."""
    memory = MemorySaver()
    
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("category_agent", run_category_agent_node)

    workflow.set_entry_point("supervisor")
    workflow.add_conditional_edges("supervisor", should_run_category_agent)
    workflow.add_edge("category_agent", END)

    return workflow.compile(checkpointer=memory)


# Build graph on module import (async-safe lazy initialization)
_graph = None


async def get_graph():
    """Get or build the graph instance (async singleton pattern)."""
    global _graph
    if _graph is None:
        _graph = await build_graph_async()
    return _graph
