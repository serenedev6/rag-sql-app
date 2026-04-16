# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Fill in .env with OPENAI_API_KEY, SQL_SERVER, SQL_DATABASE, SQL_USERNAME, SQL_PASSWORD
```

Requires **ODBC Driver 17 for SQL Server** installed on the system.

## Running

```bash
# Demo mode (no SQL Server needed — uses dummy data)
python main.py --demo

# Real mode (requires .env configured with SQL Server credentials)
python main.py
```

Before running real mode, configure `main.py`:
- `TABLE_NAME` — the SQL table to query
- `TEXT_COLUMNS` — columns to embed as RAG content
- `METADATA_COLUMNS` — columns to store as metadata for filtering
- `REBUILD_VECTOR_STORE` — set `True` to regenerate embeddings from scratch

## Architecture

Two parallel approaches for natural language querying of SQL Server:

**Vector RAG pipeline** (`main.py` entry point):
1. `db_connector.py` — pyodbc connection to SQL Server; fetches data as DataFrames
2. `data_processor.py` — converts DataFrame rows to LangChain `Document` objects; each row becomes a text block (`col: value\n...`) with metadata; splits into chunks
3. `vector_store.py` — embeds documents via `text-embedding-3-small`, persists to ChromaDB at `./chroma_db/`; supports load/rebuild/append
4. `rag_chain.py` — `RetrievalQA` chain using `gpt-4o-mini`; retrieves top-k similar chunks and answers in Hindi/Hinglish using a custom prompt

**Text-to-SQL pipeline** (`text_to_sql.py`):
- LangChain SQL agent that converts natural language directly to SQL queries
- Best for numerical/aggregation queries; RAG pipeline is better for text/description searches

**When to use which:**
- Text, descriptions, comments → Vector RAG (`main.py`)
- Numbers, dates, counts, aggregations → Text-to-SQL (`text_to_sql.py`)

## Key implementation details

- ChromaDB persists to `./chroma_db/` locally; delete this directory or set `REBUILD_VECTOR_STORE = True` to force re-embedding
- The RAG prompt and LLM responses are in Hindi/Hinglish by design
- `db_connector.py` supports both SQL Server Authentication and Windows Authentication (`USE_WINDOWS_AUTH=yes` in `.env`)
- `fetch_table_data` uses `SELECT TOP {limit}` syntax (SQL Server specific, not `LIMIT`)
