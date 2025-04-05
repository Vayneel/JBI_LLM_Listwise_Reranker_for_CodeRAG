import os
import shutil
import stat
import sys

import git
import re
from pprint import pprint

from chunker import Chunker, ChunkingMode
from embedder import Embedder
from index import Index

debug: bool = "--debug" in sys.argv
reset_db: bool = "--reset-db" in sys.argv

# repo_url: str = ""  # change to whatever repo you need to skip repo url entering
repo_url: str = "https://github.com/viarotel-org/escrcpy.git"
# repo_url: str = "https://github.com/Vayneel/Bragi.git"

local_repo_path: str = "repo"
local_db_path: str = "database"
repo: git.Repo
index: Index
chunking_mode: ChunkingMode = ChunkingMode.CHARS  # lines or chars
chunk_size: int = 720  # how many lines / chars to put in single chunk (including chunk overlap)
chunk_overlap: int = 240  # how many lines / chars are going to overlap with other chunks (half with previous, half with following chunk)
chunk_all_files: bool = True  # enable at your own risk
encoding: str | None = "UTF-8"  # change at your own risk


def print_done(process_name: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(process_name + "...", end="")
            func(*args, **kwargs)
            print("Done.")

        return wrapper

    return decorator


def on_remove_error(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)  # change to writable
    func(path)  # retry deletion


def remove_directory(path: str) -> None:
    if not os.path.exists(path): return
    shutil.rmtree(path, onerror=on_remove_error)  # removes content of directory with repository


@print_done("Program preparation")
def preparation() -> None:
    remove_directory(local_repo_path)  # if we've cloned some repository before, we need to remove old repo
    if reset_db: remove_directory(local_db_path)  # removes old database if enabled


def repo_url_input():
    global repo_url

    while not re.fullmatch(r"https://github\.com/[\w-]+/[\w-]+\.git", repo_url):
        # todo more variations like ssh etc. if possible
        repo_url = input("Please enter the repo url (enter 'exit' to exit the loop): ").strip()

        if repo_url == "exit":
            print("Exiting program...")
            exit(0)



@print_done("Repository cloning")
def clone_repo():
    global repo

    try:
        repo = git.Repo.clone_from(repo_url, to_path=local_repo_path)
    except git.CommandError:
        print("Failed to clone.")
        exit(1)

    if repo.bare:
        print("This repo is bare. Exiting program...")
        exit(0)


@print_done("Chunking & embedding files")
def index_files():
    global index

    embedder = Embedder(debug=debug)
    index = Index(embedder, debug=debug)
    if "--skip-index" not in sys.argv:  # todo add check if db does not exist
        chunker = Chunker(
            chunking_mode=chunking_mode,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            chunk_all_files=chunk_all_files,
            encoding=encoding,
            debug=debug,
        )
        for chunk in chunker.chunk_repo(path=local_repo_path):
            index.add_record(chunk)


def user_query():
    if not index: return

    # query = input("Please enter the query: ").strip()
    # print(index.search(query))
    query = "is there a function related to volume?"

    pprint(index.search(query, k=3))


def main():
    if "--skip-clone" not in sys.argv or not os.path.exists(local_repo_path):
        preparation()  # deletion of old files
        repo_url_input()  # loop that waits for proper git url input
        clone_repo()  # tries to clone repo if exists
    index_files()  # chunking, embedding and indexing files from repo
    user_query()
    print("All set up.\n")


if __name__ == "__main__":
    main()

