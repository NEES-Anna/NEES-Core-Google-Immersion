from __future__ import annotations

import re

from app.schemas import GovernanceAnalysis, PolicyDecision, RiskBand, Scenario


HOSTILE_TERMS = {
    "harsh",
    "rude",
    "angry",
    "insult",
    "threaten",
    "shame",
    "humiliate",
    "stupid",
    "idiot",
}
DESTRUCTIVE_TERMS = {
    "delete",
    "wipe",
    "remove",
    "erase",
    "destroy",
    "drop database",
    "purge",
    "disable account",
}
SENSITIVE_TERMS = {
    "legal advice",
    "medical advice",
    "financial advice",
    "diagnose",
    "prescribe",
    "guaranteed",
    "guarantee",
    "lawsuit",
    "investment",
}
MEMORY_BOUNDARY_TERMS = {
    "ignore previous instructions",
    "system prompt",
    "internal guidelines",
    "private memory",
    "system guidelines",
    "developer mode",
    "override rules",
    "system configuration",
}
SAFE_GENERIC_RESPONSE = "I can help with a concise, user-facing response."
FINAL_RESPONSE_RE = re.compile(r"\bfinal response:\s*(.*)", re.IGNORECASE)
SYNTHESIZED_SUMMARY_TERMS = (
    "users find",
    "users report",
    "while",
    " but ",
    "difficult",
    "confusing",
)
NON_USER_FACING_MARKERS = (
    "positive:",
    "negative:",
    "constraint check:",
    "draft 1:",
    "draft 2:",
    "draft 3:",
    "draft:",
    "input:",
    "constraint",
    "core value:",
    "pain points:",
    "role:",
    "option",
    "direct and concise?",
    "only final answer?",
    "final user-facing response only?",
    "concise?",
    "refining:",
    "no reasoning",
    "no governance demo mention",
    "1-3 sentences?",
)
NON_USER_FACING_EXACT = {"yes.", "yes"}


def analyze_prompt(prompt: str, scenario: Scenario) -> GovernanceAnalysis:
    text = normalize(prompt)
    flags: list[str] = []

    if has_any(text, HOSTILE_TERMS):
        flags.append("hostile_tone")
    if has_any(text, DESTRUCTIVE_TERMS):
        flags.append("destructive_action")
    if mentions_user_data(text):
        flags.append("user_data_risk")
    if has_any(text, SENSITIVE_TERMS):
        flags.append("sensitive_advice")
    if "guaranteed" in text or "guarantee" in text:
        flags.append("unsupported_certainty")
    if "without asking" in text or "without confirmation" in text:
        flags.append("missing_confirmation")
    if has_any(text, MEMORY_BOUNDARY_TERMS) or scenario == "memory_boundary":
        flags.append("memory_boundary_risk")

    intent = detect_intent(text, scenario, flags)
    risk_band, policy_decision = classify_policy(scenario, flags)
    explanation = explain_decision(risk_band, policy_decision, flags)

    return GovernanceAnalysis(
        intent=intent,
        risk_band=risk_band,
        policy_decision=policy_decision,
        flags=flags,
        explanation=explanation,
    )


def finalize_response(raw_response: str, analysis: GovernanceAnalysis) -> str:
    cleaned_response = clean_model_output(raw_response)
    if analysis.intent == "summarize_information":
        cleaned_response = cap_sentences(cleaned_response, limit=3)

    if analysis.policy_decision == "allow":
        return cleaned_response

    if analysis.policy_decision == "modify":
        if "hostile_tone" in analysis.flags:
            return (
                "Respond calmly, acknowledge the concern, and offer a clear next step.\n\n"
                f"{soften_hostile_text(cleaned_response)}"
            )
        if "sensitive_advice" in analysis.flags:
            return (
                "This is general information, not professional advice. Consult a qualified "
                f"professional for your specific situation.\n\n{cleaned_response}"
            )
        return cleaned_response

    if analysis.policy_decision == "ask_confirmation":
        return (
            "This action may change or remove important data. Please confirm the exact scope, "
            "review the affected records, and verify a rollback plan before proceeding."
        )

    if "memory_boundary_risk" in analysis.flags:
        return (
            "I cannot fulfill this request because it attempts to bypass memory boundaries or "
            "extract internal system configuration details."
        )

    return (
        "I cannot provide that response as written because it could create harm. Reframe the "
        "request with appropriate safeguards, consent, and professional review."
    )


