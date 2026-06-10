from typing import Any, Literal
from pydantic import BaseModel, Field, field_validator


Scenario = Literal["general", "customer_support", "agent_action", "sensitive_advice", "memory_boundary"]
RiskBand = Literal["green", "yellow", "red"]
PolicyDecision = Literal["allow", "modify", "ask_confirmation", "block"]


class AnalyzeRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=8000)
    scenario: Scenario = "general"

    @field_validator("prompt")
    @classmethod
    def prompt_must_not_be_blank(cls, value: str) -> str:
        prompt = value.strip()
        if not prompt:
            raise ValueError("Prompt must not be empty.")
        return prompt


class GovernanceAnalysis(BaseModel):
    intent: str
    risk_band: RiskBand
    policy_decision: PolicyDecision
    flags: list[str]
    explanation: str


class AnalyzeResponse(BaseModel):
    trace_id: str
    scenario: Scenario
    intent: str
    risk_band: RiskBand
    policy_decision: PolicyDecision
    flags: list[str]
    gemma_raw_response: str
    governed_response: str
    explanation: str
    trace: dict[str, Any]
