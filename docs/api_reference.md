<!--
---
meta:
  description: "Complete API reference for the WhisperServe Audio Transcription API. Details all endpoints including inference, self-serve, health, and billing."
  keywords: "transcription API reference, WhisperServe endpoints, speech-to-text API, audio transcription endpoint, FastAPI API docs"
  og:title: "WhisperServe API Reference"
  og:description: "Full API reference for the WhisperServe Audio Transcription API with endpoint details, request/response schemas, and error codes."
  og:type: "article"
  og:url: "https://docs.whisperserve.com/docs/api-reference"
  og:image: "https://docs.whisperserve.com/og-api-reference.png"
  twitter:card: "summary"
  twitter:title: "WhisperServe API Reference"
  twitter:description: "Full API reference for the WhisperServe Audio Transcription API with endpoint details, request/response schemas, and error codes."
---
-->

# API Reference

<!--
Structured Data (JSON-LD) for the API Reference documentation page.
-->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "name": "WhisperServe Audio Transcription API Reference",
  "description": "Complete API reference for the WhisperServe Audio Transcription API. Details all endpoints including inference, self-serve, health, and billing.",
  "keywords": ["transcription API reference", "WhisperServe endpoints", "speech-to-text API", "audio transcription endpoint", "FastAPI API docs"],
  "author": {
    "@type": "Organization",
    "name": "WhisperServe"
  },
  "url": "https://docs.whisperserve.com/api-reference",
  "sameAs": "https://github.com/puretechteam/whisperserve"
}
</script>

<!--
Semantic HTML structure hints:
- <article> wraps the full API reference
- <section> groups related endpoints
- <h1> is the page title; <h2> are major sections; <h3> are individual endpoints
- <dl>, <dt>, <dd> can be used for endpoint parameter definitions
- <table> is appropriate for response schemas and error code listings
-->

## Base URL

All endpoints are served from the following base URL:

```
http://localhost:8000
```

## Authentication

All endpoints (except `/health` and `/self-serve/signup`) require an API key in the `Authorization` header:

```
Authorization: Bearer <api_key>
```

## Endpoints

### POST /v1/inference

<!--
Schema.org markup for the inference endpoint.
-->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "EntryPoint",
  "name": "Transcribe Audio",
  "description": "Transcribe an audio file using OpenAI Whisper speech-to-text model.",
  "url": "http://localhost:8000/v1/inference",
  "httpMethod": "POST",
  "encodingType": "multipart/form-data",
  "contentType": "multipart/form-data",
  "expectsAccept": "application/json",
  "returns": "application/json",
  "parameter": [
    {
      "@type": "PropertyValue",
      "name": "file",
      "description": "Audio file to transcribe (wav, mp3, m4a, etc.)",
      "required": true,
      "encoding": "multipart/form-data"
    },
    {
      "@type": "PropertyValue",
      "name": "Authorization",
      "description": "Bearer token API key",
      "required": true,
      "encoding": "header"
    },
    {
      "@type": "PropertyValue",
      "name": "model",
      "description": "Optional Whisper model name (defaults to base)",
      "required": false,
      "encoding": "query"
    }
  ]
}
</script>

Transcribe an audio file. The API uses OpenAI Whisper for speech-to-text conversion and supports caching of previously transcribed content.

**Headers:**
- `Authorization: Bearer <api_key>` (required)

**Body:** `multipart/form-data`
- `file` (required) — Audio file (wav, mp3, m4a, etc.)

**Response (200):**
```json
{
  "transcription": "Hello world",
  "cached": false
}
```

**Errors:**
- `401` — Invalid or missing API key
- `429` — Rate limit exceeded (free tier: 100 calls/day)
- `400` — Invalid audio file

---

### GET /health

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "EntryPoint",
  "name": "Health Check",
  "description": "Check the health status of the WhisperServe transcription API.",
  "url": "http://localhost:8000/health",
  "httpMethod": "GET",
  "expectsAccept": "application/json",
  "returns": "application/json"
}
</script>

Health check endpoint. Returns `ok` when the service is running.

**Response (200):**
```json
{"status": "ok"}
```

---

### POST /v1/self-serve/signup

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "EntryPoint",
  "name": "Sign Up",
  "description": "Create a new account and receive an API key for the WhisperServe transcription service.",
  "url": "http://localhost:8000/v1/self-serve/signup",
  "httpMethod": "POST",
  "encodingType": "application/json",
  "contentType": "application/json",
  "expectsAccept": "application/json",
  "returns": "application/json",
  "parameter": [
    {
      "@type": "PropertyValue",
      "name": "email",
      "description": "User email address for account creation",
      "required": true,
      "encoding": "body"
    }
  ]
}
</script>

Create a new account and API key.

**Headers:**
- `Content-Type: application/json`

**Body:**
```json
{"email": "user@example.com"}
```

**Response (200):**
```json
{"api_key": "ak_abc123...", "user_id": "user@example.com"}
```

---

### GET /v1/self-serve/dashboard

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "EntryPoint",
  "name": "Usage Dashboard",
  "description": "Retrieve usage statistics for the authenticated API key.",
  "url": "http://localhost:8000/v1/self-serve/dashboard",
  "httpMethod": "GET",
  "expectsAccept": "application/json",
  "returns": "application/json"
}
</script>

Get usage statistics for the authenticated API key.

**Headers:**
- `Authorization: Bearer <api_key>` (required)

**Response (200):**
```json
{
  "total_requests": 150,
  "total_duration_ms": 45000,
  "total_input_bytes": 10485760,
  "avg_duration_ms": 300,
  "period_days": 30
}
```

---

### GET /v1/self-serve/api-keys

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "EntryPoint",
  "name": "List API Keys",
  "description": "List all API keys associated with the authenticated user account.",
  "url": "http://localhost:8000/v1/self-serve/api-keys",
  "httpMethod": "GET",
  "expectsAccept": "application/json",
  "returns": "application/json"
}
</script>

List all API keys for the authenticated user.

**Headers:**
- `Authorization: Bearer <api_key>` (required)

**Response (200):**
```json
[
  {
    "id": 1,
    "api_key": "ak_abc123...",
    "created_at": "2026-07-26T12:00:00+00:00",
    "revoked": false
  }
]
```

---

### DELETE /v1/self-serve/api-keys/{key_id}

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "EntryPoint",
  "name": "Revoke API Key",
  "description": "Revoke an API key so it can no longer be used for authentication.",
  "url": "http://localhost:8000/v1/self-serve/api-keys/{key_id}",
  "httpMethod": "DELETE",
  "expectsAccept": "application/json",
  "returns": "application/json"
}
</script>

Revoke an API key.

**Headers:**
- `Authorization: Bearer <api_key>` (required)

**Response (200):**
```json
{"detail": "API key revoked"}
```

**Errors:**
- `401` — Invalid API key
- `404` — API key not found or not owned by user