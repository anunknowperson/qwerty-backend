import os

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

vector_store = Chroma(
    embedding_function=OllamaEmbeddings(
        model="mxbai-embed-large:latest", base_url=os.environ.get("EMBEDDINGS_API_BASE")
    )
)
