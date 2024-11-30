import logging
import os

import pandas as pd
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

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
            + f" {row["category"]}, {row["name.1"]},"
            + f" список телефонных номеров: {row["phones"][1:-1].replace(",", ", ")}\n\n"
        ),
        axis=1,
    )

    logging.info("Starting adding contacts to storage...")

    _ = vector_store.add_texts(contacts)

    logging.info("Finish adding contacts to storage.")


load_contacts()
