# MLIP 전구체 흡착 계산: SevenNet 중심 1달 준비 코스

2026-11-06

## 요약과 권장

**SevenNet-Omni(`7net-omni`)로 시작하되, UMA·MACE·Orb를 같은 입력으로 돌려 비교하고, 선택은 본인 DFT 결과로 하세요.** Matbench Discovery 순위는 결정 지표이라 전구체 흡착 정확도를 보장하지 않습니다.

- **왜 SevenNet-Omni인가:** 결정·표면(OC20/OC22)·MOF·분자(OMol25)까지 15개 데이터셋으로 학습했고, 논문에서 ASD 억제제 흡착 데이터로도 시험되었습니다. SevenNet-MF-ompa(Matbench 22위)는 이번 용도에서는 차선입니다.
- **가장 큰 위험:** 기체 전구체 분자의 에너지 오차, 태스크(`modal`) 선택(같은 흡착에서 0.159 eV대 0.684 eV), 라이선스 표기 충돌.
- **다른 도구:** 완화는 ASE 최적화기(FIRE 등), 대량 배치는 TorchSim, 후보 비교는 UMA(`oc20`·`omol`), MACE(MH-1·MPA-0), Orb v3, MatterSim.
- **4주 계획:** 1주 설치·재현 → 2주 흡착 파이프라인 → 3주 DFT 대비 검증(통과 기준 제안: E_ads MAE 0.1~0.2 eV) → 4주 스크리닝 또는 모델 교체 판단.
- **현재 한계:** 실제 ALD 전구체 흡착에 대한 정량 비교는 이번에 본문을 열지 못해 확인하지 못했습니다. 내 계 DFT 5~10개가 유일한 근거입니다.

## Matbench Discovery에서 쓸 수 있는 모델

