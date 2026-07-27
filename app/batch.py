import logging
import os
import time
from fastapi import APIRouter, Depends, File, UploadFile, Request, Query
from fastapi.responses import JSONResponse

from app.auth.api_key import get_api_key, get_api_key_tier, get_daily_usage_count
from app.logging.usage import log_usage
from app.models.cache import get_cached_result, cache_result, get_cache_key
from app.models.inference import InferenceEngine

router = APIRouter()


def _get_engine(request: Request, model_name: str) -> InferenceEngine:
    if model_name not in request.app.state.models:
        request.app.state.models[model_name] = InferenceEngine(model_name)
    return request.app.state.models[model_name]


@router.post("/inference/batch")
async def batch_inference(
    request: Request,
    files: list[UploadFile] = File(...),
    api_key: str = Depends(get_api_key),
    model: str = Query(None),
):
    model_name = model or os.getenv("MODEL_NAME", "base")
    start_time = time.monotonic()
    logging.info("Batch inference request received with %d files model=%s", len(files), model_name)
    engine = _get_engine(request, model_name)
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

    results = []
    for file in files:
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
                results.append({
                    "transcription": cached["text"],
                    "cached": True,
                    "filename": file.filename,
                })
                continue

            result = engine.transcribe(content)
            if tier == "pay-as-you-go":
                billing = request.app.state.billing
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

            results.append({
                "transcription": result["text"],
                "cached": False,
                "filename": file.filename,
            })
        except Exception as e:
            latency_ms = int((time.monotonic() - start_time) * 1000)
            logging.exception("Batch inference failed for file=%s", file.filename)
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
            results.append({
                "error": str(e),
                "filename": file.filename,
            })

    return JSONResponse(content={"results": results})