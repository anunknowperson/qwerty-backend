import logging
import os
from pathlib import Path

import pandas as pd
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm

vector_store = Chroma(
    embedding_function=OllamaEmbeddings(
        model="mxbai-embed-large:latest", base_url=os.environ.get("EMBEDDINGS_API_BASE")
    )
)


def load_contacts():
    df = pd.read_excel("data/contacts.xlsx")

    contacts = df.apply(
        lambda row: (
            f"{row["name"]} район,"
            f" {row["category"]}, {row["name.1"]},"
            f" список телефонных номеров: {row["phones"][1:-1].replace(",", ", ")}\n\n"
        ),
        axis=1,
    )

    logging.info("Starting adding contacts to storage...")

    _ = vector_store.add_texts(contacts)

    logging.info("Finish adding contacts to storage.")


load_contacts()


def load_knowledge_base_data():
    data_dir = Path("./knowledge_base")
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    for article_path in tqdm(data_dir.iterdir()):
        with open(article_path) as f:
            data = Document(f.read(), link="https://gu.spb.ru/knowledge-base/")
            splitted = splitter.split_documents([data])
            _ = vector_store.add_documents(splitted)


load_knowledge_base_data()
