from config.win_ssl_fix import apply_windows_ssl_fix
apply_windows_ssl_fix()

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatOpenAI(
    model="gpt-5-mini",  # or whatever model you have in config.py
    api_key=os.getenv("OPENAI_API_KEY"),
)

try:
    response = llm.invoke([HumanMessage(content="Say hello")])
    print("SUCCESS:", response.content)
except Exception as e:
    print("ERROR:", type(e).__name__, str(e))