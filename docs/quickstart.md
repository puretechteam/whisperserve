<!--
---
meta:
  description: "Quick start guide for the WhisperServe. Set up your API key, transcribe audio files, and use the Python SDK in minutes."
  keywords: "audio transcription, WhisperServe, speech-to-text, FastAPI transcription, audio to text, speech recognition API, Whisper quick start"
  og:title: "WhisperServe — Quick Start"
  og:description: "Get started with the WhisperServe audio transcription API. Transcribe audio files via REST or Python SDK."
  og:type: "article"
  og:url: "https://docs.whisperserve.com/docs/quickstart"
  og:image: "https://docs.whisperserve.com/og-quickstart.png"
  twitter:card: "summary"
  twitter:title: "WhisperServe — Quick Start"
  twitter:description: "Get started with the WhisperServe audio transcription API. Transcribe audio files via REST or Python SDK."
---
-->

# Quick Start Guide

<!--
Structured Data (JSON-LD) for the Quick Start documentation page.
This markup helps search engines understand the API documentation context.
-->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "name": "WhisperServe Audio Transcription API — Quick Start",
  "description": "Quick start guide for the WhisperServe Audio Transcription API. Set up your API key, transcribe audio files, and use the Python SDK.",
  "keywords": ["audio transcription", "WhisperServe", "speech-to-text", "FastAPI transcription", "audio to text", "speech recognition API"],
  "author": {
    "@type": "Organization",
    "name": "WhisperServe"
  },
  "url": "https://docs.whisperserve.com/quickstart",
  "sameAs": "https://github.com/puretechteam/whisperserve"
}
</script>

<!--
Semantic HTML structure hints for rendering engines:
- <article> wraps the entire quickstart content
- <section> groups each logical section (Installation, Sign Up, Transcribe, SDK, Dashboard, Errors)
- <h1> is the page title; <h2> are section titles; <h3> are subsections
- <code> blocks represent inline and fenced code samples
- <nav> can wrap the table of contents if generated
-->

## Installation

Install the project dependencies using pip:

```bash
pip install -r requirements.txt
```

## Sign Up

Get your API key by creating an account:

```bash
curl -X POST http://localhost:8000/v1/self-serve/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com"}'
```

### Response

```json
{"api_key": "ak_abc123...", "user_id": "your@email.com"}
```

## Transcribe Audio

Send an audio file to the inference endpoint to receive a text transcription. The API uses OpenAI Whisper for speech-to-text conversion.

```bash
curl -X POST http://localhost:8000/v1/inference \
  -H "Authorization: Bearer ak_abc123..." \
  -F "file=@audio.wav"
```

### Response

```json
{"transcription": "Hello world", "cached": false}
```

## Python SDK

The `InferenceClient` SDK provides a programmatic interface for audio transcription.

```python
from sdk import InferenceClient

client = InferenceClient(api_key="ak_abc123...")

result = client.transcribe("audio.wav")
print(result["transcription"])

usage = client.get_usage()
print(f"Total requests: {usage['total_requests']}")

client.close()
```

### SDK Methods

| Method | Description |
|--------|-------------|
| `transcribe(path)` | Transcribe an audio file and return the result |
| `get_usage()` | Retrieve usage statistics for the API key |
| `close()` | Close the underlying HTTP session |

## Usage Dashboard

View your account usage and request statistics:

```bash
curl -X GET http://localhost:8000/v1/self-serve/dashboard \
  -H "Authorization: Bearer ak_abc123..."
```

## Error Handling

Handle transcription errors gracefully using the `InferenceError` exception:

```python
from sdk import InferenceClient, InferenceError

client = InferenceClient(api_key="ak_abc123...")

try:
    result = client.transcribe("audio.wav")
except InferenceError as e:
    print(f"Error {e.status_code}: {e.message}")
```

### Common Error Codes

| Status Code | Meaning |
|-------------|---------|
| `401` | Invalid or missing API key |
| `429` | Rate limit exceeded (free tier: 100 calls/day) |
| `400` | Invalid audio file format |
| `500` | Internal server error |