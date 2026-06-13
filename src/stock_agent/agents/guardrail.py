import re
from typing import Optional

from stock_agent.schemas.analysis import AgentState, GuardrailResult, StrategistResult


_PII_EMAIL_RE = re.compile(r"\b[\w.%+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
_PII_PHONE_RE = re.compile(r"\b\d{2,3}[-\s]?\d{3,4}[-\s]?\d{4}\b")
_PROFANITY = {"fuck", "shit", "damn", "씨발", "좆"}
_GUARANTEE_RE = re.compile(r"\b(guarantee|guaranteed|risk[- ]?free|will\s+be|will\s+make|ensure|assure|보장|무위험|확실히|반드시|100%)\b", re.I)
_PERCENT_RETURN_RE = re.compile(r"\b\d{1,3}%\s*(return|수익|수익률)\b", re.I)

# Additional banned phrases and language-specific risky phrases
_BANNED_PHRASES = {
    "한국": ["무조건", "확실한 수익", "절대 손실 없음", "100% 수익"],
}


def _contains_pii(text: Optional[str]) -> bool:
    if not text:
        return False
    if _PII_EMAIL_RE.search(text):
        return True
    if _PII_PHONE_RE.search(text):
        return True
    return False


def _contains_profanity(text: Optional[str]) -> bool:
    if not text:
        return False
    low = text.lower()
    return any(word in low for word in _PROFANITY)


def _contains_guarantee(text: Optional[str]) -> bool:
    if not text:
        return False
    if _GUARANTEE_RE.search(text):
        return True
    if _PERCENT_RETURN_RE.search(text):
        return True
    return False


def _soften_headline(headline: str) -> str:
    # basic, conservative rewrites to avoid strong guarantees
    h = headline
    h = re.sub(r"\bwill\b", "may", h, flags=re.I)
    # remove explicit guarantee/assurance words rather than reintroducing them
    h = re.sub(r"\bguarantee(s?|d)?\b", "", h, flags=re.I)
    h = re.sub(r"\bensure(s?|d)?\b", "", h, flags=re.I)
    h = re.sub(r"\bassure(s?|d)?\b", "", h, flags=re.I)
    h = re.sub(r"\bno\s*risk\b", "reduced visibility on risk", h, flags=re.I)
    # replace explicit percent-return statements with non-numeric phrasing
    h = _PERCENT_RETURN_RE.sub("significant return", h)

    # strip multiple spaces introduced by removals
    h = re.sub(r"\s{2,}", " ", h).strip()
    if not h.endswith(" [수정됨]"):
        h = h + " [수정됨]"
    return h


def run_guardrail(state: AgentState, evidence_bundle: Optional[dict] = None, policy: Optional[dict] = None) -> AgentState:
    """Run guardrail checks on the strategist output and attach GuardrailResult to state.

    This performs lightweight, deterministic checks:
    - PII detection (emails/phones)
    - Profanity detection
    - Investment-guarantee / absolute claim detection
    - Evidence sufficiency (basic)

    The function does not call external services and is safe to run synchronously.
    """
    if state.strategist is None:
        raise ValueError("Strategist result required for guardrail evaluation")

    strat: StrategistResult = state.strategist
    passed = True
    warnings: list[str] = []
    revised_headline = strat.headline or ""

    # PII checks
    if _contains_pii(str(state.user_query)):
        passed = False
        warnings.append("PII detected in user query — input rejected or redacted")

    if _contains_pii(revised_headline) or any(_contains_pii(r) for r in strat.key_reasons):
        passed = False
        warnings.append("PII detected in strategist output — redaction required")

    # Profanity checks
    if _contains_profanity(str(state.user_query)) or _contains_profanity(revised_headline) or any(_contains_profanity(r) for r in strat.key_reasons):
        passed = False
        warnings.append("Inappropriate language detected in inputs/outputs")

    # Guarantee / absolute claim detection
    guarantee_found = _contains_guarantee(revised_headline) or any(_contains_guarantee(r) for r in strat.key_reasons)
    if guarantee_found:
        passed = False
        warnings.append("Potential investment-guarantee or absolute claim detected and softened")
        revised_headline = _soften_headline(revised_headline or strat.headline)

    # Evidence sufficiency: require at least one key reason and non-empty next_actions
    if not strat.key_reasons or len(strat.key_reasons) < 1:
        warnings.append("Insufficient explicit supporting reasons provided by strategist")

    # Build disclaimer
    disclaimer_lines = []
    disclaimer_lines.append("본 분석은 교육 및 정보 제공 목적이며 투자 권유가 아닙니다.")
    disclaimer_lines.append("투자 결정은 본인의 판단과 책임으로 진행하시기 바랍니다.")
    if not passed:
        disclaimer_lines.append("일부 문구가 위험 검출로 인해 완화되었거나 출력이 제한되었습니다.")

    disclaimer = " ".join(disclaimer_lines)

    guardrail_result = GuardrailResult(
        passed=passed,
        warnings=warnings,
        revised_headline=revised_headline,
        disclaimer=disclaimer,
    )

    state.guardrail = guardrail_result
    return state

