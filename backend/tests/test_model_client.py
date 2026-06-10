import httpx
import pytest

from app import model_client
from app.config import Settings


class FailingAsyncClient:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def post(self, *args, **kwargs):
        request = httpx.Request("POST", "https://example.test?key=super-secret")
        return httpx.Response(
            403,
            text='{"error":"API key super-secret is invalid"}',
            request=request,
        )


class CapturingAsyncClient:
    payloads = []

    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        return False

    async def post(self, *args, **kwargs):
        self.payloads.append(kwargs["json"])
        request = httpx.Request("POST", "https://example.test")
        return httpx.Response(
            200,
            json={"candidates": [{"content": {"parts": [{"text": "Final answer."}]}}]},
            request=request,
        )


@pytest.mark.anyio
async def test_generate_model_response_adds_safe_api_error_metadata(monkeypatch, capsys):
    monkeypatch.setattr(model_client.httpx, "AsyncClient", FailingAsyncClient)
    settings = Settings(
        _env_file=None,
        gemini_api_key="super-secret",
        gemma_model="gemma-test",
        gemma_fallback_models="gemma-fallback",
        mock_gemma_when_missing_key=True,
    )

    raw_response, metadata = await model_client.generate_model_response(
        "Summarize product feedback.",
        "general",
        settings,
    )

    assert "[MOCK MODEL CANDIDATE RESPONSE]" in raw_response
    assert metadata["provider"] == "mock_after_api_error"
    assert metadata["mock"] is True
    assert metadata["requested_model"] == "gemma-test"
    assert metadata["used_model"] == "gemma-test"
    assert metadata["attempted_models"] == ["gemma-test", "gemma-fallback"]
    assert len(metadata["failed_models"]) == 2
    assert metadata["failed_models"][0]["model"] == "gemma-test"
    assert metadata["failed_models"][1]["model"] == "gemma-fallback"
    assert metadata["error"] == "HTTPStatusError"
    assert metadata["error_status_code"] == 403
    assert metadata["error_message"]
    assert "super-secret" not in metadata["error_message"]

    console_output = capsys.readouterr().out
    assert "Model API call failed" in console_output
    assert "super-secret" not in console_output


def test_fallback_model_list_parses_safely():
    settings = Settings(
        _env_file=None,
        gemma_model="primary",
        gemma_fallback_models=" fallback-a, ,primary,fallback-b,fallback-a ",
    )

    assert settings.fallback_model_list == ["fallback-a", "fallback-b"]
    assert settings.live_model_candidates == ["primary", "fallback-a", "fallback-b"]


def test_cors_origin_list_accepts_comma_separated_deployed_frontends():
    settings = Settings(
        _env_file=None,
        cors_origins="https://app-one.vercel.app, https://demo.example.com,",
    )

    assert settings.cors_origin_list == [
        "https://app-one.vercel.app",
        "https://demo.example.com",
    ]


@pytest.mark.anyio
async def test_generate_model_response_sends_generation_config(monkeypatch):
    CapturingAsyncClient.payloads = []
    monkeypatch.setattr(model_client.httpx, "AsyncClient", CapturingAsyncClient)
    settings = Settings(
        _env_file=None,
        gemini_api_key="test-key",
        gemma_model="gemma-test",
        gemma_fallback_models="gemma-fallback",
        mock_gemma_when_missing_key=True,
    )

    raw_response, metadata = await model_client.generate_model_response(
        "Summarize product feedback.",
        "general",
        settings,
    )

    assert raw_response == "Final answer."
    assert metadata["provider"] == "google_gemini_api"
    assert CapturingAsyncClient.payloads[0]["generationConfig"] == {
        "temperature": 0.2,
        "maxOutputTokens": 512,
        "topP": 0.9,
    }


@pytest.mark.anyio
async def test_generate_model_response_uses_mock_when_no_key_present():
    settings = Settings(
        _env_file=None,
        gemini_api_key=None,
        gemma_model="gemma-test",
        gemma_fallback_models="gemma-fallback",
        mock_gemma_when_missing_key=True,
    )

    raw_response, metadata = await model_client.generate_model_response(
        "Summarize product feedback.",
        "general",
        settings,
    )

    assert "[MOCK MODEL CANDIDATE RESPONSE]" in raw_response
    assert metadata["provider"] == "mock"
    assert metadata["mock"] is True
    assert metadata["attempted_models"] == []
    assert metadata["failed_models"] == []
