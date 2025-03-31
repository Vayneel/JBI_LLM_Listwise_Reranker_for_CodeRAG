import numpy as np
import chromadb
from chromadb.config import Settings

from embedder import Embedder


class Index:
    def __init__(self, embedder: Embedder, persist_directory: str = "database", reset_db: bool = False):
        self.__embedder: Embedder = embedder
        self.__client = chromadb.PersistentClient(path=persist_directory)

        self.__collection = self.__client.get_or_create_collection(
            name="code_embeddings",
            metadata={"hnsw:space": "cosine"}
        )

        self.__record_count = self.__collection.count() + 1


    def add_record(self, record: dict[str, str | dict[str, str | int]]):
        embeddings = self.__embedder.embed_text(record["chunk"])

        self.__collection.add(
            embeddings=[embeddings],
            documents=[record["chunk"]],
            metadatas=[record["metadata"]],
            ids=[str(self.__record_count)]
        )

        self.__record_count += 1
