"""LangGraph workflow: supervisor -> category agents -> synthesizer."""

from agent.category_agent import run_category_agent
from agent.synthesizer import synthesizer_node
from agent.supervisor import supervisor_node
from langgraph.graph import END, StateGraph

from src.state import AgentState


def run_category_agents_node(state: AgentState) -> dict:
    """Run each routed category agent and collect results."""
    user_query = state.get("user_query", "")
    conversation_context = state.get("conversation_context", "")
    routed_categories = state.get("routed_categories", [])
    query = (
        f"{conversation_context}\n\nCurrent: {user_query}"
        if conversation_context
        else user_query
    )
    results = {}
    for cat in routed_categories:
        try:
            results[cat] = run_category_agent(cat, query)
        except Exception as e:
            results[cat] = f"Error: {e}"
    return {"category_results": results}


def build_graph():
    """Build and compile the LangGraph workflow."""
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("category_agents", run_category_agents_node)
    workflow.add_node("synthesizer", synthesizer_node)

    workflow.set_entry_point("supervisor")
    workflow.add_edge("supervisor", "category_agents")
    workflow.add_edge("category_agents", "synthesizer")
    workflow.add_edge("synthesizer", END)

    return workflow.compile()


graph = build_graph()
