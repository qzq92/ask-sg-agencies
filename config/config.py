"""Configuration and LLM initialization."""

import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

load_dotenv()

# OpenAI API - used for all agents
llm = ChatOpenAI(
    model="gpt-5.1",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0,
)
