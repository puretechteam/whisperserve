<!--
Sitemap configuration for the WhisperServe documentation site.
This file defines the pages and their SEO metadata for search engine crawlers.
-->

# Sitemap — WhisperServe Documentation

<!--
Format: Each entry represents a documentation page with its SEO metadata.
Search engines use sitemaps to discover and index pages efficiently.
-->

## Pages

| Priority | Change Frequency | Page | URL |
|----------|-----------------|------|-----|
| 1.0 | daily | Documentation Home | `/docs/index.md` |
| 0.9 | weekly | Quick Start Guide | `/docs/quickstart.md` |
| 0.9 | weekly | API Reference | `/docs/api_reference.md` |

## Sitemap XML (for deployment)

When deployed, the following XML sitemap should be served at `/sitemap.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://docs.whisperserve.com/</loc>
    <lastmod>2026-07-27</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://docs.whisperserve.com/quickstart</loc>
    <lastmod>2026-07-27</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
  <url>
    <loc>https://docs.whisperserve.com/api-reference</loc>
    <lastmod>2026-07-27</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>
</urlset>
```

## robots.txt

The following `robots.txt` configuration should be placed at the site root to guide crawlers:

```
User-agent: *
Allow: /docs/
Disallow: /

Sitemap: https://docs.whisperserve.com/sitemap.xml
```

## SEO Metadata Summary

| Page | Meta Description | Keywords |
|------|-----------------|----------|
| Home | WhisperServe is a FastAPI-based audio transcription service powered by OpenAI Whisper. Transcribe audio files to text via REST API or Python SDK. | audio transcription, WhisperServe, speech-to-text, FastAPI transcription, audio to text, speech recognition API |
| Quick Start | Quick start guide for the WhisperServe Audio Transcription API. Set up your API key, transcribe audio files, and use the Python SDK in minutes. | audio transcription, WhisperServe, speech-to-text, FastAPI transcription, audio to text, speech recognition API, Whisper quick start |
| API Reference | Complete API reference for the WhisperServe Audio Transcription API. Details all endpoints including inference, self-serve, health, and billing. | transcription API reference, WhisperServe endpoints, speech-to-text API, audio transcription endpoint, FastAPI API docs |