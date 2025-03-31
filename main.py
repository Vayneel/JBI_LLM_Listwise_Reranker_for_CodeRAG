import os
import git
import re

repo_url: str = ""
local_repo_path: str = "repo"
repo: git.Repo


def preparation():
    if not os.path.exists(local_repo_path): return

    for root, _, files in os.walk(local_repo_path):
        for file in files:
            os.remove(os.path.join(root, file))

    for root, dirs, _ in os.walk(local_repo_path):
        for directory in dirs:
            os.rmdir(os.path.join(root, directory))


def main():
    global repo_url, local_repo_path, repo

    # https://github.com/gitpython-developers/GitPython.git
    while not re.fullmatch(r"https://github\.com/[\w-]+/[\w-]+\.git", repo_url):
        # todo more variations like ssh etc. if possible
        repo_url = input("Please enter the repo url: ").strip()

    try:
        repo = git.Repo.clone_from(repo_url, to_path=local_repo_path)
    except git.CommandError:
        print("Failed to clone.")
        exit(1)

    if repo.bare:
       print("This repo is bare")

if __name__ == "__main__":
    preparation()
    main()