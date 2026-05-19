"""LangGraph workflow: supervisor -> category agents (parallel) -> synthesizer.

Uses async execution with memory checkpointing for efficiency.
"""

import asyncio
import warnings

from agent.category_agent import run_category_agent
from agent.synthesizer import synthesizer_node
from agent.supervisor import supervisor_node
from config.llm_errors import LLMServiceUnavailable
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from src.state import AgentState

MAX_PARALLEL_AGENTS = 3

# Suppress Streamlit ScriptRunContext warnings from parallel threads
warnings.filterwarnings("ignore", message=".*ScriptRunContext.*")


async def run_category_agents_node_async(state: AgentState) -> dict:
    """Run routed category agents in parallel using asyncio."""
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
        if isinstance(result, LLMServiceUnavailable):
            raise result
        if isinstance(result, Exception):
            results[cat] = f"Error: {result}"
        else:
            results[cat] = result
    
    return {"category_results": results}


async def build_graph_async():
    """Build and compile the async LangGraph workflow with memory checkpointing."""
    # Use MemorySaver for in-memory checkpointing (simpler than SQLite)
    memory = MemorySaver()
    
    workflow = StateGraph(AgentState)

    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("category_agents", run_category_agents_node_async)
    workflow.add_node("synthesizer", synthesizer_node)

    workflow.set_entry_point("supervisor")
    workflow.add_edge("supervisor", "category_agents")
    workflow.add_edge("category_agents", "synthesizer")
    workflow.add_edge("synthesizer", END)

    return workflow.compile(checkpointer=memory)


# Build graph on module import (async-safe lazy initialization)
_graph = None


async def get_graph():
    """Get or build the graph instance (async singleton pattern)."""
    global _graph
    if _graph is None:
        _graph = await build_graph_async()
    return _graph
