"""Shared logic for running category agents with tools."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage

from config.config import llm
from config.llm_errors import invoke_llm
from tools.collection import search_collections
from tools.dataset import get_dataset_metadata, list_datasets_by_agency, search_datasets

TOOLS = [get_dataset_metadata, search_datasets, list_datasets_by_agency, search_collections]
TOOLS_BY_NAME = {tool.name: tool for tool in TOOLS}

MAX_ITERATIONS = 5


def _message_content(response: AIMessage) -> str:
    content = response.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(str(part) for part in content)
    return str(content)


def _invoke_tool(tool_name: str, args: dict[str, Any]) -> str:
    tool = TOOLS_BY_NAME.get(tool_name)
    if tool is None:
        return f"Tool not found: {tool_name}"
    try:
        result = tool.invoke(args)
    except Exception as exc:  # noqa: BLE001 - surface tool failures to the LLM
        return f"Tool error ({tool_name}): {exc}"
    return result if isinstance(result, str) else json.dumps(result)


def run_category_agent_with_tools(system_prompt: str, user_query: str) -> str:
    """Run a category agent (LLM + tools) until it returns a final response."""
    model = llm.bind_tools(TOOLS)
    messages: list[BaseMessage] = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_query),
    ]

    for _ in range(MAX_ITERATIONS):
        response = invoke_llm(model, messages)
        if not isinstance(response, AIMessage):
            response = AIMessage(content=str(response))
        messages.append(response)

        tool_calls = response.tool_calls or []
        if not tool_calls:
            return _message_content(response)

        for tool_call in tool_calls:
            tool_name = tool_call.get("name", "")
            tool_args = tool_call.get("args", {})
            content = _invoke_tool(tool_name, tool_args)
            messages.append(
                ToolMessage(content=content, tool_call_id=tool_call.get("id", ""))
            )

    return "Maximum iterations reached without a final response."
