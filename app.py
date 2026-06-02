"""Streamlit entrypoint for SG Open Data Dataset Recommender."""

from __future__ import annotations

from config.windows_patch import apply_windows_patch

apply_windows_patch()

import asyncio
from typing import Literal, TypedDict

import streamlit as st

from config.llm_errors import (
    LLMModelDeprecated,
    LLMServiceUnavailable,
    get_fallback_response,
    is_llm_service_error,
)
from config.routing import MAX_ROUTED_CATEGORIES
from src.graph import format_category_list, get_graph


class ChatMessage(TypedDict):
    role: Literal["user", "assistant"]
    content: str


def format_conversation_context(messages: list[ChatMessage]) -> str:
    """Format prior messages for context. Excludes the current turn."""
    parts = []
    for message in messages:
        role = "User" if message["role"] == "user" else "Assistant"
        parts.append(f"{role}: {message['content']}")
    return "\n".join(parts) if parts else ""


def init_session_state() -> None:
    if "messages" not in st.session_state:
        st.session_state.messages = []


def main() -> None:
    st.set_page_config(
        page_title="SG Open Data Dataset Recommender",
        page_icon="📊",
        layout="wide",
    )
    st.title("📊 SG Open Data Dataset Recommender")
    st.caption(
        "Describe your data problem and get relevant dataset recommendations from data.gov.sg"
    )
    st.info(
        f"**Note:** Each search is limited to at most **{MAX_ROUTED_CATEGORIES} data categories**. "
        "If your question spans more than that, only the top "
        f"{MAX_ROUTED_CATEGORIES} most relevant categories are searched, to keep response time and "
        "LLM usage reasonable."
    )

    init_session_state()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Describe your data problem or need..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            status = st.empty()
            response_placeholder = st.empty()
            status.info("🔍 Analyzing your query...")
            prior: list[ChatMessage] = st.session_state.messages[:-1]
            conversation_context = format_conversation_context(prior)
            result: dict[str, str] = {}
            streamed_response = ""
            is_error = False
            display = "No recommendations."

            if "thread_id" not in st.session_state:
                st.session_state.thread_id = (
                    f"thread_{hash(st.session_state.get('session_id', 'default'))}"
                )

            config = {"configurable": {"thread_id": st.session_state.thread_id}}

            try:
                graph = asyncio.run(get_graph())

                async def consume_stream() -> None:
                    nonlocal streamed_response, result
                    stream = graph.astream_events(
                        {
                            "messages": [],
                            "user_query": prompt,
                            "conversation_context": conversation_context,
                            "routed_categories": [],
                            "routed_category": "",
                            "category_results": {},
                            "final_response": "",
                        },
                        config=config,
                        version="v2",
                    )

                    async for output in stream:
                        event_type = output.get("event")
                        node = output.get("metadata", {}).get("langgraph_node", "")

                        if event_type == "on_chat_model_stream":
                            if node in ("category_agents", "synthesizer"):
                                chunk = output.get("data", {}).get("chunk")
                                if chunk and hasattr(chunk, "content") and chunk.content:
                                    streamed_response += chunk.content
                                    response_placeholder.markdown(streamed_response + "▌")

                        if event_type == "on_tool_start":
                            tool_name = output.get("name", "tool")
                            status.info(f"🔧 Running `{tool_name}`...")

                        if event_type == "on_tool_end":
                            tool_name = output.get("name", "tool")
                            status.info(f"✅ `{tool_name}` completed")

                        if event_type == "on_chain_end":
                            node_name = output.get("name", "")
                            node_output = output.get("data", {}).get("output", {})
                            if node_name == "supervisor":
                                categories = node_output.get("routed_categories", [])
                                if categories:
                                    labels = format_category_list(categories)
                                    status.info(f"🔎 Searching: {labels}...")
                                if "final_response" in node_output:
                                    result["final_response"] = node_output["final_response"]
                            if node_name == "category_agents" and "final_response" in node_output:
                                result["final_response"] = node_output["final_response"]
                            if node_name == "synthesizer" and "final_response" in node_output:
                                result["final_response"] = node_output["final_response"]

                asyncio.run(consume_stream())
                display = result.get("final_response", streamed_response or "No recommendations.")
            except LLMModelDeprecated as exc:
                display = f"{exc}\nPlease switch to a supported model (e.g., gpt-5.1)."
                is_error = True
            except LLMServiceUnavailable:
                display = get_fallback_response()
                is_error = True
            except (RuntimeError, asyncio.CancelledError) as exc:
                display = f"Error: {exc}"
                is_error = True
            except Exception as exc:
                is_error = True
                display = (
                    get_fallback_response()
                    if is_llm_service_error(exc)
                    else f"Error: {exc}"
                )

            status.empty()
            response_placeholder.markdown(display)

        if not is_error:
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": display,
                }
            )


if __name__ == "__main__":
    main()
