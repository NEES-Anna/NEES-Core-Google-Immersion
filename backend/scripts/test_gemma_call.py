from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import httpx

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.config import Settings
from app.gemma_client import RETRY_DELAY_SECONDS, call_gemma_model, is_retryable_error, safe_exception_metadata


async def main() -> None:
    settings = Settings(_env_file=BACKEND_DIR / ".env")
    key_present = bool(settings.gemini_api_key)

    print(f"model: {settings.gemma_model}")
    print(f"key_present: {str(key_present).lower()}")
    print(f"attempted_models: {', '.join(settings.live_model_candidates)}")

    if not settings.gemini_api_key:
        print("success: false")
        print("error: GEMINI_API_KEY is not set")
        return

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": "Return exactly: OK"}],
            }
        ]
    }

    failed_models: list[dict[str, str | int]] = []
    async with httpx.AsyncClient(timeout=settings.gemma_timeout_seconds) as client:
        for model in settings.live_model_candidates:
            for attempt_number in range(1, 3):
                try:
                    text = await call_gemma_model(client, model, settings.gemini_api_key, payload)
                    print("success: true")
                    print(f"used_model: {model}")
                    print(f"fallback_used: {str(model != settings.gemma_model).lower()}")
                    print(f"response: {text}")
                    return
                except Exception as exc:
                    details = {"model": model, **safe_exception_metadata(exc, settings.gemini_api_key)}
                    failed_models.append(details)
                    print(f"failure_model: {model}")
                    print(f"failure_attempt: {attempt_number}")
                    print(f"error: {details.get('error')}")
                    if "error_status_code" in details:
                        print(f"status_code: {details['error_status_code']}")
                    print(f"error_message: {details.get('error_message', '')}")
                    if is_retryable_error(details) and attempt_number == 1:
                        await asyncio.sleep(RETRY_DELAY_SECONDS)
                        continue
                    break

    print("success: false")
    print(f"failed_models: {len(failed_models)}")


if __name__ == "__main__":
    asyncio.run(main())
