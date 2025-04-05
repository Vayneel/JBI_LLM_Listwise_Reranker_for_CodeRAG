import os
from enum import Enum
from charset_normalizer import from_path

from embedder import Embedder


class ChunkingMode(Enum):
    LINES = 'l'
    CHARS = 'c'


class Chunker:
    """
    Class for chunking documents.
    """

    __chunk_size: int  # lines to chunk
    __chunk_overlap: int  # how many lines will overlap for each chunk
    __chunk_all_files: bool  # used in __extract_allowed_files method
    __file_encoding: str
    __embedder: Embedder
    __debug: bool

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


    def __init__(self, chunking_mode: ChunkingMode, chunk_size: int, chunk_overlap: int, embedder: Embedder,
                 chunk_all_files: bool = False, encoding: str = None, debug: bool = False) -> None:
        self.chunking_mode: ChunkingMode = chunking_mode
        self.__chunk_size = chunk_size
        self.__chunk_overlap = chunk_overlap
        self.__chunk_all_files = chunk_all_files
        self.__file_encoding = encoding.upper()
        self.__embedder = embedder
        self.__debug = debug

        if chunk_size < self.__chunk_overlap + 1: self.__chunk_size = self.__chunk_overlap + 1


    def __is_file_allowed(self, file: str) -> bool:
        # todo allow every file
        if self.__chunk_all_files: return True

        allowed_extensions = (
            ".py",
            ".java",
            ".js",
            ".html",
            ".css",
            ".xml"
            ".c", ".h", ".cpp", ".cs",
            ".md", ".txt", ".json"
            ".sh",
            ".kt", ".kts", "ktm",
            ".gradle"
        )

        if file.endswith(allowed_extensions):
            return True

        return False


    def __chunk_lines(self, filename: str, content: list[str]):
        current_line: int = 0
        chunk_index: int = 0  # index of chunk in the file; saved in metadata of chunk

        while current_line < len(content):
            chunk: str = f"{filename}\n"
            line_step: int = 0

            while self.__embedder.get_token_usage(chunk) < 512:
                if current_line + line_step + 1 >= len(content): break
                chunk += content[current_line + line_step].rstrip()
                line_step += 1

            yield {
                "metadata": {
                    "filename": filename,
                    "chunk-index": chunk_index,
                },

                "chunk": chunk,
            }

            current_line += max(int(line_step * 0.8), 4)
            chunk_index += 1


    def __chunk_text(self, filename: str, content: str):
        current_char: int = 0
        chunk_index: int = 0  # index of chunk in the file; saved in metadata of chunk
        char_step: int = self.__chunk_size - (self.__chunk_overlap // 2 + self.__chunk_overlap % 2)

        chunk: str = f"{filename}\n"

        while current_char < len(content):
            if current_char + char_step >= len(content):
                chunk += content[current_char: -1]  # takes all chars left
            else:
                chunk += content[current_char : current_char + self.__chunk_size]  # takes __chunk_size chars

            yield {
                "metadata": {
                    "filename": filename,
                    "chunk-index": chunk_index,
                },

                "chunk": chunk,
            }

            current_char += char_step
            chunk_index += 1


    def __yield_chunks(self, root: str, filename: str, encoding: str):
        file = os.path.join(root, filename)
        with open(file, "r", encoding=encoding) as f:
            if self.chunking_mode == ChunkingMode.LINES:
                yield from self.__chunk_lines(file, f.readlines())
            elif self.chunking_mode == ChunkingMode.CHARS:
                yield from self.__chunk_text(file, f.read())


    def __try_with_another_encoding(self, root: str, file: str):
        result = from_path(os.path.join(root, file)).best()
        if result is None or result.encoding == self.__file_encoding: return

        try:
            yield from self.__yield_chunks(root, file, result.encoding)

        except (UnicodeDecodeError, UnicodeError) as e:
            print(f"Encoding-related error in file {os.path.join(root, file)}. Exiting program...")
            print(f"\n[ERROR OUTPUT]\n{e}")
            exit(1)



    def chunk_repo(self, path):
        if not os.path.exists(path): return None

        for root, _, files in os.walk(path):
            for file in files:
                if not self.__is_file_allowed(file): continue
                if self.__debug: print(f"chunking file {os.path.join(root, file)}")

                try:
                    yield from self.__yield_chunks(root, file, self.__file_encoding)

                except (UnicodeDecodeError, UnicodeError) as e:
                    results = self.__try_with_another_encoding(root, file)
                    if results is not None:
                        yield from results
