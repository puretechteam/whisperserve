<!--
---
meta:
  description: "WhisperServe is a FastAPI-based audio transcription service powered by OpenAI Whisper. Transcribe audio files to text via REST API or Python SDK."
  keywords: "audio transcription, WhisperServe, speech-to-text, FastAPI transcription, audio to text, speech recognition API, transcription service, WhisperServe free"
  og:title: "WhisperServe"
  og:description: "FastAPI-based audio transcription service powered by OpenAI Whisper. Transcribe audio files to text via REST API or Python SDK."
  og:type: "website"
  og:url: "https://docs.whisperserve.com"
  og:image: "https://docs.whisperserve.com/og-image.png"
  twitter:card: "summary_large_image"
  twitter:title: "WhisperServe"
  twitter:description: "FastAPI-based audio transcription service powered by OpenAI Whisper. Transcribe audio files to text via REST API or Python SDK."
---
-->

# WhisperServe

<!--
Structured Data (JSON-LD) for the documentation landing page.
This markup enables search engines to display rich results for the API documentation.
-->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "WebAPI",
  "name": "WhisperServe Audio Transcription API",
  "description": "A FastAPI-based audio transcription service powered by OpenAI Whisper. Upload audio files and receive text transcriptions via a REST API or the Python SDK.",
  "url": "https://docs.whisperserve.com",
  "documentation": "https://docs.whisperserve.com",
  "sameAs": "https://github.com/puretechteam/whisperserve",
  "keywords": ["audio transcription", "WhisperServe", "speech-to-text", "FastAPI transcription", "audio to text", "speech recognition API", "transcription service"],
  "author": {
    "@type": "Organization",
    "name": "WhisperServe",
    "url": "https://github.com/puretechteam"
  },
  "provider": {
    "@type": "Organization",
    "name": "WhisperServe",
    "url": "https://github.com/puretechteam/whisperserve"
  },
  "applicationCategory": "DeveloperAPI",
  "operatingSystem": "Linux, macOS, Windows",
  "programmingLanguage": "Python",
  "requiresSubscription": false,
  "termsOfService": "https://github.com/puretechteam/whisperserve/blob/main/LICENSE"
}
</script>

<!--
Semantic HTML structure hints:
- <header> contains the page title and tagline
- <nav> contains the documentation navigation links
- <main> wraps the primary content area
- <section> groups related content blocks (overview, endpoints, SDK, etc.)
- <aside> can contain a sidebar with quick links
- <footer> contains copyright and repository links
-->

## Overview

**WhisperServe** is a FastAPI-based audio transcription service powered by OpenAI Whisper. Upload audio files and receive text transcriptions via a REST API or the Python SDK.

### Key Features

- **Speech-to-Text Transcription** — Convert audio files (wav, mp3, m4a) to text using OpenAI Whisper
- **Caching** — Previously transcribed content is cached for faster repeat requests
- **Python SDK** — Easy-to-use `InferenceClient` for programmatic access
- **Usage Dashboard** — Track request counts, duration, and input size per API key
- **API Key Management** — Create, list, and revoke API keys via self-serve endpoints

### Quick Links

| Documentation | Description |
|---------------|-------------|
| [Quick Start](quickstart.md) | Set up your API key and transcribe your first audio file |
| [API Reference](api_reference.md) | Full endpoint documentation with request/response schemas |

## Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/v1/inference` | Transcribe an audio file |
| `GET` | `/health` | Health check |
| `POST` | `/v1/self-serve/signup` | Create an account and API key |
| `GET` | `/v1/self-serve/dashboard` | Get usage statistics |
| `GET` | `/v1/self-serve/api-keys` | List API keys |
| `DELETE` | `/v1/self-serve/api-keys/{key_id}` | Revoke an API key |

## Getting Started

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Sign Up for an API Key

```bash
curl -X POST http://localhost:8000/v1/self-serve/signup \
  -H "Content-Type: application/json" \
  -d '{"email": "your@email.com"}'
```

### 3. Transcribe Audio

```bash
curl -X POST http://localhost:8000/v1/inference \
  -H "Authorization: Bearer ak_abc123..." \
  -F "file=@audio.wav"
```

### 4. Use the Python SDK

```python
from sdk import InferenceClient

client = InferenceClient(api_key="ak_abc123...")
result = client.transcribe("audio.wav")
print(result["transcription"])
client.close()
```

## Search Keywords

This documentation covers the following topics:

- Audio transcription API
- Whisper speech-to-text
- FastAPI transcription service
- Speech recognition API
- Audio to text conversion
- Python transcription SDK
- API key authentication
- Usage dashboard and analytics

## Repository

The source code is available on GitHub: [puretechteam/whisperserve](https://github.com/puretechteam/whisperserve)

## License

MIT License. See [LICENSE](https://github.com/puretechteam/whisperserve/blob/main/LICENSE) for details.