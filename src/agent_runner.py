"""Shared logic for running category agents with tools."""

import json
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

from config.config import llm
from tools.dataset import get_dataset_metadata

TOOLS = [get_dataset_metadata]
TOOLS_BY_NAME = {t.name: t for t in TOOLS}


def run_category_agent_with_tools(system_prompt: str, user_query: str) -> str:
    """Run a category agent (LLM + tools) until it returns a final response."""
    model = llm.bind_tools(TOOLS)
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_query),
    ]
    max_iterations = 10
    for _ in range(max_iterations):
        response = model.invoke(messages)
        messages.append(response)
        if not getattr(response, "tool_calls", None) or not response.tool_calls:
            return response.content
        for tc in response.tool_calls:
            tool = TOOLS_BY_NAME.get(tc["name"])
            if tool:
                result = tool.invoke(tc.get("args", {}))
                content = result if isinstance(result, str) else json.dumps(result)
            else:
                content = "Tool not found"
            messages.append(
                ToolMessage(content=content, tool_call_id=tc.get("id", ""))
            )
    return "Maximum iterations reached."
