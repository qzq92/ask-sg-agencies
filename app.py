"""Streamlit entrypoint for SG Open Data Dataset Recommender."""

import re
import streamlit as st

from config.llm_errors import LLMServiceUnavailable, get_fallback_response, is_llm_service_error
from src.graph import graph


def extract_dataset_links(text: str) -> list[tuple[str, str]]:
    """Extract dataset links from markdown-style URLs in text."""
    pattern = r"https://data\.gov\.sg/datasets/(d_[a-f0-9]+)/view"
    matches = re.findall(pattern, text)
    return [(m, f"https://data.gov.sg/datasets/{m}/view") for m in matches]


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


def render_dataset_cards(links: list[tuple[str, str]]):
    """Render dataset links as formatted cards."""
    for ds_id, url in links:
        with st.container():
            st.markdown(
                f"""
            <div style="
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 16px;
                margin: 8px 0;
                background: #fafafa;
            ">
                <strong>Dataset:</strong> {ds_id}<br>
                <a href="{url}" target="_blank">View on data.gov.sg →</a>
            </div>
            """,
                unsafe_allow_html=True,
            )


def main():
    st.set_page_config(
        page_title="SG Open Data Dataset Recommender",
        page_icon="📊",
        layout="centered",
    )
    st.title("📊 SG Open Data Dataset Recommender")
    st.caption(
        "Describe your data problem and get relevant dataset recommendations from data.gov.sg"
    )

    init_session_state()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("links"):
                render_dataset_cards(msg["links"])

    if prompt := st.chat_input("Describe your data problem or need..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            status = st.empty()
            status.info("🔍 Analyzing your query...")
            prior = st.session_state.messages[:-1]
            conversation_context = format_conversation_context(prior)
            result = {}
            try:
                for event in graph.stream(
                    {
                        "messages": [],
                        "user_query": prompt,
                        "conversation_context": conversation_context,
                        "routed_categories": [],
                        "category_results": {},
                        "final_response": "",
                    },
                    stream_mode="values",
                ):
                    result = event
                    if "routed_categories" in event and event["routed_categories"]:
                        cats = ", ".join(event["routed_categories"])
                        num_cats = len(event["routed_categories"])
                        parallel_note = " (in parallel)" if num_cats > 1 else ""
                        status.info(f"🔎 Searching {num_cats} categories{parallel_note}: {cats}...")
                    if "category_results" in event and event["category_results"]:
                        status.info("✨ Synthesizing recommendations...")

                final = result.get("final_response", "No recommendations.")
            except LLMServiceUnavailable:
                final = get_fallback_response()
            except Exception as e:
                final = (
                    get_fallback_response()
                    if is_llm_service_error(e)
                    else f"Error: {e}"
                )

            status.empty()
            st.markdown(final)
            links = extract_dataset_links(final)
            if links:
                st.markdown("**Recommended datasets:**")
                render_dataset_cards(links)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": final,
                "links": links,
            }
        )


if __name__ == "__main__":
    main()
