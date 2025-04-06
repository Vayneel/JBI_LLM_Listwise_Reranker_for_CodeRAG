import faiss
import numpy as np
import os
import pickle
from typing import List, Dict, Any, Optional, Union
from embedder import Embedder


class FaissIndex:
    """
    A vector index implementation using FAISS.
    """

    def __init__(self, embedder: Embedder, persist_directory: str = "faiss_database", debug: bool = False):
        """
        Initialize the FAISS index.

        Args:
            embedder: An instance of the Embedder class
            persist_directory: Directory where the index will be saved
            debug: Whether to print debug information
        """
        self.__embedder: Embedder = embedder
        self.__persist_directory: str = persist_directory
        self.__debug: bool = debug

        # Create persist directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)

        # Paths for saving index components
        self.__index_path = os.path.join(persist_directory, "faiss_index.bin")
        self.__metadata_path = os.path.join(persist_directory, "metadata.pkl")
        self.__documents_path = os.path.join(persist_directory, "documents.pkl")

        # Initialize or load index and related data
        self.__index = None
        self.__documents = []
        self.__metadatas = []
        self.__record_count = 0

        self.__initialize_or_load_index()

    def __initialize_or_load_index(self):
        """Initialize a new index or load an existing one."""
        if os.path.exists(self.__index_path) and os.path.exists(self.__metadata_path) and os.path.exists(
                self.__documents_path):
            if self.__debug:
                print(f"Loading existing index from {self.__persist_directory}")

            # Load the FAISS index
            self.__index = faiss.read_index(self.__index_path)

            # Load documents and metadata
            with open(self.__documents_path, 'rb') as f:
                self.__documents = pickle.load(f)

            with open(self.__metadata_path, 'rb') as f:
                self.__metadatas = pickle.load(f)

            self.__record_count = len(self.__documents)
        else:
            if self.__debug:
                print(f"Creating new index in {self.__persist_directory}")

            # Get dimension from a sample embedding
            sample_text = "sample code"
            sample_embedding = self.__embedder.embed_text(sample_text)
            dimension = sample_embedding.shape[0]

            # Create a new FAISS index
            self.__index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
            self.__documents = []
            self.__metadatas = []
            self.__record_count = 0

    def get_record_count(self) -> int:
        """
        Get the number of records in the index.

        Returns:
            int: Number of records
        """
        return self.__record_count

    def add_record(self, record: Dict[str, Union[str, Dict[str, Union[str, int]]]]):
        """
        Add a record to the index.

        Args:
            record: A dictionary containing the chunk and metadata
        """
        chunk = record["chunk"]
        metadata = record["metadata"]

        if self.__debug:
            print(f"Adding record with metadata: {metadata}")

        # Check for duplicates (optional)
        # This is a simple check, you might want a more sophisticated one
        # for i, doc in enumerate(self.__documents):
        #     if doc == chunk:
        #         if self.__debug:
        #             print(f"Duplicate found for {metadata['filename']}, chunk {metadata['chunk-index']}")
        #         return

        # Get embedding
        embedding = self.__embedder.embed_text(chunk)

        # Convert to float32 and reshape for FAISS
        embedding = np.float32(embedding).reshape(1, -1)

        # Add to FAISS index
        self.__index.add(embedding)

        # Store document and metadata
        self.__documents.append(chunk)
        self.__metadatas.append(metadata)

        self.__record_count += 1

        # Periodically save the index (optional)
        if self.__record_count % 100 == 0:
            self.save()

    def search(self, query: str, k: int = 10) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query: The search query
            k: Number of results to return

        Returns:
            List of dictionaries containing search results
        """
        if self.__record_count == 0:
            return []

        # Get query embedding
        query_embedding = self.__embedder.embed_text(query)

        # Convert to float32 and reshape for FAISS
        query_embedding = np.float32(query_embedding).reshape(1, -1)

        # Search
        distances, indices = self.__index.search(query_embedding, min(k, self.__record_count))

        # Format results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.__documents):
                continue

            document = self.__documents[idx]
            metadata = self.__metadatas[idx]

            results.append({
                "content": document,
                "filename": metadata["filename"],
                "chunk-index": metadata["chunk-index"],
                "score": float(distances[0][i])  # Convert to native Python float
            })

        return results

    def save(self):
        """Save the index and related data to disk."""
        if self.__debug:
            print(f"Saving index to {self.__persist_directory}")

        # Save the FAISS index
        faiss.write_index(self.__index, self.__index_path)

        # Save documents and metadata
        with open(self.__documents_path, 'wb') as f:
            pickle.dump(self.__documents, f)

        with open(self.__metadata_path, 'wb') as f:
            pickle.dump(self.__metadatas, f)

    def clear(self):
        """Clear the index and related data."""
        if self.__debug:
            print("Clearing index")

        # Reinitialize the index
        dimension = self.__index.d
        self.__index = faiss.IndexFlatIP(dimension)
        self.__documents = []
        self.__metadatas = []
        self.__record_count = 0

        # Save the empty index
        self.save()
