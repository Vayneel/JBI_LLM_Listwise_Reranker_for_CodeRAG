import os
import shutil
import stat

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