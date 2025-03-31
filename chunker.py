import os

class Chunker:
    """
    Class for chunking documents.
    """

    __chunk_size: int  # lines to chunk
    __chunk_overlap: int  # how many lines will overlap for each chunk
    __chunk_all_files: bool  # used in __extract_allowed_files method
    collection: list[dict[str, str | dict[str, str | int]]]  # list of chunks with metadata

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


    def __init__(self, chunk_size: int, chunk_overlap: int, chunk_all_files: bool = False) -> None:
        self.__chunk_size = chunk_size
        self.__chunk_overlap = chunk_overlap
        self.__chunk_all_files = chunk_all_files
        self.collection = []

        if chunk_size < self.__chunk_overlap + 1: self.__chunk_size = self.__chunk_overlap + 1


    def __extract_allowed_files(self, files: list[tuple[str, str]]) -> list[tuple[str, str]]:
        if self.__chunk_all_files: return files

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


    def __is_file_allowed(self, file: str) -> bool:
        if self.__chunk_all_files: return True

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

        if file.endswith(allowed_extensions):
            return True

        return False


    def __chunk_file(self, filename: str, content: list[str]):
        current_line: int = 0
        chunk_index: int = 0
        line_step: int = self.__chunk_size - (self.__chunk_overlap // 2 + self.__chunk_overlap % 2)

        while current_line < len(content):
            chunk: str = ""

            for line_index in range(self.__chunk_size):
                if current_line + line_index >= len(content): return

                chunk += content[current_line + line_index]

            yield {
                "chunk": chunk,
                "metadata": {
                    "filename": filename,
                    "chunk-index": chunk_index,
                }
            }

            current_line += line_step
            chunk_index += 1


    def __chunk_files(self, files: list[tuple[str, str]]):
        for file in files:
            with open(os.path.join(file[0], file[1]), "r") as f:
                yield from self.__chunk_file(
                    file[1],  # filename
                    f.readlines()
                )


    def chunk_repo(self, path):
        if not os.path.exists(path): return None

        for root, _, files in os.walk(path):
            for file in files:
                if not self.__is_file_allowed(file): continue

                with open(os.path.join(root, file), "r") as f:
                    yield from self.__chunk_file(file, f.readlines())