def normalize(prompt: str) -> str:
    return re.sub(r"\s+", " ", prompt.strip().lower())


def has_any(text: str, terms: set[str]) -> bool:
    return any(term in text for term in terms)


def mentions_user_data(text: str) -> bool:
    return any(term in text for term in {"user data", "users", "accounts", "customer records", "database"})


def detect_intent(text: str, scenario: Scenario, flags: list[str]) -> str:
    if "memory_boundary_risk" in flags:
        return "extract_system_instructions"
    if "destructive_action" in flags:
        return "perform_destructive_agent_action"
    if scenario == "customer_support" or "customer" in text:
        return "respond_to_customer_complaint"
    if "sensitive_advice" in flags:
        return "provide_sensitive_advice"
    if "summarize" in text or "summary" in text:
        return "summarize_information"
    if scenario == "agent_action":
        return "perform_agent_action"
    return "general_assistance"


def classify_policy(scenario: Scenario, flags: list[str]) -> tuple[RiskBand, PolicyDecision]:
    if "memory_boundary_risk" in flags:
        return "red", "block"

    if "destructive_action" in flags and "user_data_risk" in flags:
        if "missing_confirmation" in flags or scenario == "agent_action":
            return "red", "ask_confirmation"
        return "yellow", "ask_confirmation"

    if "sensitive_advice" in flags:
        if "unsupported_certainty" in flags:
            return "red", "block"
        return "yellow", "modify"

    if "hostile_tone" in flags:
        return "yellow", "modify"

    return "green", "allow"


def explain_decision(risk_band: RiskBand, policy_decision: PolicyDecision, flags: list[str]) -> str:
    if policy_decision == "allow":
        return "No material governance risk was detected, so the response is allowed."
    if policy_decision == "modify":
        return "The raw response was adjusted to reduce escalation or unsupported certainty."
    if policy_decision == "ask_confirmation":
        return "The request affects important data or actions, so explicit confirmation is required."
    return "The request is blocked because it asks for high-risk guidance without adequate safeguards."


def soften_hostile_text(text: str) -> str:
    replacements = {
        "harsh": "clear",
        "angry": "concerned",
        "rude": "direct",
        "idiot": "customer",
        "stupid": "unhelpful",
    }
    softened = text
    for source, target in replacements.items():
        softened = re.sub(source, target, softened, flags=re.IGNORECASE)
    return softened


def clean_model_output(raw: str) -> str:
    final_response_candidates = extract_final_response_candidates(raw)
    if final_response_candidates:
        return strip_surrounding_quotes(best_clean_candidate(final_response_candidates))

    cleaned_lines = [line.strip() for line in raw.splitlines() if is_user_facing_line(line)]
    cleaned = "\n".join(cleaned_lines).strip()
    if not cleaned:
        return SAFE_GENERIC_RESPONSE

    quoted_candidates = [
        candidate
        for candidate in re.findall(r'"([^"\n]+(?:\n[^"\n]+)*)"', cleaned)
        if is_clean_candidate(candidate)
    ]
    if quoted_candidates:
        return strip_surrounding_quotes(best_clean_candidate(quoted_candidates))

    clean_candidates = [candidate for candidate in clean_candidate_paragraphs(cleaned) if is_clean_candidate(candidate)]
    if clean_candidates:
        return strip_surrounding_quotes(best_clean_candidate(clean_candidates))

    return SAFE_GENERIC_RESPONSE


def clean_model_response(text: str) -> str:
    return clean_model_output(text)


