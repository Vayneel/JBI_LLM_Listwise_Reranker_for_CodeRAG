import os
import shutil
import stat
import git
import re

repo_url: str = "https://github.com/viarotel-org/escrcpy.git"  # change to whatever repo you need to skip repo url entering
local_repo_path: str = "repo"
repo: git.Repo

def on_remove_error(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)  # change to writable
    func(path)  # retry deletion

def preparation():
    if not os.path.exists(local_repo_path): return  # if we've cloned repository before
    shutil.rmtree(local_repo_path, onerror=on_remove_error)  # removes content of directory with repository


def repo_url_input():
    global repo_url

    while not re.fullmatch(r"https://github\.com/[\w-]+/[\w-]+\.git", repo_url):
        # todo more variations like ssh etc. if possible
        repo_url = input("Please enter the repo url (enter 'exit' to exit the loop): ").strip()

        if repo_url == "exit":
            print("Exiting program...")
            exit(0)


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


def main():
    repo_url_input()  # loop that waits for proper git url input
    clone_repo()  # tries to clone repo if exists




if __name__ == "__main__":
    preparation()
    main()