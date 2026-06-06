# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Commands

### Docker (full stack)
```bash
docker compose up --build          # Build + start all services (postgres, backend, frontend)
docker compose up -d postgres      # Start only database
docker compose down                # Stop all services
docker compose down -v             # Stop + delete database volume
```

### Backend (local without Docker)
```bash
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env         # Fill in GROQ_API_KEY at minimum
uvicorn app.main:app --reload --port 8000
```

### Database migrations (Alembic)
```bash
cd backend
alembic revision --autogenerate -m "description"   # Generate migration from model changes
alembic upgrade head                                # Apply all pending migrations
alembic downgrade -1                                # Roll back last migration
```

### Scripts
```bash
cd backend
python scripts/reseed_db.py        # Rebuild seed data
python scripts/run_scrapers.py     # Execute all scrapers once
python scripts/seed_rich_data.py   # Load rich data into DB
```

## Architecture

### Agentic RAG Chat Flow (primary path)

The chat endpoint (`POST /api/v1/chat`) uses an **Agentic RAG** pattern via Groq/OpenAI tool calling:

1. `AgenticRAGService.run()` receives user message + conversation history
2. `build_messages()` constructs the message list with system prompt (Turkish city assistant persona with anti-hallucination rules)
3. `create_tool_completion()` sends messages + `TOOL_DEFINITIONS` to the LLM (OpenAI primary, Groq fallback)
4. The LLM decides which tool(s) to call — up to `AGENT_MAX_TOOL_ROUNDS` rounds
5. `_execute_tool_call()` dispatches to the matching function in `TOOL_FUNCTIONS` (13 tools in `agent/tools.py`)
6. Tool results are fed back as `role: tool` messages; LLM produces final answer
7. Response includes `intent`, `search_method` (sql/rag/hybrid), `confidence`, and `sources`

**Key files:** `agent/service.py`, `agent/prompt.py`, `agent/definitions.py`, `agent/tools.py`, `llm.py`

### Retrieval Strategies (three tiers)

- **SQL Only** — Direct queries on structured tables (pharmacies, weather, currency, earthquakes, fuel, gold, prayer times)
- **RAG Only** — pgvector similarity search via `search_similar_chunks()` in `services/rag.py` (city knowledge, history, geography)
- **Hybrid** — Both SQL keyword search + pgvector RAG, combined results (news, events, places, announcements, projects, jobs, outages)

The `search_similar_chunks()` pipeline: query expansion (Turkish synonyms + stopword removal) → parallel vector `<=>` + lexical `ts_rank_cd` retrieval → fusion scoring (0.70 vector / 0.30 lexical) → source-type boost → overlap rerank → top-K.

### LLM Provider Architecture

`services/llm.py` manages two providers with lazy initialization and automatic fallback:
- **Primary:** OpenAI (`gpt-4o-mini`) — requires `OPENAI_API_KEY`
- **Secondary:** Groq (`llama-3.3-70b-versatile`) — requires `GROQ_API_KEY`

Both `generate_chat_response()` and `create_tool_completion()` share `_call_with_fallback()` which iterates providers, retries each up to `LLM_MAX_RETRIES` times with exponential backoff, then falls through to the next provider.

### Database Models and pgvector

All models inherit from `Base` in `database.py`. `async_session` uses `expire_on_commit=False`. The `get_db` dependency auto-commits on success and rolls back on exception.

`DocumentChunk` (in `models/city.py`) is the pgvector table — only created if the `pgvector` Python package is importable (`HAS_PGVECTOR` / `HAS_VECTOR` flags in `rag.py` and `chunk_indexer.py`). `DocumentChunk = None` if pgvector is unavailable; all dependent code checks this flag before operating.

**Important:** `DocumentChunk.created_at` is `TIMESTAMP WITHOUT TIME ZONE`. When writing to this column, use naive datetimes (e.g., `datetime.now(timezone.utc).replace(tzinfo=None)`).

### Chunk Indexing Pipeline

`services/chunk_indexer.py` contains `SOURCE_CONFIGS` — a dict mapping each `source_type` string to its model, text builder, metadata builder, and active filter. `sync_all_document_chunks()` iterates source types, fetches active rows, hashes content to detect changes, re-embeds only changed chunks, and cleans up stale rows. Called by scheduler jobs and seed data loader.

### Scraper Scheduler

`services/scheduler.py` registers 9 APScheduler jobs at varying intervals (15min to 7 days). Each job creates its own `async_session`. Startup background jobs also fire via `asyncio.create_task()` in `main.py:lifespan`.

### Rate Limiting Caveat

SlowAPI's `@limiter.limit()` decorator **requires** the endpoint function to accept a `request: Request` parameter (it extracts the client IP from it). Omitting this causes `Exception: No "request" or "websocket" argument`.

### Configuration

`core/config.py` uses `pydantic-settings` with `SettingsConfigDict(env_file=".env", case_sensitive=True)`. The `async_database_url` property automatically converts `postgresql://` → `postgresql+asyncpg://`. All settings have defaults; only `GROQ_API_KEY` and `COLLECTAPI_KEY` must be set explicitly.

### Auth

`core/auth.py` provides `verify_api_key` FastAPI dependency checking `X-API-Key` header. Controlled by `AUTH_ENABLED` (default: `True`). Set `AUTH_ENABLED=false` in development to bypass.

### Key Conventions

- All endpoints use async SQLAlchemy with `AsyncSession = Depends(get_db)`
- Turkish language throughout — code comments, log messages, LLM prompts, and user-facing strings
- Background jobs must catch all exceptions (a single job failure must not affect others)
- Services that refresh external data use **insert-before-delete** or **scoped delete** to prevent empty-read race conditions
- The embedding model (`multilingual-e5-small`, 384-dim) loads lazily with a thread lock and cooldown period on failure
- `query:` and `passage:` prefixes are required for the e5 embedding model
