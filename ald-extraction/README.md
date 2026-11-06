# ALD 논문 데이터 추출·DB 구축 (2026-11-04)

- [report.md](report.md): 조사 결과, 자체 호스팅/외부 API LLM 구현 방식, 데이터베이스 설계, 검증 전략, 실행 계획
- [build-guide.md](build-guide.md): 자체 호스팅 LLM(GPU 없는 PC)으로 바로 돌리는 구축 가이드 (`ald_extract_kit` 코드 기준)

참고: 보고서 점수·별 수는 각 출처가 보고한 값이며 직접 재현한 것이 아닙니다. 자체 호스팅 모델의 실제 정확도는 측정 전입니다.
- [code/](code/): 추출 파이프라인 구현 (`pip install -e ".[dev]"`, `pytest -q`, 사용법은 code/README.md)
