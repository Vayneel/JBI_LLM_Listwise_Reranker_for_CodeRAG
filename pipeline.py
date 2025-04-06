import sys
import re
import os

from utilities import print_done, remove_directory
from chunker import Chunker, ChunkingMode
from embedder import Embedder
from index_chroma import ChromaIndex
from index_faiss import FaissIndex

import git


LOCAL_REPO_PATH: str = "repo"
ENCODING: str | None = "UTF-8"
DEFAULT_INDEX: type(FaissIndex) | type(ChromaIndex) = ChromaIndex
LOCAL_DB_PATH: str = "faiss_database" if DEFAULT_INDEX is FaissIndex else "chroma_index"

debug: bool = "--debug" in sys.argv

reset_db: bool = "--reset-db" in sys.argv

SKIP_CLONING: bool = "--skip-cloning" in sys.argv and os.path.exists(LOCAL_REPO_PATH)
if "--skip-cloning" in sys.argv: print("Cloning will be skipped" if SKIP_CLONING else "Cloning won't be skipped")
SKIP_INDEXING: bool = "--skip-indexing" in sys.argv and not reset_db and os.path.exists(LOCAL_DB_PATH)  # todo skip cloning dependant?
if "--skip-indexing" in sys.argv: print("Indexing will be skipped" if SKIP_INDEXING else "Indexing won't be skipped")
PRINT_RECORD_COUNT: bool = "--print-record-count" in sys.argv
if "--faiss" in sys.argv:
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
    INDEX = FaissIndex
elif "--chroma" in sys.argv:
    INDEX = ChromaIndex
else:
    INDEX = DEFAULT_INDEX  # todo maybe another later
print(f"{"FAISS" if INDEX is FaissIndex else "Chroma"} will be used as index")
BUILT_IN_EMBEDDINGS: bool = "--built-in-embeddings" in sys.argv and INDEX is ChromaIndex
if BUILT_IN_EMBEDDINGS: print("Built-in embeddings activated")

# repo_url: str = ""  # change to whatever repo you need to skip repo url entering
repo_url: str = "https://github.com/viarotel-org/escrcpy.git"
repo: git.Repo
embedder: Embedder
index: INDEX
chunking_mode: ChunkingMode = ChunkingMode.LINES  # lines or chars
chunk_size: int = 720  # how many lines / chars to put in single chunk (including chunk overlap)
chunk_overlap: int = 240  # how many lines / chars are going to overlap with other chunks (half with previous, half with following chunk)
chunk_all_files: bool = True  # enable at your own risk



@print_done("Program preparation")
def preparation() -> None:
    if not SKIP_CLONING:
        remove_directory(LOCAL_REPO_PATH)  # if we've cloned some repository before, we need to remove old repo
    if reset_db:
        remove_directory(LOCAL_DB_PATH)  # removes old chroma_database if enabled


def repo_url_input():
    if SKIP_CLONING: return

    global repo_url

    while not re.fullmatch(r"https://github\.com/[\w-]+/[\w-]+\.git", repo_url):
        # todo more variations like ssh etc. if possible
        repo_url = input("Please enter the repo url (enter 'exit' to exit the loop): ").strip()

        if repo_url == "exit":
            print("Exiting program...")
            exit(0)



@print_done("Repository cloning")
def clone_repo():
    if SKIP_CLONING: return

    global repo

    try:
        repo = git.Repo.clone_from(repo_url, to_path=LOCAL_REPO_PATH)
    except git.CommandError:
        print("Failed to clone.")
        exit(1)

    if repo.bare:
        print("This repo is bare. Exiting program...")
        exit(0)


@print_done("Initializing index")
def initialize_index():
    global embedder, index

    if BUILT_IN_EMBEDDINGS:
        index = INDEX(
            persist_directory=LOCAL_DB_PATH,
            debug=debug
        )
    else:
        embedder = Embedder(debug=debug)
        index = INDEX(
            embedder=embedder,
            persist_directory=LOCAL_DB_PATH,
            debug=debug
        )
    if PRINT_RECORD_COUNT: print(index.get_record_count())


@print_done("Indexing")
def index_files():
    if SKIP_INDEXING: return

    chunker = Chunker(
        chunking_mode=chunking_mode,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        embedder=embedder,
        chunk_all_files=chunk_all_files,
        encoding=ENCODING,
        debug=debug,
    )
    for chunk in chunker.chunk_repo(path=LOCAL_REPO_PATH):
        index.add_record(chunk)


def user_query(query: str):
    if not index: return

    return index.search(query)