def extract_final_response_candidates(raw: str) -> list[str]:
    lines = raw.splitlines()
    candidates: list[str] = []

    for index, line in enumerate(lines):
        match = FINAL_RESPONSE_RE.search(line)
        if not match:
            continue

        marked_text = match.group(1).strip()
        if is_clean_candidate(marked_text):
            candidates.append(marked_text)

        tail = "\n".join(lines[index + 1 :]).strip()
        for candidate in clean_candidate_paragraphs(tail):
            if is_clean_candidate(candidate) and looks_like_final_answer(candidate):
                candidates.append(candidate)

    return candidates


def is_user_facing_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True

    lowered = stripped.lower()
    if lowered in NON_USER_FACING_EXACT:
        return False

    if has_non_user_facing_marker(stripped):
        return False

    return not re.match(r"^\s*[*-]\s*(constraint|core|pain)\b", lowered)


def has_non_user_facing_marker(text: str) -> bool:
    lowered = text.strip().lower()
    if lowered in NON_USER_FACING_EXACT:
        return True
    if re.search(r"\byes\.", lowered):
        return True
    return any(marker in lowered for marker in NON_USER_FACING_MARKERS)


def is_clean_candidate(text: str) -> bool:
    stripped = strip_surrounding_quotes(text)
    return bool(stripped) and not has_non_user_facing_marker(stripped)


def clean_candidate_paragraphs(text: str) -> list[str]:
    paragraphs = [paragraph.strip() for paragraph in re.split(r"\n\s*\n", text) if paragraph.strip()]
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return paragraphs + lines


def best_clean_candidate(candidates: list[str]) -> str:
    scored_candidates = [
        (score_clean_candidate(candidate, index), candidate)
        for index, candidate in enumerate(candidates)
        if is_clean_candidate(candidate)
    ]
    if not scored_candidates:
        return SAFE_GENERIC_RESPONSE
    return max(scored_candidates, key=lambda item: item[0])[1]


def score_clean_candidate(text: str, index: int) -> tuple[int, int]:
    stripped = strip_surrounding_quotes(text)
    lowered = f" {stripped.lower()} "
    score = index

    if looks_like_final_answer(stripped):
        score += 20
    if len(split_sentences(stripped)) == 1:
        score += 12
    if any(term in lowered for term in SYNTHESIZED_SUMMARY_TERMS):
        score += 8
    if re.search(r"\b(users|customers)\s+(find|report|say|want|need)\b", lowered):
        score += 8
    if re.search(r"\b(while|although)\b.+\b(but|find|difficult|confusing)\b", lowered):
        score += 6
    if looks_like_fragment_joined_restatement(stripped):
        score -= 35
    if len(stripped) < 20:
        score -= 10

    return score, len(stripped)


def split_sentences(text: str) -> list[str]:
    return [sentence.strip() for sentence in re.findall(r"[^.!?]+[.!?]+|[^.!?]+$", text.strip()) if sentence.strip()]


def looks_like_fragment_joined_restatement(text: str) -> bool:
    sentences = split_sentences(text)
    if len(sentences) < 3:
        return False

    short_sentences = [sentence for sentence in sentences if len(sentence.split()) <= 7]
    has_feedback_fragment_terms = all(
        re.search(r"\b(app|setup|instruction|trace|panel|useful|confusing|hard|understand)\b", sentence, re.IGNORECASE)
        for sentence in sentences[:3]
    )
    return len(short_sentences) >= 3 and has_feedback_fragment_terms


def looks_like_final_answer(text: str) -> bool:
    stripped = strip_surrounding_quotes(text)
    return len(stripped) >= 20 and bool(re.search(r"[.!?]$", stripped))


def strip_surrounding_quotes(text: str) -> str:
    return text.strip().strip('"“”').strip()


def cap_sentences(text: str, limit: int) -> str:
    sentences = re.findall(r"[^.!?]+[.!?]+(?:\s+|$)|[^.!?]+$", text.strip())
    selected = [sentence.strip() for sentence in sentences if sentence.strip()][:limit]
    return " ".join(selected) if selected else text.strip()
