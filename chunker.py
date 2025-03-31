import os
from enum import Enum


class ChunkingMode(Enum):
    LINES = "lines"
    CHARS = "chars"


class Chunker:
    """
    Class for chunking documents.
    """

    __chunk_size: int  # lines to chunk
    __chunk_overlap: int  # how many lines will overlap for each chunk
    __chunk_all_files: bool  # used in __extract_allowed_files method
    __file_encoding: str = None # switches to latin-1 if __chunk_all_files enabled to prevent errors

    """
    Example:
    
    collection = [
        {
            "metadata": {
                "filename": "foo.bar",
                "chunk-id": N
            },
            
            "chunk": "...",
        },
    ]
    """


    def __init__(self, chunking_mode: ChunkingMode, chunk_size: int, chunk_overlap: int,
                 chunk_all_files: bool = False) -> None:
        self.chunking_mode: ChunkingMode = chunking_mode
        self.__chunk_size = chunk_size
        self.__chunk_overlap = chunk_overlap
        self.__chunk_all_files = chunk_all_files

        if chunk_all_files: self.__file_encoding = "latin-1"

        if chunk_size < self.__chunk_overlap + 1: self.__chunk_size = self.__chunk_overlap + 1


    def __is_file_allowed(self, file: str) -> bool:
        if self.__chunk_all_files: return True

        allowed_extensions = (
            ".py",
            ".java",
            ".js",
            ".html",
            ".css",
            ".c", ".h", ".cpp", ".cs",
            ".md", ".txt",
            ".sh",
            ".kt", ".kts", "ktm",
        )

        if file.endswith(allowed_extensions):
            return True

        return False


    def __chunk_lines(self, filename: str, content: list[str]):
        current_line: int = 0
        chunk_index: int = 0  # index of chunk in the file; saved in metadata of chunk
        line_step: int = self.__chunk_size - (self.__chunk_overlap // 2 + self.__chunk_overlap % 2)

        while current_line < len(content):
            chunk: str = ""

            for line_index in range(self.__chunk_size):
                if current_line + line_index >= len(content): return

                chunk += content[current_line + line_index]

            yield {
                "metadata": {
                    "filename": filename,
                    "chunk-index": chunk_index,
                },

                "chunk": chunk,
            }

            current_line += line_step
            chunk_index += 1


    def __chunk_text(self, filename: str, content: str):
        current_char: int = 0
        chunk_index: int = 0  # index of chunk in the file; saved in metadata of chunk
        char_step: int = self.__chunk_size - (self.__chunk_overlap // 2 + self.__chunk_overlap % 2)

        while current_char < len(content):
            if current_char + char_step >= len(content):
                chunk: str = content[current_char: -1]  # takes all chars left
            else:
                chunk: str = content[current_char : current_char + self.__chunk_size]  # takes __chunk_size chars

            yield {
                "metadata": {
                    "filename": filename,
                    "chunk-index": chunk_index,
                },

                "chunk": chunk,
            }

            current_char += char_step
            chunk_index += 1


    def chunk_repo(self, path):
        if not os.path.exists(path): return None

        for root, _, files in os.walk(path):
            for file in files:
                if not self.__is_file_allowed(file): continue

                try:
                    with open(os.path.join(root, file), "r", encoding=self.__file_encoding) as f:
                        if self.chunking_mode == ChunkingMode.LINES:
                            yield from self.__chunk_lines(file, f.readlines())
                        elif self.chunking_mode == ChunkingMode.CHARS:
                            yield from self.__chunk_text(file, f.read())

                except UnicodeDecodeError:
                    print(f"Unsupported encoding in file {os.path.join(root, file)}. Exiting program...")
                    exit(1)
