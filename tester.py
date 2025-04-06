import json
from pipeline import *


def load_test_data(json_path: str = 'test_inputs.json'):
    with open(json_path, 'r') as f:
        return json.load(f)


def recall_at_k(retrieved, relevant, k=10):
    retrieved_at_k = set(retrieved[:k])
    relevant_set = set(relevant)
    hits = sum(1 for item in retrieved_at_k if item in relevant_set)
    return hits / min(len(relevant), k)


def run_tests():
    test_data = load_test_data()

    preparation()  # deletion of old files
    repo_url_input()  # loop that waits for proper git url input
    clone_repo()  # tries to clone repo if exists
    initialize_index()
    index_files()  # chunking, embedding and indexing files from repo

    for test_case in test_data:
        query = test_case["question"]
        expected_files = test_case["files"]

        results = user_query(query)
        if results:
            retrieved_files = [result["filename"] for result in user_query(query)]
            score = recall_at_k(retrieved_files, expected_files)
        else:
            retrieved_files = []
            score = 0
        print(f"Query: {query}")
        print(f"Expected files: {expected_files}")
        print(f"Retrieved files: {retrieved_files}")
        print(f"Match score: {score:.2f}\n")


if __name__ == "__main__":
    run_tests()
