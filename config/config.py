"""Configuration and LLM initialization."""

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# OpenAI API - used for all agents
llm = init_chat_model(
    model="gpt-5.3",
    model_provider="openai",
    api_key=api_key,
)
