import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.gemma_client import generate_gemma_response
from app.governance import analyze_prompt, finalize_response
from app.schemas import AnalyzeRequest, AnalyzeResponse
from app.trace import build_trace, new_trace_id


settings = get_settings()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NEES Core Engine — Google Immersion Demo",
    version="0.1.0",
    description="Governance demo for Google for Startups Immersion Phase 2.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str | bool | list[str]]:
    return {
        "status": "ok",
        "app_name": "NEES Core Engine — Google Immersion Demo",
        "version": "0.1.0",
        "mock_mode": not bool(settings.gemini_api_key) and settings.mock_gemma_when_missing_key,
        "model": settings.gemma_model,
        "fallback_models": settings.fallback_model_list,
    }


@app.post("/v1/guard/analyze", response_model=AnalyzeResponse)
@app.post("/v1/governance/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest) -> AnalyzeResponse:
    trace_id = new_trace_id()
    analysis = analyze_prompt(request.prompt, request.scenario)
    raw_response, model_metadata = await generate_gemma_response(
        request.prompt,
        request.scenario,
        settings,
    )
    governed_response = finalize_response(raw_response, analysis)
    trace = build_trace(
        trace_id=trace_id,
        prompt=request.prompt,
        scenario=request.scenario,
        analysis=analysis,
        model_metadata=model_metadata,
        governed_response=governed_response,
    )
    logger.info(
        "trace_id=%s scenario=%s prompt_length=%d intent=%s risk_band=%s "
        "policy_decision=%s mock_mode=%s",
        trace_id,
        request.scenario,
        len(request.prompt),
        analysis.intent,
        analysis.risk_band,
        analysis.policy_decision,
        bool(model_metadata.get("mock", False)),
    )

    return AnalyzeResponse(
        trace_id=trace_id,
        scenario=request.scenario,
        intent=analysis.intent,
        risk_band=analysis.risk_band,
        policy_decision=analysis.policy_decision,
        flags=analysis.flags,
        gemma_raw_response=raw_response,
        governed_response=governed_response,
        explanation=analysis.explanation,
        trace=trace,
    )
