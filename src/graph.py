"""LangGraph workflow: supervisor -> category agents (parallel) -> synthesizer."""

import asyncio
from concurrent.futures import ThreadPoolExecutor

from agent.category_agent import run_category_agent
from agent.synthesizer import synthesizer_node
from agent.supervisor import supervisor_node
from langgraph.graph import END, StateGraph

from src.state import AgentState

MAX_PARALLEL_AGENTS = 3


def _run_agent_sync(args: tuple) -> tuple[str, str]:
    """Run a single category agent synchronously. Returns (category, result)."""
    cat, query = args
    try:
        result = run_category_agent(cat, query)
        return (cat, result)
    except Exception as e:
        return (cat, f"Error: {e}")


def run_category_agents_node(state: AgentState) -> dict:
    """Run routed category agents in parallel using ThreadPoolExecutor."""
    user_query = state.get("user_query", "")
    conversation_context = state.get("conversation_context", "")
    routed_categories = state.get("routed_categories", [])
    
    if not routed_categories:
        return {"category_results": {}}
    
    query = (
        f"{conversation_context}\n\nCurrent: {user_query}"
        if conversation_context
        else user_query
    )
    
    tasks = [(cat, query) for cat in routed_categories]
    
    with ThreadPoolExecutor(max_workers=MAX_PARALLEL_AGENTS) as executor:
        results_list = list(executor.map(_run_agent_sync, tasks))
    
    results = dict(results_list)
    return {"category_results": results}


async def run_category_agents_node_async(state: AgentState) -> dict:
    """Async version: run routed category agents in parallel."""
    user_query = state.get("user_query", "")
    conversation_context = state.get("conversation_context", "")
    routed_categories = state.get("routed_categories", [])
    
    if not routed_categories:
        return {"category_results": {}}
    
    query = (
        f"{conversation_context}\n\nCurrent: {user_query}"
        if conversation_context
        else user_query
    )
    
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(None, run_category_agent, cat, query)
        for cat in routed_categories
    ]
    
    results_list = await asyncio.gather(*tasks, return_exceptions=True)
    
    results = {}
    for cat, result in zip(routed_categories, results_list):
        if isinstance(result, Exception):
            results[cat] = f"Error: {result}"
        else:
            results[cat] = result
    
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
