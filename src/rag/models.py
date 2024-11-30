import os

from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = "_"  # No API key is needed

model = ChatOpenAI(model="saiga", streaming=True, base_url=os.environ.get("MODEL_API_BASE"))
