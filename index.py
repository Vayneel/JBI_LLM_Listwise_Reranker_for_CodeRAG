import chromadb
from chromadb.api.types import IncludeEnum

from embedder import Embedder


class Index:
    __debug: bool

    def __init__(self, embedder: Embedder, persist_directory: str = "database", debug: bool = False):
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
        # todo add duplicate check
        embeddings = self.__embedder.embed_text(record["chunk"])

        self.__collection.add(
            embeddings=[embeddings],
            documents=[record["chunk"]],
            metadatas=[record["metadata"]],
            ids=[str(self.__record_count)]
        )

        self.__record_count += 1

    def search(self, query: str, k: int = 10):
        query_embedding = self.__embedder.embed_text(query)

        results = self.__collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            # include=[chromadb.Documents, chromadb.Metadata],
            # include=["documents", "metadatas"],
            include=[
                IncludeEnum.documents,
                IncludeEnum.metadatas,
            ],
        )

        return [
            {
                "content": document,
                "filename": metadata["filename"],
                "chunk-index": metadata["chunk-index"],
                # "score": score
            }
            for document, metadata,  # score
            in zip(
                results["documents"][0],
                results["metadatas"][0],
                # results["distances"][0]
            )
        ]
