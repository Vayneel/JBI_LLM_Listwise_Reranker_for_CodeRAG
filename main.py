import os
import sys

from pipeline import *

def main():
    preparation()  # deletion of old files
    repo_url_input()  # loop that waits for proper git url input
    clone_repo()  # tries to clone repo if exists
    initialize_index()
    index_files()  # chunking, embedding and indexing files from repo
    print("All set up.\n")

    query = ""
    while query != "q":
        query = input("Enter query (q to quit): ")
        if query == "q": break
        user_query(query)


if __name__ == "__main__":
    main()

