<!--
---
meta:
  title: "Publishing WhisperServe on RapidAPI"
  description: "Guide to publishing the WhisperServe Audio Transcription API on the RapidAPI marketplace."
  keywords: "RapidAPI, WhisperServe, audio transcription API, publish API, FastAPI, OpenAI Whisper"
  og:title: "Publishing WhisperServe on RapidAPI"
  og:description: "Step-by-step guide to publishing the WhisperServe Audio Transcription API on the RapidAPI marketplace."
  og:type: "article"
  og:url: "https://docs.whisperserve.com/docs/rapidapi"
  og:image: "https://docs.whisperserve.com/og-rapidapi.png"
  twitter:card: "summary"
  twitter:title: "Publishing WhisperServe on RapidAPI"
  twitter:description: "Step-by-step guide to publishing the WhisperServe Audio Transcription API on RapidAPI."
  twitter:url: "https://docs.whisperserve.com/docs/rapidapi"
  twitter:image: "https://docs.whisperserve.com/og-rapidapi.png"
---
-->

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "name": "Publishing WhisperServe on RapidAPI",
  "description": "Guide to publishing the WhisperServe Audio Transcription API on the RapidAPI marketplace.",
  "keywords": ["RapidAPI", "WhisperServe", "audio transcription API", "publish API", "FastAPI", "OpenAI Whisper"],
  "author": {
    "@type": "Organization",
    "name": "WhisperServe"
  },
  "url": "https://docs.whisperserve.com/docs/rapidapi",
  "sameAs": "https://github.com/puretechteam/whisperserve"
}
</script>

# Publishing WhisperServe on RapidAPI

This guide covers the steps to publish the WhisperServe Audio Transcription API on the RapidAPI marketplace.

## Prerequisites

- A RapidAPI account (sign up at https://rapidapi.com)
- The FastAPI app running and accessible at a public URL (or via a tunneling service like ngrok for testing)
- The OpenAPI specification file at `rapidapi/openapi.yaml` validated and complete

## Step 1: Validate the OpenAPI Spec

Before submitting, validate the OpenAPI specification to ensure it is well-formed and complete.

```bash
pip install openapi-spec-validator
python -c "
import yaml
from openapi_spec_validator import validate_spec
with open('rapidapi/openapi.yaml') as f:
    spec = yaml.safe_load(f)
validate_spec(spec)
print('OpenAPI spec is valid')
"
```

Fix any validation errors before proceeding.

## Step 2: Host the OpenAPI Definition

RapidAPI requires the OpenAPI spec to be accessible via a public URL. Options include:

- **GitHub raw URL**: Push the spec to the `rapidapi/openapi.yaml` path in the repository and use the raw GitHub URL.
- **RapidAPI dashboard**: Paste the spec directly into the RapidAPI editor.

The `rapidapi-config.json` references the GitHub raw URL:

```
https://raw.githubusercontent.com/puretechteam/whisperserve/main/rapidapi/openapi.yaml
```

Update this URL if the repository or branch differs.

## Step 3: Create the API on RapidAPI

1. Log in to https://rapidapi.com
2. Click **Create API** (or **Add API** from the dashboard)
3. Choose **Start from an OpenAPI Specification**
4. Either:
   - Paste the contents of `rapidapi/openapi.yaml` directly into the editor, or
   - Provide the URL to the hosted OpenAPI spec
5. Click **Import**

## Step 4: Configure API Details

On the API management page, set the following fields to match `rapidapi/rapidapi-config.json`:

| Field | Value |
|-------|-------|
| **API Name** | `WhisperServe Audio Transcription API` |
| **Category** | `Audio & Speech` |
| **Version** | `1.0.0` |
| **Description** | FastAPI-based audio transcription service powered by OpenAI Whisper |
| **Type** | HTTP |
| **Protocol** | HTTPS (production) / HTTP (development) |
| **Base URL** | `https://api.whisperserve.example.com` (production) |

## Step 5: Configure Authentication

1. Go to the **Authentication** tab in the RapidAPI dashboard
2. Set the auth type to **API Key**
3. Configure:
   - **Key name**: `Authorization`
   - **Key location**: `Header`
   - **Prefix**: `Bearer`
4. Save the configuration

## Step 6: Add Endpoints

RapidAPI auto-discovers endpoints from the OpenAPI spec. Verify that all 10 endpoints are listed:

| Method | Endpoint | Auth Required |
|--------|----------|---------------|
| GET | `/health` | No |
| POST | `/v1/inference` | Yes |
| POST | `/v1/inference/batch` | Yes |
| POST | `/v1/self-serve/signup` | No |
| GET | `/v1/self-serve/dashboard` | Yes |
| GET | `/v1/self-serve/analytics` | Yes |
| GET | `/v1/self-serve/api-keys` | Yes |
| DELETE | `/v1/self-serve/api-keys/{key_id}` | Yes |
| POST | `/v1/billing/generate-invoices` | No |
| POST | `/v1/webhooks` | No |

For each endpoint, verify:
- The summary and description are accurate
- Request parameters (query, path, body) are correctly mapped
- Response schemas match the actual API responses
- Status codes are documented

## Step 7: Set Up Pricing and Plans

1. Go to the **Pricing** tab
2. Configure the pricing tiers to match the API's usage model:
   - **Free**: 100 calls/day
   - **Pay-as-you-go**: Usage-based billing via Stripe
   - **Enterprise**: Custom pricing
3. Set the pricing currency to USD

## Step 8: Test the API

1. Use the **Test** tab in the RapidAPI dashboard to send requests to each endpoint
2. Verify responses match the OpenAPI spec
3. Test authentication by sending requests with and without a valid `Authorization: Bearer <api_key>` header

## Step 9: Submit for Review

1. Ensure all required fields are filled in (description, terms of service, contact info)
2. Add the API to a **RapidAPI Hub** or keep it private until ready
3. Click **Submit for Review** (if publishing publicly)
4. Wait for RapidAPI team approval

## Step 10: Post-Publication

- Monitor API usage and error rates via the RapidAPI dashboard
- Update the OpenAPI spec when adding new endpoints or changing existing ones
- Re-validate the spec after each update
- Keep the `rapidapi-config.json` in sync with any configuration changes

## Useful Links

- **RapidAPI Publisher Docs**: https://rapidapi.com/docs/api-glossary/api-definition/
- **OpenAPI 3.0 Specification**: https://spec.openapis.org/oas/v3.0.3
- **Project Repository**: https://github.com/puretechteam/whisperserve