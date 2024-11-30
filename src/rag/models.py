import os

import dotenv
from langchain_openai import ChatOpenAI

dotenv.load_dotenv()

os.environ["OPENAI_API_KEY"] = "_"  # No API key is needed

model = ChatOpenAI(model="saiga", streaming=True, base_url=os.environ.get("MODEL_API_BASE"))
