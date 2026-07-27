# WhisperServe SDK

Python SDK for interacting with the WhisperServe Audio Transcription API.

## Installation

```bash
pip install whisperserve-sdk
```

## Usage

### Synchronous Client

```python
from sdk import InferenceClient

client = InferenceClient(api_key="your-api-key")

result = client.transcribe("audio.wav")
print(result["transcription"])

usage = client.get_usage()
print(f"Total requests: {usage['total_requests']}")

client.close()
```

### Asynchronous Client

```python
import asyncio
from sdk import AsyncInferenceClient

async def main():
    async with AsyncInferenceClient(api_key="your-api-key") as client:
        result = await client.transcribe("audio.wav")
        print(result["transcription"])

asyncio.run(main())
```

### Error Handling

```python
from sdk import InferenceClient, InferenceError

client = InferenceClient(api_key="your-api-key")

try:
    result = client.transcribe("audio.wav")
except InferenceError as e:
    print(f"Error {e.status_code}: {e.message}")
```

### Context Manager

```python
from sdk import InferenceClient

with InferenceClient(api_key="your-api-key") as client:
    result = client.transcribe("audio.wav")
    print(result["transcription"])
```

## API Reference

### InferenceClient

| Method | Description |
|--------|-------------|
| `transcribe(audio_path)` | Transcribe an audio file |
| `transcribe_batch(audio_paths)` | Transcribe multiple audio files |
| `get_usage()` | Get usage statistics |
| `list_keys()` | List API keys |
| `revoke_key(key_id)` | Revoke an API key |
| `close()` | Close the HTTP client |

### AsyncInferenceClient

Same methods as `InferenceClient`, but async versions (prefixed with `async`). Supports `async with` context manager.

### InferenceError

Exception raised when API requests fail. Contains `message` and `status_code` attributes.

## License

MIT License.