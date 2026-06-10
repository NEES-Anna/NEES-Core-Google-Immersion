from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["app_name"] == "NEES Core Engine — Google Immersion Demo"
    assert body["version"] == "0.1.0"
    assert isinstance(body["mock_mode"], bool)
    assert body["model"]
    assert isinstance(body["fallback_models"], list)


def test_analyze_api_returns_required_fields():
    response = client.post(
        "/v1/guard/analyze",
        json={
            "prompt": "Reply harshly to this angry customer.",
            "scenario": "customer_support",
        },
    )

    assert response.status_code == 200
    body = response.json()
    for field in {
        "trace_id",
        "scenario",
        "intent",
        "risk_band",
        "policy_decision",
        "flags",
        "gemma_raw_response",
        "governed_response",
        "explanation",
        "trace",
    }:
        assert field in body

    assert body["trace_id"].startswith("trace_")
    assert body["risk_band"] == "yellow"
    assert body["policy_decision"] == "modify"


def test_analyze_rejects_blank_prompt():
    response = client.post(
        "/v1/guard/analyze",
        json={"prompt": "   ", "scenario": "general"},
    )

    assert response.status_code == 422
    assert "Prompt must not be empty" in response.text


def test_trace_contains_required_keys():
    response = client.post(
        "/v1/guard/analyze",
        json={"prompt": "Summarize this product feedback.", "scenario": "general"},
    )

    assert response.status_code == 200
    trace = response.json()["trace"]
    for key in {
        "trace_id",
        "scenario",
        "intent",
        "risk_band",
        "policy_decision",
        "flags",
        "model_name",
        "mock_mode",
        "response_hash_sha256_prefix",
        "response_char_count",
        "prompt_word_count",
        "timestamp",
        "created_at",
        "input_summary",
        "governance_analysis",
        "model_metadata",
        "final_decision",
        "app_name",
        "nees_guard_version",
    }:
        assert key in trace

    assert trace["app_name"] == "NEES Core Engine — Google Immersion Demo"
    assert trace["nees_guard_version"] == "0.1.0"
    assert len(trace["response_hash_sha256_prefix"]) == 16
    assert trace["response_char_count"] == len(response.json()["governed_response"])
    assert trace["prompt_word_count"] == 4


def test_governance_analyze_endpoint_alias():
    response = client.post(
        "/v1/governance/analyze",
        json={"prompt": "Summarize this feedback.", "scenario": "general"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "trace_id" in body
    assert body["scenario"] == "general"
    assert body["risk_band"] == "green"
