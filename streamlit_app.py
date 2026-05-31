import streamlit as st


def main() -> None:
    st.set_page_config(
        page_title="stock-agent - 단계형 투자성향 수집",
        page_icon="📊",
        layout="wide",
    )
    _init_intake_state()
    st.markdown(
        """
### 진행 상황 (PM 안내)

- ✅ **6주차 (이번 주)** — PRD v0.6, 기능명세서, 협업 가이드 완성
- ⏳ **7주차** — DB 스키마 적용 + Quant Worker 첫 호출 + Hello E2E
- ○ **8주차** — 기본 기능 5개 완성 + langfuse 연동
- ○ **9주차** — 중간 시연 (박민호 페르소나)
- ○ **10주차** — 고급 기능 시작 (A2A 패턴)
- ○ **11주차** — 고급 기능 완성
- ○ **12주차** — Streamlit Cloud 라이브 배포 + 발표

### 문서 보러가기

- [PRD v0.6](docs/prd/PRD_v0.6.md)
- [기능 명세서](docs/functional-spec/functional_spec_v0.1.md)
- [시스템 흐름도](docs/architecture/system_flow.md)
- [용어집](docs/glossary.md)

---

> 본 시스템 출력은 투자 권유가 아닙니다. (교육용 프로토타입)
        """
    )


if __name__ == "__main__":
    main()
