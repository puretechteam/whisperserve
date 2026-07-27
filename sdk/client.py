import concurrent.futures
import time
import httpx
from typing import Optional


class InferenceError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class InferenceClient:
    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        timeout: float = 30.0,
    ):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._client = httpx.Client(
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )

    def _request_with_retry(
        self,
        method: str,
        url: str,
        *,
        max_retries: int = 3,
        **kwargs,
    ):
        delay = 1.0
        last_exception = None
        for attempt in range(max_retries + 1):
            try:
                response = self._client.request(method, url, **kwargs)
                return response
            except httpx.TransportError as e:
                last_exception = e
                if attempt < max_retries:
                    time.sleep(delay)
                    delay *= 2.0
                    continue
                raise
        raise last_exception  # type: ignore[misc]

    def transcribe(self, audio_path: str) -> dict:
        with open(audio_path, "rb") as f:
            response = self._request_with_retry(
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

    def transcribe_batch(self, audio_paths: list) -> list:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.transcribe, path) for path in audio_paths]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        return results

    def get_usage(self) -> dict:
        response = self._request_with_retry(
            "GET",
            f"{self._base_url}/v1/self-serve/dashboard",
        )
        if response.status_code != 200:
            raise InferenceError(
                response.json().get("detail", "Failed to fetch usage"),
                status_code=response.status_code,
            )
        return response.json()

    def list_keys(self) -> list:
        response = self._request_with_retry(
            "GET",
            f"{self._base_url}/v1/self-serve/api-keys",
        )
        if response.status_code != 200:
            raise InferenceError(
                response.json().get("detail", "Failed to list API keys"),
                status_code=response.status_code,
            )
        return response.json()

    def revoke_key(self, key_id: int) -> bool:
        response = self._request_with_retry(
            "DELETE",
            f"{self._base_url}/v1/self-serve/api-keys/{key_id}",
        )
        if response.status_code != 200:
            raise InferenceError(
                response.json().get("detail", "Failed to revoke API key"),
                status_code=response.status_code,
            )
        return True

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()