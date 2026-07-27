# AGENTS.md — WhisperServe Project Conventions

This file extends the shared conventions in `C:\Users\Tanner\KiloProjects\AGENTS.md` with WhisperServe-specific rules.

## Project Overview

WhisperServe is a FastAPI-based audio transcription API powered by OpenAI Whisper, with Stripe billing, a Python SDK, and Docker deployment.

## Project-Specific Conventions

- **No comments in code** — code should be self-documenting; do not add inline or block comments.
- **JSONResponse for all errors** — use `JSONResponse(status_code=..., content={"error": ...})` for error responses, never plain text.
- **async/await patterns** — all route handlers are `async def`; use `await` for I/O operations.
- **Lifespan context manager** — use `@asynccontextmanager` for FastAPI lifespan to manage model loading and cleanup.
- **Error logging** — use `os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "error.log")` for error log paths; never hardcode absolute paths.
- **API key auth** — use `Depends(get_api_key)` for endpoint authentication; the `get_api_key` dependency validates Bearer tokens against the SQLite database.
- **Model caching** — `app.state.models` dict caches `InferenceEngine` instances by model name; use `_get_engine()` to access or create them.

## Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app, lifespan, inference endpoint |
| `app/batch.py` | Batch inference endpoint |
| `app/models/inference.py` | InferenceEngine wrapping Whisper model |
| `app/auth/api_key.py` | API key generation, validation, tier lookup |
| `app/billing/stripe.py` | Stripe billing integration |
| `sdk/` | Python SDK (package name: `whisperserve-sdk`) |
| `docker/Dockerfile` | Multi-stage Docker build |
| `docker/entrypoint.sh` | Entrypoint with RELOAD env var support |

## Naming

- Project name: **WhisperServe** (not 50kmmr, not Whisper API)
- SDK package: **whisperserve-sdk** (not whisper-api-sdk)
- GitHub repo: **puretechteam/whisperserve**