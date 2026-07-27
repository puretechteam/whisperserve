import os
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Depends, Request, Query
from fastapi.responses import JSONResponse, Response
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from app.batch import router as batch_router
from app.auth.api_key import get_api_key, get_api_key_tier, get_daily_usage_count
from app.logging.usage import log_usage
from app.middleware.rate_limit import RateLimitMiddleware
from app.models.inference import InferenceEngine
from app.models.cache import get_cached_result, cache_result, get_cache_key
from app.self_serve import router as self_serve_router
from app.billing.stripe import BillingService
from app.billing.invoices import generate_invoices_for_all_active

load_dotenv()

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN", ""),
        integrations=[
            FastApiIntegration(),
            LoggingIntegration(),
        ],
        traces_sample_rate=os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1"),
        environment=os.getenv("ENVIRONMENT", "development"),
    )
    app.state.models = {}
    app.state.billing = BillingService()
    yield
    app.state.models = None
    app.state.billing = None


app = FastAPI(lifespan=lifespan)

app.add_middleware(RateLimitMiddleware)

app.include_router(batch_router, prefix="/v1")
app.include_router(self_serve_router, prefix="/v1")


def _get_engine(app: FastAPI, model_name: str) -> InferenceEngine:
    if model_name not in app.state.models:
        app.state.models[model_name] = InferenceEngine(model_name)
    return app.state.models[model_name]


@app.get("/health")
async def health():
    return JSONResponse(content={"status": "ok"})


@app.get("/sitemap.xml")
async def sitemap():
    sitemap_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sitemap.xml")
    with open(sitemap_path, "r") as f:
        content = f.read()
    return Response(content=content, media_type="application/xml")


@app.get("/robots.txt")
async def robots():
    robots_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "robots.txt")
    with open(robots_path, "r") as f:
        content = f.read()
    return Response(content=content, media_type="text/plain")


@app.post("/v1/inference")
async def inference(
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key),
    model: str = Query(None),
):
    model_name = model or os.getenv("MODEL_NAME", "base")
    start_time = time.monotonic()
    tier = get_api_key_tier(api_key)
    if tier == "free":
        daily_count = get_daily_usage_count(api_key)
        if daily_count >= 100:
            latency_ms = int((time.monotonic() - start_time) * 1000)
            log_usage(
                api_key=api_key,
                model=model_name,
                duration_ms=0,
                input_size_bytes=0,
                latency_ms=latency_ms,
                status_code=429,
            )
            return JSONResponse(
                status_code=429,
                content={"error": "Free tier limit reached: 100 calls/day"},
            )
    elif tier == "pay-as-you-go":
        daily_count = get_daily_usage_count(api_key)
        if daily_count >= 10000:
            latency_ms = int((time.monotonic() - start_time) * 1000)
            log_usage(
                api_key=api_key,
                model=model_name,
                duration_ms=0,
                input_size_bytes=0,
                latency_ms=latency_ms,
                status_code=429,
            )
            return JSONResponse(
                status_code=429,
                content={"error": "Pro tier limit reached: 10000 calls/day"},
            )
    logging.info("Inference request received for file=%s model=%s", file.filename, model_name)
    engine = _get_engine(app, model_name)
    content = await file.read()
    logging.info("Read %d bytes from file=%s", len(content), file.filename)

    try:
        cache_key = get_cache_key(content, model_name)
        cached = get_cached_result(cache_key)
        if cached is not None:
            latency_ms = int((time.monotonic() - start_time) * 1000)
            log_usage(
                api_key=api_key,
                model=model_name,
                duration_ms=0,
                input_size_bytes=len(content),
                latency_ms=latency_ms,
                status_code=200,
            )
            return JSONResponse(content={"transcription": cached["text"], "cached": True})

        result = engine.transcribe(content)
        if tier == "pay-as-you-go":
            billing = app.state.billing
            billing.record_usage(api_key, 1)
        cache_result(cache_key, result)
        latency_ms = int((time.monotonic() - start_time) * 1000)

        log_usage(
            api_key=api_key,
            model=model_name,
            duration_ms=result.get("duration", 0),
            input_size_bytes=len(content),
            latency_ms=latency_ms,
            status_code=200,
        )

        return JSONResponse(content={"transcription": result["text"], "cached": False})
    except Exception as e:
        latency_ms = int((time.monotonic() - start_time) * 1000)
        logging.exception("Inference failed for file=%s", file.filename)
        with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "error.log"), "a") as f:
            f.write(str(e) + "\n")
        log_usage(
            api_key=api_key,
            model=model_name,
            duration_ms=0,
            input_size_bytes=len(content),
            latency_ms=latency_ms,
            status_code=500,
        )
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.post("/v1/webhooks")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature", "")
    billing = app.state.billing
    result = billing.handle_webhook(payload, sig_header)
    if result is None:
        return JSONResponse(status_code=400, content={"error": "Invalid signature"})
    billing.process_webhook_event(result["type"], result["data"])
    return JSONResponse(content={"received": True})


@app.post("/v1/billing/generate-invoices")
async def generate_invoices():
    results = generate_invoices_for_all_active()
    return JSONResponse(content={"generated": len(results), "invoices": results})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    sentry_sdk.capture_exception(exc)
    logging.exception("Unhandled exception for %s", request.url.path)
    return JSONResponse(status_code=500, content={"error": "Internal server error"})