Matbench Discovery 순위는 **결정 안정성·구조 최적화·포논** 점수이지 분자 흡착 정확도가 아닙니다. 아래는 [리더보드](https://matbench-discovery.materialsproject.org/models)에서 읽은 값이고(전체 74개 항목 중 일부, 페이지에 갱신일 표기 없음), 상위권은 대부분 MPtrj+OMat24+sAlex("OAM") 계열입니다.

| 순위 | 모델 | CPS | F1 | κSRME ↓ | 학습 데이터 | 파라미터 |
|---|---|---|---|---|---|---|
| 1 | DPA-4.1-Max-OAM-PFT | 0.913 | 0.935 | 0.081 | MP+OMat24+sAlex+MDR-MP | 99M |
| 3 | DPA-4.1-Max-OAM | 0.910 | 0.933 | 0.09 | MP+OMat24+sAlex | 99M |
| 4 | TECE-OAM-RRA-1.0 | 0.908 | 0.929 | 0.093 | MP+OMat24+sAlex | 222M |
| 7 | EquiformerV3+DeNS-OAM | 0.902 | 0.931 | 0.118 | MP+OMat24+sAlex | 30.3M |
| 8 | GRACE-3L-OAM-L | 0.900 | 0.925 | 0.121 | MP+OMat24+sAlex | 42.1M |
| 9 | PET-OAM-XL | 0.898 | 0.924 | 0.119 | MP+OMat24+sAlex | 730M |
| 12 | eSEN-30M-OAM | 0.888 | 0.925 | 0.17 | MP+OMat24+sAlex | 30.2M |
| 14 | Nequip-OAM-XL | 0.886 | 0.906 | 0.125 | MP+OMat24+sAlex | 32.1M |
| 16 | MACE-SOYO-OAM | 0.873 | 0.903 | 0.184 | MP+OMat24+sAlex | 6.48M |
| 17 | SevenNet-Omni-i12 | 0.873 | 0.906 | 0.192 | COSMOS 데이터셋 | 54.9M |
| 21 | ORB v3 | 0.861 | 0.905 | 0.21 | MPtrj+Alex+OMat24 | 25.5M |
| 22 | SevenNet-MF-ompa | 0.844 | 0.901 | 0.317 | MP+OMat24+sAlex | 25.7M |
| 30 | MACE-MPA-0 | 0.795 | 0.852 | 0.412 | MP+sAlex | 9.06M |
| 33 | MatterSim v1 5M | 0.767 | 0.862 | 0.575 | MatterSim | 4.55M |
| 45 | SevenNet-l3i5 | 0.714 | 0.76 | 0.55 | MPtrj | 1.17M |
| 50 | SevenNet-0 | 0.653 | 0.724 | 0.762 | MPtrj | 842k |
| 52 | MACE-MP-0 | 0.637 | 0.669 | 0.682 | MPtrj | 4.69M |
| 62 | CHGNet | 0.400 | 0.613 | 1.717 | MPtrj | 413k |

CPS는 발견(F1)·구조 최적화(RMSD)·포논(κSRME)을 합친 점수입니다. SevenNet은 상위권은 아니지만 중상위(MF-ompa 22위)이고, 아래 절에서 보듯 **분자·표면 데이터까지 학습한 모델이 따로 있다는 점**이 전구체 흡착에서는 더 중요합니다.

## 전구체 흡착에 쓸 모델과 주의점

전구체 흡착(분자–표면)에는 Matbench 점수보다 **학습 데이터에 분자·표면이 들어 있는지**가 더 중요합니다. 아래 후보 중 SevenNet-Omni는 그 조건을 만족하고, 논문에서 ASD 억제제 흡착 데이터로도 시험된 모델입니다.

| 후보 | 왜 후보인지 | 라이선스·접근 | 확인할 점 |
|---|---|---|---|
| [SevenNet-Omni](https://sevennet.readthedocs.io/en/latest/user_guide/pretrained.html) (`7net-omni`, 문서의 권장 모델) | 결정·표면(OC20/OC22)·MOF·분자(OMol25 등) 15개 데이터셋 다중 작업 학습. 태스크로 `mpa`(PBE), `omol25_low`(ωB97M-V), `matpes_r2scan` 등 선택 | 코드 MIT(Zenodo v0.12.0 표기). 체크포인트 라이선스는 문서에 없음 | 라이선스 표기 충돌(아래 참고), `modal` 선택이 결과를 바꿈 |
| [UMA](https://github.com/facebookresearch/fairchem) (`uma-s-1p2p1`, `uma-m-1p1`) | `oc20`(촉매 표면), `omol`(분자), `omat`(무기물) 태스크. 흡착재 예제가 공식 문서에 있음 | 코드 MIT. 가중치는 "적용 분야별로 라이선스가 다름", Hugging Face 신청·로그인 필요 | 가중치 라이선스(상업 사용), `oc20`은 분산 보정 없음 |
| [MACE](https://mace-docs.readthedocs.io/en/latest/guide/foundation_models.html) (MACE-MP-0/MPA-0, MACE-MH-1, MACE-OFF23) | MPA-0·MP-0는 재료용(MIT). MH-1은 OMAT/OMOL/OC20/MATPES로 학습된 다목적(표기: ASL). OFF23은 유기 분자용(ASL) | `mace_mp(model="medium-mpa-0")`, `mace_mp(dispersion=True)`로 D3 | ASL 표기 모델의 상업·업무 이용 조건 확인 |
| [Orb v3](https://matbench-discovery.materialsproject.org/models/orb-v3) | Apache-2.0(코드·체크포인트), 보존력 방식, 25.5M, Matbench CPS 0.861 | pip, 라이선스 부담 작음 | 분자·표면 데이터 학습 여부는 이번에 확인하지 못함 |
| MatterSim, eSEN, GRACE 등 | 아래 벤치마크에서 좋은 결과가 보고된 모델이 있음 | 각 레포 확인 | 전구체 계에서 직접 시험 필요 |

**벤치마크 근거 (흡착 에너지)**

- 촉매 흡착 벤치마크 [논문](https://arxiv.org/pdf/2512.16702)은 16개 계열 80개 모델을 비교했고, "eSEN, Orb, UMA가 대체로 성능이 좋다"고 했습니다. 동시에 "모든 경우에 최고인 모델은 없으니 내 계에서 확인하라"고 권고합니다.
- 흡착 에너지 오차의 상당 부분은 **기체 분자 에너지 오차**에서 옵니다. 고체 데이터만 학습한 모델은 기체 분자 에너지를 잘 맞추지 못하고, 구조 완화(relaxation)를 거치면 오차가 늘어났습니다(eSEN-30M-OAM은 RMSE 1.6배). SevenNet-Omni 논문도 흡착 오차가 대부분 분자 단독 에너지에서 온다고 보고합니다.
- SevenNet-Omni [논문](https://arxiv.org/html/2510.11241v1)의 보고치: 금속 표면 흡착 오차 0.06 eV 이하, MOF 0.1 eV 이하. ADS41 벤치마크(흡착 에너지 MAE, r2SCAN 수준)에서 `matpes-r2scan` 태스크 0.159 eV, `mpa` 태스크 0.684 eV로 **태스크에 따라 4배 차이**가 납니다. 저자들은 Co·Ni 표면의 산소 함유 분자 흡착이 널리 잘못 예측된다고 경고합니다.
- 자성 원소(Co, Ni 등) 표면은 다수 모델에서 큰 오차(일부 3 eV 초과)가 보고되었습니다. 분자·표면 태스크가 있는 UMA의 `oc20`은 산화물이 학습에 없습니다(`oc22`는 >1p2에서 제공).
- 유기 분자 201개·Zn 슬럭 벤치마크(JPCL 2026)는 M3GNet, eSCN, UMA, MatterSim을 비교해 MatterSim이 전체적으로 좋았고, UMA는 흡착 거리를 체계적으로 과대평가했다고 합니다([ICIQ 요약](https://iciq.org/publication/benchmarking-universal-machine-learning-interatomic-potentials-for-accelerated-adsorption-energy-evaluation-with-dft-single-point-calculations/)). 단, 이것은 Zn 표면이라 SiO₂·실리콘계에 일반화되지 않습니다.

**ALD/ASD 적용 사례**

- Kim, Han, Kang의 [arXiv:2610.22911](https://arxiv.org/abs/2610.22911)(2026-10-16)는 사전학습 범용 MLIP와 off-lattice grand canonical Monte Carlo를 이어 비정질 SiO₂ 위 억제제 흡착·전구체 차단을 다뤘습니다. 실제 표면에서 반응 에너지와 활성화 장벽이 사이트마다 크게 다르다는 결론입니다. 쓴 모델 이름과 DFT 비교 수치는 본문을 열지 못해(접속 제한) 확인하지 못했습니다.
- SevenNet-Omni 논문은 "ASD 억제제 흡착 반응 데이터는 위 Kim 등의 저자들이 제공했다"고 적고 있습니다. 즉 SevenNet 제작자 그룹이 이 용도로 직접 시험했지만, 그 수치는 이번에 읽은 텍스트에 없었습니다.

**실무 주의점 (위 근거와 제 추론 구분)**

- *근거:* 서로 다른 DFT 수준의 태스크(예: UMA `oc20`은 RPBE·분산 없음, `omol`은 ωB97M-V, `omat`은 PBE)는 기준이 다릅니다. SevenNet은 `modal`을 반드시 고르게 합니다.
- *제 추론:* 슬럭은 한 태스크, 기체 분자는 다른 태스크로 계산해 E_ads = E(슬럭+분자) − E(슬럭) − E(분자)를 만들면 에너지 기준이 섞일 수 있습니다. 모든 항을 같은 태스크에서 계산하고, 실제 DFT와 비교해 검증하는 편이 안전합니다.
- *근거:* [SevenNet D3는 CUDA GPU가 필수](https://sevennet.readthedocs.io/en/stable/user_guide/ase_calculator.html)(CPU 단독 미지원). 유기 전구체는 분산력 기여가 크므로 D3 포함 여부가 결과를 크게 바꿀 수 있습니다(UMA 문서도 `oc20`에서 큰 분자의 분산을 경고).

## 환경 준비와 세팅 문서 체크리스트

아래 항목을 1주차에 끝내면 이후 실험이 수월해집니다. 파이썬·PyTorch·CUDA 버전 요구 사항은 이번에 확인하지 못했으니 설치 전에 공식 문서에서 확인하세요(Matbench 제출 페이지의 torch 2.2.1 등은 2025년 3월 당시 버전이라 지금과 다릅니다).

**A. 설치**

- [ ] 가상환경 하나를 모델 계열별로 분리(SevenNet / fairchem(UMA) / MACE / Orb는 의존성 충돌 가능성이 큽니다)
- [ ] SevenNet: `pip install sevenn` ([PyPI](https://pypi.org/project/sevenn/) 패키지명), 단 시작 전 [변경 기록](https://sevennet.readthedocs.io/en/latest/changelog.html)의 0.13.0 변경 사항(`mliap12` 그룹 이름 변경, `torchscript` 파일 형식 지원 중단, CUDA 13용 그룹 추가) 확인
- [ ] 가중치 다운로드는 처음부터 한 번에: `7net-omni`, `7net-mf-ompa`, 소형 `7net-nano-5.5`
- [ ] UMA: `pip install fairchem-core`, Hugging Face 계정으로 UMA 저장소 접근 신청 후 `huggingface-cli login`
- [ ] MACE(`mace-torch`), Orb(`orb-models`), 배치 완화용 [TorchSim](https://github.com/torchsim/torch-sim)(`pip install torch-sim-atomistic`, Python 3.12+, MIT)
- [ ] ASE, pymatgen, 시각화(ase gui 또는 OVITO)

**B. 연산 자원**

- [ ] GPU 없이 가능한 것: 소형 모델(`7net-nano-*`, 약 105k 파라미터)으로 작은 슬럭 완화, 파이프라인 검증
- [ ] GPU가 필요한 것: SevenNet D3(CUDA 필수), 큰 모델의 대량 완화, NEB 반복 계산
- [ ] 기준 설정: 수렴 기준 fmax·최대 스텝을 한 곳에 고정. 참고로 Matbench 프로토콜은 FIRE, fmax 0.02, 최대 800스텝, FrechetCellFilter입니다(결정용; 슬럭에는 셀 필터를 쓰지 않습니다)

**C. 세팅 문서(기록할 것)**

- [ ] 환경 고정 파일(`pip freeze`), 모델 이름·버전·체크섬·`modal`/`task_name`
- [ ] 라이선스 표(코드, 가중치, 학습 데이터 각각) — 아래 위험요소 절 참고
- [ ] DFT 기준 데이터셋: 본인이 가진 전구체·표면 DFT 결과 5~10개(흡착 에너지, 구조, 사이트 순위)
- [ ] 실행 로그 템플릿: 모델, 슬럭 크기·층 수, 고정 층, 분산 보정 유무, 수렴 여부, 소요 시간

**D. 최소 실행 예시 (SevenNet, 문서의 코드 형태)**

```python
from sevenn.calculator import SevenNetCalculator
from ase.io import read
from ase.optimize import FIRE

atoms = read('slab_plus_precursor.xyz')
atoms.calc = SevenNetCalculator(model='7net-omni', modal='mpa')  # modal은 다중 충실도 모델에서 필수
FIRE(atoms).run(fmax=0.05, steps=500)
print(atoms.get_potential_energy())
```

위 `modal` 이름은 문서에 예시된 값(`mpa`, `omat24`, `matpes_pbe`, `matpes_r2scan`, `omol25_low`)이며, 슬럭·분자에 어느 모달이 맞는지는 1주차에 DFT 데이터로 비교해 정합니다.

## 4주 코스 (11/9 시작 가정)

순서는 **설치·재현 → 흡착 파이프라인 → DFT 대비 검증 → 스크리닝·판단**입니다. 3주차 말 검증 결과가 나쁘면 4주차는 스크리닝 대신 모델 교체·미세조정 판단으로 바꿔야 합니다.

| 주 | 목표 | 할 일 | 산출물 | 통과 기준(제안) |
|---|---|---|---|---|
| 1주 (11/9–11/13) | 설치와 재현 | 가상환경 분리 설치, SevenNet(`7net-omni`, `7net-mf-ompa`, `7net-nano-5.5`)·UMA·MACE·Orb 로드. 동일 ASE 스크립트로 간단한 벌크·작은 슬럭 완화. 라이선스 표 작성. GPU 없으면 소형 모델로 파이프라인만 검증 | 세팅 문서 v1, 환경 고정 파일, 라이선스 표 | 네 계열이 같은 스크립트로 에너지·힘을 출력, 재현 가능한 설치 절차 |
| 2주 (11/16–11/20) | 흡착 계산 파이프라인 | 슬럭 생성(ASE/pymatgen), 분자 배치·후보 사이트 샘플링, 하부 층 고정 후 완화(FIRE/LBFGS), 기체 분자·슬럭 에너지 참조 계산, E_ads 자동 집계, 배치 완화(TorchSim) 시험 | E_ads 스크립트, 실행 로그 템플릿 | 동일 입력에서 재실행 시 같은 결과, 모델·태스크별 결과 표 자동 생성 |
| 3주 (11/23–11/27) | DFT 대비 검증 | 본인 DFT 데이터 5~10개를 기준으로 모델 3~4개·`modal`/`task_name`별 E_ads MAE, 흡착 거리·사이트 순위(Kendall τ), D3 유무(GPU 필요), 오차 원인(기체 분자 에너지·완화 후 오차 등) 분해 | 벤치마크 표, 오차 원인 메모 | 스크리닝용: E_ads MAE 0.1~0.2 eV 이하(촉매 벤치마크 논문이 "초기 스크리닝에는 충분"이라 한 수준을 참고한 제 제안), 사이트 순위 유지 |
| 4주 (11/30–12/4) | 확장과 판단 | 통과 시: 전구체 3~5종 × 표면 2~3종 스크리닝, ASE CI-NEB로 반응 장벽 1~2개 시험, 모델 간 차이를 불확실성으로 기록. 미통과 시: 모델 교체 또는 미세조정(SevenNet 0.13의 망각 방지 미세조정 기능) 타당성 평가 | 최종 보고서: 모델 선택 근거, 사용 가이드, go/no-go | 모델 선택이 DFT 비교 수치로 뒤받침되고 한계가 문서화됨 |

**매일 할 일(모든 주차 공통)**: 실험마다 실행 로그 한 줄(모델·`modal`·수렴 여부·소요 시간), 같은 입력을 다른 모델로 한 번 더 돌리기.

**방향을 정하는 것**: 3주차에서 태스크를 바꿔도 오차가 내려가지 않으면 흡착 에너지를 MLIP로 직접 쓰지 말고, MLIP로 완화한 구조에 DFT 싱글포인트를 계산하는 방식으로 전환합니다. 이 방식은 [ICIQ 저자들의 워크플로](https://iciq.org/publication/benchmarking-universal-machine-learning-interatomic-potentials-for-accelerated-adsorption-energy-evaluation-with-dft-single-point-calculations/)로 보고된 방법이며, 유기분자/Zn 표면에서 MatterSim 기반으로 85.4%의 성공률을 보고했습니다.

## 위험요소와 확인이 필요한 것

| 항목 | 내용 | 대응 |
|---|---|---|
| 라이선스 | SevenNet은 Zenodo v0.12.0 기록에 MIT로 나오지만, Matbench 제출 페이지(MF-ompa)는 코드·체크포인트 모두 GPL-3.0으로 표기(제출자 신고 값). UMA 가중치는 "적용 분야별로 다름", MACE의 OMAT·MH-1·OFF23은 ASL로 표기 | 설치한 패키지의 LICENSE 파일·체크포인트 배포 페이지를 직접 확인. 업무에 쓸 경우 소속 기관 규정에 맞춰 상업 이용 가능 여부를 먼저 확정 |
| 기체 분자 에너지 | 고체만 학습한 모델은 기체 분자 에너지를 잘 못 맞춤. 흡착 오차의 대부분이 여기서 왔다는 보고도 있음 | 분자 데이터를 학습한 태스크(`omol25_low`, UMA `omol`) 비교, 분자 에너지만 DFT로 계산해 치환하는 시험 |
| 태스크 선택 | SevenNet-Omni는 같은 ADS41 흡착에서 `matpes-r2scan` 0.159 eV vs `mpa` 0.684 eV | 태스크를 고정하지 말고 3주차에 전부 비교 |
| 자성 원소 | Co·Ni 표면에서 큰 오차가 보고됨 | 전구체·기판에 3d 전이금속이 있으면 DFT로 직접 확인 |
| 완화 후 오차 | MLIP로 완화하면 에너지 오차가 커지는 경향(eSEN-30M-OAM은 RMSE 1.6배) | 완화 구조에 DFT 싱글포인트를 대조 |
| 분산·D3 | SevenNet D3는 CUDA GPU 필수. UMA `oc20`은 분산 없음(RPBE) | GPU가 없는 동안은 분산 영향이 큰 계의 결론을 보류 |
| 벤치마크 한계 | Matbench는 결정 지표이고, 실제 ALD 전구체(금속유기 착체)·비정질 표면에 대한 직접 데이터는 이번에 못 찾음 | 내 계의 DFT 5~10개가 유일한 신뢰 근거 |

**이번에 확인하지 못한 것**

- arXiv:2610.22911 본문(쓴 모델 이름·DFT 비교 수치): 접속 제한으로 초록만 읽음
- Nature Commun. SevenNet-Omni 본문, JPCL ICIQ 논문 본문, 참고 벤치마크의 모델별 흡착 에너지 표: 열람 불가 또는 일부 잘림
- 설치 요구 버전(Python·PyTorch·CUDA), 각 체크포인트의 정확한 라이선스
- Matbench 값은 페이지를 읽은 시점(2026-11-06) 기준이고 순위는 수시로 바뀝니다
- 실행 예시 코드는 공식 문서의 예제를 조합한 것이며, 실행 테스트는 하지 못했습니다

**열린 질문 (답에 따라 계획이 바뀝니다)**

- 어떤 전구체·표면이 첫 타깃이고, 그 계의 DFT 결과가 있는가?
- 상용 범용 포텐셜 등 이미 쓰는 기준선과 함께 비교할 것인가?
- GPU가 없는 환경에서만 계산할 수 있는가, GPU 확보 시점은 언제인가?

## 출처

직접 열어 읽은 페이지만 적었습니다(2026-11-06 열람).

- SevenNet: [GitHub](https://github.com/MDIL-SNU/SevenNet), [변경 기록](https://sevennet.readthedocs.io/en/latest/changelog.html), [사전학습 모델](https://sevennet.readthedocs.io/en/latest/user_guide/pretrained.html), [ASE 계산기](https://sevennet.readthedocs.io/en/stable/user_guide/ase_calculator.html), [Zenodo v0.12.0](https://zenodo.org/records/17921835)
- Matbench Discovery: [리더보드](https://matbench-discovery.materialsproject.org/models), [SevenNet-MF-ompa](https://matbench-discovery.materialsproject.org/models/sevennet-mf-ompa), [Orb v3](https://matbench-discovery.materialsproject.org/models/orb-v3), [MACE-MPA-0](https://matbench-discovery.materialsproject.org/models/mace-mpa-0)
- SevenNet-Omni: [Optimizing Cross-Domain Transfer for Universal MLIPs (arXiv:2510.11241)](https://arxiv.org/html/2510.11241v1)
- 흡착 벤치마크: [How accurate are foundational MLIPs for heterogeneous catalysis? (arXiv:2512.16702)](https://arxiv.org/pdf/2512.16702), [ICIQ 유기분자/Zn 슬럭 논문 요약](https://iciq.org/publication/benchmarking-universal-machine-learning-interatomic-potentials-for-accelerated-adsorption-energy-evaluation-with-dft-single-point-calculations/), [지지 나노입자 벤치마크 (arXiv:2512.05221, alphaXiv)](https://www.alphaxiv.org/abs/2512.05221.md)
- ALD/ASD: [From Surface Reactions to Inhibitor Coverage (arXiv:2610.22911, 초록만)](https://arxiv.org/abs/2610.22911)
- UMA: [fairchem GitHub](https://github.com/facebookresearch/fairchem), [UMA 모델 문서](https://fair-chem.github.io/core/uma.html)
- MACE: [Foundation models 문서](https://mace-docs.readthedocs.io/en/latest/guide/foundation_models.html)
- 배치 완화: [TorchSim GitHub](https://github.com/torchsim/torch-sim)
