import chromadb
import os
from chromadb.api.types import IncludeEnum
from chromadb.utils import embedding_functions

from embedder import Embedder


class ChromaIndex:
    def __init__(self, embedding_model: str | Embedder = "all-MiniLM-L6-v2", persist_directory: str = "chroma_database",
                 debug: bool = False):

        self.__client = chromadb.PersistentClient(path=persist_directory)
        self.__debug = debug

        if not isinstance(embedding_model, Embedder):
            self.__built_in_embeddings = True

            if embedding_model == "all-MiniLM-L6-v2":
                self.__embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=embedding_model
                )
            # elif embedding_model == "openai":
            #     self.__embedding_function = embedding_functions.OpenAIEmbeddingFunction(
            #         api_key=os.environ.get("OPENAI_API_KEY"),
            #         model_name="text-embedding-ada-002"
            #     )
            else:
                print(f"Unsupported embedding model: {embedding_model}. Switching to `all-MiniLM-L6-v2`.")
                self.__embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=embedding_model
                )

            self.__collection = self.__client.get_or_create_collection(
                name="code_embeddings",
                metadata={"hnsw:space": "cosine"},
                embedding_function=self.__embedding_function
            )

        else:
            self.__built_in_embeddings = False

            self.__embedder: Embedder = embedding_model

            self.__collection = self.__client.get_or_create_collection(
                name="code_embeddings",
                metadata={"hnsw:space": "cosine"}
            )

        self.__record_count = self.__collection.count() + 1

    def get_record_count(self):
        return self.__collection.count()

    def add_record(self, record: dict[str, str | dict[str, str | int]]):
        if self.__built_in_embeddings:
            self.__collection.add(
                documents=[record["chunk"]],
                metadatas=[record["metadata"]],
                ids=[str(self.__record_count)]
            )
        else:
            embeddings = self.__embedder.embed_text(record["chunk"])

            self.__collection.add(
                embeddings=[embeddings],
                documents=[record["chunk"]],
                metadatas=[record["metadata"]],
                ids=[str(self.__record_count)]
            )

        self.__record_count += 1

    def search(self, query: str, k: int = 10):

        if not self.__built_in_embeddings:
            query = self.__embedder.embed_text(query)

        results = self.__collection.query(
            query_texts=[query],
            n_results=k,
            include=[
                IncludeEnum.documents,
                IncludeEnum.metadatas,
                IncludeEnum.distances,
            ],
        )

        return [
            {
                "content": document,
                "filename": metadata["filename"],
                "chunk-index": metadata["chunk-index"],
                "score": score
            }
            for document, metadata, score
            in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            )
        ]
