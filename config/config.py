"""Configuration and LLM initialization."""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# Perplexity API via OpenAI-compatible interface
llm = ChatOpenAI(
    model="sonar-pro",
    api_key=os.getenv("PPLX_API_KEY"),
    base_url="https://api.perplexity.ai",
    temperature=0,
)
