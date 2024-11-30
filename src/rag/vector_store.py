import os

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

vector_store = Chroma(
    embedding_function=OllamaEmbeddings(model="nomic-embed-text", base_url=os.environ.get("EMBEDDINGS_BASE_URL"))
)
