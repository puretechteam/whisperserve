# WhisperServe

A FastAPI-based audio transcription service powered by OpenAI Whisper. Upload audio files and receive text transcriptions via a REST API or the Python SDK.

## Quick Start

### Installation

```bash
pip install whisperserve-sdk
```

### Sign Up

Get your API key:

```bash
curl -X POST http://localhost:8000/v1/self-serve/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com"}'
```

Response:

```json
{"api_key": "ak_abc123...", "user_id": "your@email.com"}
```

### Transcribe Audio

```bash
curl -X POST http://localhost:8000/v1/inference \
  -H "Authorization: Bearer ak_abc123..." \
  -F "file=@audio.wav"
```

Response:

```json
{"transcription": "Hello world", "cached": false}
```

### Python SDK

```python
from whisperserve_sdk import InferenceClient

client = InferenceClient(api_key="ak_abc123...")

result = client.transcribe("audio.wav")
print(result["transcription"])

usage = client.get_usage()
print(f"Total requests: {usage['total_requests']}")

client.close()
```

### Pricing

| Tier | Price per Call | Daily Limit | Description |
|------|---------------|-------------|-------------|
| Free | $0.00 | 100 calls/day | Free tier — 100 calls per day |
| Pay-as-you-go | $0.10 | 10,000 calls/day | Pro tier — $0.10 per call, 10,000 calls per day |
| Enterprise | Custom | Unlimited | Enterprise tier — custom pricing, contact us |

### Error Handling

```python
from whisperserve_sdk import InferenceClient, InferenceError

client = InferenceClient(api_key="ak_abc123...")

try:
    result = client.transcribe("audio.wav")
except InferenceError as e:
    print(f"Error {e.status_code}: {e.message}")
```

## API Reference

Full API documentation is available in [docs/api_reference.md](docs/api_reference.md).

Key endpoints:

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/inference` | Transcribe an audio file |
| `GET` | `/health` | Health check |
| `POST` | `/v1/self-serve/signup` | Create an account and API key |
| `GET` | `/v1/self-serve/dashboard` | Get usage statistics |
| `GET` | `/v1/self-serve/api-keys` | List API keys |
| `DELETE` | `/v1/self-serve/api-keys/{key_id}` | Revoke an API key |

## SDK Installation

Install the SDK from PyPI:

```bash
pip install whisperserve-sdk
```

Or install locally in editable mode for development:

```bash
pip install -e ./sdk
```

The SDK provides the `InferenceClient` and `AsyncInferenceClient` classes for programmatic access to the transcription API, along with `InferenceError` for exception handling.

## Versioning

This project uses [Semantic Versioning (SemVer)](https://semver.org/). Version tags are automatically created on pushes to `master` based on commit messages.

## License

MIT License. See [LICENSE](LICENSE) for details.