"""Streamlit entrypoint for SG Open Data Dataset Recommender."""

from config.windows_patch import apply_windows_patch
apply_windows_patch()


import asyncio
import streamlit as st

from config.llm_errors import (
    LLMModelDeprecated,
    LLMServiceUnavailable,
    get_fallback_response,
    is_llm_service_error,
)
from src.graph import get_graph


def format_conversation_context(messages: list) -> str:
    """Format prior messages for context. Excludes the current turn."""
    parts = []
    for m in messages:
        role = "User" if m["role"] == "user" else "Assistant"
        parts.append(f"{role}: {m['content']}")
    return "\n".join(parts) if parts else ""


def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []


def main():
    st.set_page_config(
        page_title="SG Open Data Dataset Recommender",
        page_icon="📊",
        layout="wide",
    )
    st.title("📊 SG Open Data Dataset Recommender")
    st.caption(
        "Describe your data problem and get relevant dataset recommendations from data.gov.sg"
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
            prior = st.session_state.messages[:-1]
            conversation_context = format_conversation_context(prior)
            result = {}
            streamed_response = ""
            is_error = False

            # Generate a thread_id for checkpointing (one per user session)
            if "thread_id" not in st.session_state:
                st.session_state.thread_id = f"thread_{hash(st.session_state.get('session_id', 'default'))}"
            
            config = {"configurable": {"thread_id": st.session_state.thread_id}}
            
            try:
                # Get the async graph instance
                graph = asyncio.run(get_graph())

                # Stream like app_main.py: token events + tool events + node completion events
                async def consume_stream():
                    nonlocal streamed_response, result
                    resp = graph.astream_events(
                        {
                            "messages": [],
                            "user_query": prompt,
                            "conversation_context": conversation_context,
                            "routed_category": "",
                            "final_response": "",
                        },
                        config=config,
                        version="v2",
                    )

                    async for output in resp:
                        event_type = output.get("event")

                        if event_type == "on_chat_model_stream":
                            node = output.get("metadata", {}).get("langgraph_node", "")
                            if node == "category_agent":
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
                                cat = node_output.get("routed_category", "")
                                if cat:
                                    status.info(f"🔎 Searching category: {cat}...")
                                if "final_response" in node_output:
                                    result["final_response"] = node_output["final_response"]
                            if node_name == "category_agent" and "final_response" in node_output:
                                result["final_response"] = node_output["final_response"]
                asyncio.run(consume_stream())
                final = result.get("final_response", streamed_response or "No recommendations.")
                is_error = False
            except LLMModelDeprecated as e:
                final = f"{e}\nPlease switch to a supported model (e.g., gpt-5.1)."
                is_error = True
            except LLMServiceUnavailable as e:
                print(f"LLMServiceUnavailable: {e}")
                final = get_fallback_response()
                is_error = True
            except Exception as e:
                print(f"Unhandled exception ({type(e).__name__}): {e}")
                is_error = True
                final = (
                    get_fallback_response()
                    if is_llm_service_error(e)
                    else f"Error: {e}"
                )

            status.empty()
            display = final or streamed_response or "No recommendations."
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
