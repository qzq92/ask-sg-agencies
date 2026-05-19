"""Configuration and LLM initialization."""

import os
from config.win_ssl_fix import apply_windows_ssl_fix

apply_windows_ssl_fix()

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# OpenAI API - used for all agents
llm = ChatOpenAI(
    model="gpt-5-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
)
