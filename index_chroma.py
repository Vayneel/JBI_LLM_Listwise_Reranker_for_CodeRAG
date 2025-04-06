import chromadb
import os
from chromadb.api.types import IncludeEnum
from chromadb.utils import embedding_functions

from embedder import Embedder


class ChromaIndex:
    def __init__(self, embedding_model_name: str = "all-MiniLM-L6-v2", persist_directory: str = "chroma_database",
                 debug: bool = False):
        self.__client = chromadb.PersistentClient(path=persist_directory)
        self.__debug = debug
        self.__built_in_embeddings = True

        if embedding_model_name == "all-MiniLM-L6-v2":
            self.__embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=embedding_model_name
            )
        # elif embedding_model_name == "openai":
        #     self.__embedding_function = embedding_functions.OpenAIEmbeddingFunction(
        #         api_key=os.environ.get("OPENAI_API_KEY"),
        #         model_name="text-embedding-ada-002"
        #     )
        else:
            print(f"Unsupported embedding model: {embedding_model_name}. Switching to `all-MiniLM-L6-v2`.")
            self.__embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=embedding_model_name
            )

        self.__collection = self.__client.get_or_create_collection(
            name="code_embeddings",
            metadata={"hnsw:space": "cosine"},
            embedding_function=self.__embedding_function
        )

        self.__record_count = self.__collection.count() + 1


    def __init__(self, embedder: Embedder, persist_directory: str = "chroma_database", debug: bool = False):
        self.__embedder: Embedder = embedder
        self.__client = chromadb.PersistentClient(path=persist_directory)
        self.__debug = debug

        self.__collection = self.__client.get_or_create_collection(
            name="code_embeddings",
            metadata={"hnsw:space": "cosine"}
        )

        self.__record_count = self.__collection.count() + 1


    def get_record_count(self):
        return self.__collection.count()

    def add_record(self, record: dict[str, str | dict[str, str | int]]):
        # No need to manually embed text anymore
        self.__collection.add(
            documents=[record["chunk"]],
            metadatas=[record["metadata"]],
            ids=[str(self.__record_count)]
        )

        self.__record_count += 1

    def search(self, query: str, k: int = 10):
        # No need to manually embed the query
        results = self.__collection.query(
            query_texts=[query],  # Use query_texts instead of query_embeddings
            n_results=k,
            include=[
                IncludeEnum.documents,
                IncludeEnum.metadatas,
                IncludeEnum.distances,  # Re-enabled distances
            ],
        )

        return [
            {
                "content": document,
                "filename": metadata["filename"],
                "chunk-index": metadata["chunk-index"],
                "score": score  # Re-added scores
            }
            for document, metadata, score
            in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]