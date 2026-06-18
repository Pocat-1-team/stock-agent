from stock_agent.agents import guardrail as guardrail_module
from stock_agent.schemas.analysis import (
    AgentState,
    StrategistResult,
    UserProfile,
    Portfolio,
)


def _make_state(headline: str, reasons: list[str]):
    return AgentState(
        user_query="삼성전자 지금 사도 될까요?",
        user_profile=UserProfile(),
        portfolio=Portfolio(),
        strategist=StrategistResult(
            signal="HOLD",
            confidence=50,
            suitability=50,
            headline=headline,
            key_reasons=reasons,
            risks=[],
            next_actions=[],
        ),
    )


def test_guardrail_passes_clean():
    state = _make_state("중립적 관점: 업종 회복 대기", ["매출 성장 유지", "영업이익률 개선"])
    out = guardrail_module.run_guardrail(state)
    assert out.guardrail.passed is True
    assert out.guardrail.warnings == []


def test_guardrail_detects_pii_and_blocks():
    state = _make_state("Contact: test@example.com", ["매출 성장 유지"])
    out = guardrail_module.run_guardrail(state)
    assert out.guardrail.passed is False
    assert any("PII" in w for w in out.guardrail.warnings)


def test_guardrail_softens_guarantee():
    state = _make_state("This stock will guarantee 100% return", ["확실한 성장"])
    out = guardrail_module.run_guardrail(state)
    assert out.guardrail.passed is False
    assert "[수정됨]" in out.guardrail.revised_headline
    assert any("guarantee" in w.lower() or "soften" in w.lower() for w in out.guardrail.warnings)
