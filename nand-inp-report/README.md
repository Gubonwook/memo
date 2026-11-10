# NAND향 InP 채널 — 보고서 겸 학습 참고서

3D NAND의 poly-Si 채널을 InP로 바꾸는 아이디어를 공부하고 실험을 설계하기 위한 자료다 (2026-11-10 작성).

- [report.md](report.md) — 본문 (13개 장 + 4A 물리 메커니즘 + 6A 구조별 문제·해결 총정리, 출처 약 35개)
- [figures/](figures/) — 그림 7개 (PNG)

| 그림 | 내용 |
| --- | --- |
| fig0_nand_string | 3D NAND 스트링 수직 단면, 읽기 전류 경로 |
| fig1_cell_problem_map | InP 마카로니 셀 단면과 문제 지점 4곳 |
| fig2_band_program_erase | 프로그램·소거 밴드 개념도 |
| fig3_interface_defects | 역계면 결함 6종과 대응 |
| fig4_ald_cycle | TMIn/PH₃ ALD 사이클과 PH₃ 병목 |
| fig5_integration_routes | 집적 경로 A/B 비교 |
| fig6_cell_current_driver_tree | 셀 전류 드라이버 트리 |

## 주의

- InP 채널 NAND 셀을 직접 실증한 공개 문헌은 조사 범위에서 찾지 못했다. III-V NAND 실증은 imec InGaAs(IEDM 2015)뿐이다.
- 결함 지도, 메커니즘 계산값은 III-V MOSFET·산화물 채널 연구에서 온 일반 원리와 가정 값이다. 설계에는 원전과 TCAD로 재확인한다.
- 2장 물성표는 교과서 대표값이며 원전(Ioffe DB 등) 재확인이 필요하다.
- 원본(편집 가능한 문서): https://claude.ai/artifact/SXsB1f5Fs5AW8tPHabjRWR

## 관련

- [../iii-v-precursors](../iii-v-precursors) — In/Ga 전구체, As/P 반응물, 공정 조건 DB (5장·10장에서 사용)
