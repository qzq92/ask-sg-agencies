from config.windows_patch import apply_windows_patch
apply_windows_patch()

import os
from dotenv import load_dotenv
load_dotenv()

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage

api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key loaded: {bool(api_key)}, length: {len(api_key) if api_key else 0}")

llm = init_chat_model(
    model="gpt-5.3",
    model_provider="openai",
    api_key=api_key,
)

try:
    response = llm.invoke([HumanMessage(content="Say hello")])
    print("SUCCESS:", response.content)
except Exception as e:
    import traceback
    print("ERROR:", type(e).__name__, str(e))
    traceback.print_exc()