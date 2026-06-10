from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from uuid import uuid4

from app.schemas import GovernanceAnalysis


APP_NAME = "NEES Core Engine — Google Immersion Demo"
NEES_GUARD_VERSION = "0.1.0"


def new_trace_id() -> str:
    return f"trace_{uuid4().hex[:16]}"


def build_trace(
    *,
    trace_id: str,
    prompt: str,
    scenario: str,
    analysis: GovernanceAnalysis,
    model_metadata: dict,
    governed_response: str,
) -> dict:
    timestamp = datetime.now(timezone.utc).isoformat()
    response_hash = hashlib.sha256(governed_response.encode()).hexdigest()[:16]

    return {
        "trace_id": trace_id,
        "app_name": APP_NAME,
        "nees_guard_version": NEES_GUARD_VERSION,
        "scenario": scenario,
        "intent": analysis.intent,
        "risk_band": analysis.risk_band,
        "policy_decision": analysis.policy_decision,
        "flags": analysis.flags,
        "model_name": model_metadata.get("used_model") or model_metadata.get("model", "unknown"),
        "mock_mode": bool(model_metadata.get("mock", False)),
        "response_hash_sha256_prefix": response_hash,
        "response_char_count": len(governed_response),
        "prompt_word_count": len(prompt.split()),
        "timestamp": timestamp,
        "created_at": timestamp,
        "input_summary": {
            "scenario": scenario,
            "prompt_preview": prompt[:180],
            "prompt_length": len(prompt),
        },
        "governance_analysis": analysis.model_dump(),
        "model_metadata": model_metadata,
        "final_decision": {
            "risk_band": analysis.risk_band,
            "policy_decision": analysis.policy_decision,
            "flags": analysis.flags,
        },
    }
