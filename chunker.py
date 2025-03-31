import os

class Chunker:
    """
    Class for chunking documents.
    """

    collection: list[dict[str, str | dict[str, str | int]]]  # list of chunks with metadata
    chunk_size: int  # lines to chunk
    chunk_overlap: int  # how many lines will overlap for each chunk

    """
    Example:
    
    collection = [
        {
            "chunk": "...",
            "metadata": {
                "filename": "foo.bar",
                "chunk-id": 0
            }
        },
        
        {
            "chunk": "...",
            "metadata": {
                "filename": "foo.bar",
                "chunk-id": 1
            }
        }
    ]
    """


    def __init__(self, chunk_size: int, chunk_overlap: int) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap


    @staticmethod
    def __extract_allowed_files(files: list[tuple[str, str]], allow_all: bool = False) -> list[tuple[str, str]]:
        if allow_all: return files

        allowed_extensions = (
            ".py",
            ".java",
            ".js",
            ".html",
            ".css",
            ".c",
            ".h",
            ".cpp",
            ".md",
            ".sh",
            ".cs",
            ".kt", ".kts", "ktm",
        )

        allowed_files = []

        for file in files:
            if any(file[1].endswith(ext) for ext in allowed_extensions):
                allowed_files.append(file)

        return allowed_files


    @staticmethod
    def __extract_file_contents(files: list[tuple[str, str]]) -> list[tuple[str, str]]:
        files_content = []

        for file in files:
            with open(os.path.join(file[0], file[1]), "r") as f:
                files_content.append(
                    (
                        file[1],  # filename
                        f.read()
                    )
                )

        return files_content


    def chunk_file(self, root, filename):
        path = os.path.join(root, filename)
        if not os.path.exists(path): return

        with open(path, "r") as f:
            file_content = f.readlines()




    def chunk_dir(self, path):
        if not os.path.exists(path): return None

        files = []

        for root, _, files in os.walk(path):
            for file in files:
                files.append((root, file))

        files = self.__extract_allowed_files(files)
        file_contents = self.__extract_file_contents(files)

        for filename, content in file_contents:
            self.chunk_file(filename, content)