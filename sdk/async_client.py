import asyncio
import httpx
from typing import Optional

from .client import InferenceError


class AsyncInferenceClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        timeout: float = 30.0,
    ):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        self._client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self._api_key}"},
            timeout=self._timeout,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                headers={"Authorization": f"Bearer {self._api_key}"},
                timeout=self._timeout,
            )
        return self._client

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        *,
        max_retries: int = 3,
        **kwargs,
    ):
        await self._get_client()
        delay = 1.0
        last_exception = None
        for attempt in range(max_retries + 1):
            try:
                response = await self._client.request(method, url, **kwargs)
                return response
            except httpx.TransportError as e:
                last_exception = e
                if attempt < max_retries:
                    await asyncio.sleep(delay)
                    delay *= 2.0
                    continue
                raise
        raise last_exception  # type: ignore[misc]

    async def transcribe(self, audio_path: str) -> dict:
        with open(audio_path, "rb") as f:
            response = await self._request_with_retry(
                "POST",
                f"{self._base_url}/v1/inference",
                files={"file": f},
            )
        if response.status_code != 200:
            raise InferenceError(
                response.json().get("detail", "Inference failed"),
                status_code=response.status_code,
            )
        return response.json()

    async def transcribe_batch(self, audio_paths: list) -> list:
        tasks = [self.transcribe(path) for path in audio_paths]
        return await asyncio.gather(*tasks)

    async def get_usage(self) -> dict:
        response = await self._request_with_retry(
            "GET",
            f"{self._base_url}/v1/self-serve/dashboard",
        )
        if response.status_code != 200:
            raise InferenceError(
                response.json().get("detail", "Failed to fetch usage"),
                status_code=response.status_code,
            )
        return response.json()

    async def list_keys(self) -> list:
        response = await self._request_with_retry(
            "GET",
            f"{self._base_url}/v1/self-serve/api-keys",
        )
        if response.status_code != 200:
            raise InferenceError(
                response.json().get("detail", "Failed to list API keys"),
                status_code=response.status_code,
            )
        return response.json()

    async def revoke_key(self, key_id: int) -> bool:
        response = await self._request_with_retry(
            "DELETE",
            f"{self._base_url}/v1/self-serve/api-keys/{key_id}",
        )
        if response.status_code != 200:
            raise InferenceError(
                response.json().get("detail", "Failed to revoke API key"),
                status_code=response.status_code,
            )
        return True

    async def close(self):
        if self._client is not None:
            await self._client.aclose()
            self._client = None