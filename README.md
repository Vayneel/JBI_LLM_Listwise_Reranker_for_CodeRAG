# Code Repository RAG System

This repository contains a Retrieval-Augmented Generation (RAG) system designed to index and query code repositories. The system enables natural language querying over code repositories to find relevant files.

## Overview

This RAG system indexes GitHub code repositories and allows users to ask questions about the codebase in natural language. The system tries to retrieve relevant files that answer the query.

Key features:
- Supports two different vector databases (FAISS and Chroma)
- Customizable chunking strategies

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Vayneel/JBI_LLM_Listwise_Reranker_for_CodeRAG.git
cd JBI_LLM_Listwise_Reranker_for_CodeRAG
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

To index a repository and start querying:

### Command Line Arguments

The system supports various command line arguments:

- `--debug`: Enable debug mode for verbose logging
- `--reset-db`: Reset of the database
- `--skip-cloning`: Skip repository cloning if local repository exists
- `--skip-indexing`: Skip indexing if database already exists
- `--print-record-count`: Print the number of records in the database after indexing phase
- `--faiss`: Use FAISS as the vector database
- `--chroma`: Use Chroma as the vector database (default)
- `--built-in-embeddings`: Use Chroma's built-in embeddings (only works with Chroma)

Example:
```bash
python tester.py --reset-db --chroma --built-in-embeddings --debug
```

## Configuration

The system can be configured by modifying parameters in `pipeline.py`:

```python
chunking_mode: ChunkingMode = ChunkingMode.LINES  # LINES or CHARS
chunk_size: int = 720  # Size of chunks (only for CHARS chunking mode)
chunk_overlap: int = 240  # Overlap between chunks (only for CHARS chunking mode)
chunk_all_files: bool = True  # Index all files or filter by extension (alter extensions in chunker.py)
```

## Architecture

The system consists of several components:

1. **Repository Management**: Handles cloning GitHub repositories
2. **Chunker**: Splits files into manageable chunks for indexing
3. **Embedder**: Converts text chunks into vector embeddings
4. **Vector Databases**: 
   - FAISS: Efficient similarity search
   - Chroma: Vector database with metadata storage
5. **Querying**: Processes user queries and tries to retrieve relevant files

### Component Details

#### Chunking Strategies

The system supports two chunking modes:
- `ChunkingMode.LINES`: Splits text by line count (preferred for better chunking)
- `ChunkingMode.CHARS`: Splits text by character count

#### Vector Databases

- **FAISS**: Fast for large datasets
- **Chroma**: Better for persistent storage and richer metadata

## Evaluation

The system includes an evaluation framework that compares expected files with retrieved files using predefined test cases.

To run the evaluation:

```bash
python tester.py
```

This will test the system against queries in `test_inputs.json` and report the amount of retrieved files mathing expected files divided by expected files count for each query.

### Sample Test Output

```
Query: How does the application handle screen mirroring?
Expected files: ['src/components/Mirror.vue', 'src/utils/adb.js']
Retrieved files: ['src/components/Mirror.vue', 'src/utils/adb.js', 'src/components/Settings.vue', 'src/pages/Home.vue']
Match score: 1.00
```
(My actual results are at 0 score, due to bad implementation)

## Improving RAG Quality

To enhance the retrieval quality, I had better used techniques like Query Expansion and Reranking, but I did nothing due to lack of skill and time.