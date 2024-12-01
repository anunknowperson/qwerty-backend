import logging
import os
from pathlib import Path

import pandas as pd
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tqdm import tqdm


class VectorStore:
    def __init__(self):
        self.embeddings = OllamaEmbeddings(
            model="mxbai-embed-large:latest", base_url=os.environ.get("EMBEDDINGS_API_BASE")
        )
        self.contacts_db = PGVector(
            embeddings=self.embeddings,
            connection="postgresql+psycopg://user:password@localhost:5432/contacts",
        )

        self.knowledge_db = PGVector(
            embeddings=self.embeddings,
            connection="postgresql+psycopg://user:password@localhost:5432/knowledge",
        )

        self.gov_db = PGVector(
            embeddings=self.embeddings,
            connection="postgresql+psycopg://user:password@localhost:5432/gov",
        )

    def load_data(self):
        self.__load_contacts()
        self.__load_knowledge_base_data()
        self.__load_gov_spb_data()
        # self.__load_afisha_data()

    def __load_contacts(self):
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

        _ = self.contacts_db.add_texts(contacts)

        logging.info("Finish adding contacts to storage.")

    def __load_knowledge_base_data(self):
        data_dir = Path("./knowledge_base")
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        for article_path in tqdm(data_dir.iterdir()):
            with open(article_path) as f:
                data = Document(f.read(), link="https://gu.spb.ru/knowledge-base/")
                splitted = splitter.split_documents([data])
                _ = self.knowledge_db.add_documents(splitted)

    def __load_gov_spb_data(self):
        data_dir = Path("./gov_spb")
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        for article_path in tqdm(data_dir.iterdir()):
            with open(article_path) as f:
                data = Document(f.read())
                splitted = splitter.split_documents([data])
                _ = self.gov_db.add_documents(splitted)

    def similarity_search(self, query: str, k: int, theme="none") -> list[Document]:
        match theme:
            case "contacts":
                return self.contacts_db.similarity_search(query, k=k)
            case "knowledge":
                return self.knowledge_db.similarity_search(query, k=k)
            case "gov":
                return self.gov_db.similarity_search(query, k=k)
            case _:
                return [
                    *self.contacts_db.similarity_search(query, min(k // 3, 1)),
                    *self.knowledge_db.similarity_search(query, min(k // 3, 1)),
                    *self.gov_db.similarity_search(query, min(k // 3, 1)),
                ]


vector_store = VectorStore()
