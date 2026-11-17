# SevenNet 체크포인트 (격리 서버 반입용)

2026-11-17 · sevenn 0.13.0 기준 · 용도: **ALD 전구체 흡착 에너지·반쪽반응 에너지**

GitHub은 100 MB가 넘는 파일을 받지 않으므로, `.pth`를 **45 MB 조각(`ckpt/*.pth.partNN`)으로 나눠** 넣었습니다. `verify_offline.py`가 조각을 합치고 해시까지 확인합니다. 원본은 [MDIL-SNU/SevenNet Releases](https://github.com/MDIL-SNU/SevenNet/releases)의 `v0.11.0.cp`, `v0.12.0.cp`, `v0.12.1.cp` 태그이고, 원본 해시는 [`ckpt/SHA256SUMS`](ckpt/SHA256SUMS)에 적어 두었습니다.

| 파일 | 크기 | 용도 | modal |
|---|---|---|---|
| `checkpoint_sevennet_omni.pth` | 103 MB | **기본 모델.** 분자·표면·결정 15개 데이터셋 | 13개 (아래 참고) |
| `checkpoint_sevennet_omni_i8.pth` | 221 MB | Omni보다 층이 깊은 모델(8층). 느리지만 더 정확할 것으로 기대 | Omni와 같음 |
| `checkpoint_sevennet_mf_ompa.pth` | 103 MB | 비교 기준. 결정 데이터만 학습 | `omat24`, `mpa` |

Omni·Omni-i8의 modal은 `sevenn cp`로 직접 확인했습니다: `omat24, mpa, omol25_low, omol25_high, matpes_pbe, matpes_r2scan, mp_r2scan, oc20, oc22, spice, qcml, odac23, pet_mad`

| 파일 | 내용 |
|---|---|
| [`reaction_energy.py`](reaction_energy.py) | 흡착·반응 에너지 계산. 여러 modal을 한 번에 비교하고 결과를 CSV로 저장 |
| [`verify_offline.py`](verify_offline.py) | 반입 후 조각 합치기, 해시 확인, 로드 테스트, 키워드 경로 설치(`--install`) |
| [`ckpt/`](ckpt) | 체크포인트 조각 11개 + `SHA256SUMS` |

## 1. 반입 절차

```bash
# (인터넷 PC) 저장소 받기: git clone 또는 GitHub의 Code → Download ZIP
git clone --depth 1 https://github.com/Gubonwook/memo
#   → sevennet-checkpoints/ 폴더 전체(약 430 MB)를 HPC로 반입

# (격리 서버)
cd sevennet-checkpoints
python verify_offline.py --dir ckpt            # 조각 합치기 + 해시 확인 + 로드 테스트
python verify_offline.py --dir ckpt --install  # model='7net-omni' 키워드로도 사용
```

Python 없이 합치려면 `cat ckpt/checkpoint_sevennet_omni.pth.part* > checkpoint_sevennet_omni.pth`를 실행한 뒤 `sha256sum`으로 확인하세요(Windows는 `copy /b a.part00+a.part01+a.part02 a.pth`). 합친 뒤에는 `.part` 파일을 지워도 됩니다.

sevenn 자체가 서버에 없다면 인터넷 PC에서 `pip download sevenn -d pkgs`로 받아 옮긴 뒤, 서버에서 `pip install --no-index --find-links pkgs sevenn`으로 설치합니다. torch는 서버의 CUDA 버전에 맞는 휠을 따로 받으세요.

## 2. 전구체 흡착·반응 에너지에서 modal 고르기

**원칙: 한 반응식의 모든 항(slab, 분자, 흡착체)은 같은 체크포인트·같은 modal·같은 D3 설정으로 계산합니다.** modal마다 기준 DFT(범함수, U 값, 에너지 기준점)가 달라서, 섞으면 의미 없는 숫자가 나옵니다. `reaction_energy.py`는 이 조건을 자동으로 지킵니다.

| 계 | 1순위 modal | 같이 비교할 modal | 이유 |
|---|---|---|---|
| 산화물 표면(HfO₂, ZrO₂, Al₂O₃, SiO₂) + 전구체/리간드 | `oc22` | `omat24`, `mpa`, `matpes_pbe` | OC22는 산화물 표면과 흡착종 데이터(PBE+U)입니다. 다만 흡착종이 작은 분자 위주라 TEMAHf 같은 큰 전구체는 omat24 계열과 비교가 필요합니다 |
| 금속 표면(Ru, Pt, Co …) + 전구체 | `omat24`, `mpa` | `oc20` | OC20은 **RPBE**라서 PBE로 계산한 내 DFT와 절대값을 바로 비교하면 안 됩니다 |
| 기준 DFT가 r²SCAN | `matpes_r2scan` | `mp_r2scan` | Omni 논문의 ADS41 흡착 벤치마크에서 MAE가 matpes_r2scan 0.159 eV, mpa 0.684 eV로 보고됨 |
| 기체 분자 단독(리간드 이탈 에너지, conformer) | `omol25_high` | `omol25_low` | 분자 전용(ωB97M-V)입니다. **slab 항과 섞지 마세요** |

**분산(vdW):** 큰 유기금속 전구체는 vdW 기여가 큽니다. PBE 계열 modal(`omat24`·`mpa`·`oc22`·`matpes_pbe`)에는 `--d3`로 D3(BJ)를 모든 항에 똑같이 넣으세요(GPU 필요). 내 DFT 기준이 PBE+D3라면 D3를 반드시 켜야 비교가 됩니다. `omol25_*`는 VV10이 이미 들어 있어 D3를 넣으면 분산이 두 번 계산됩니다.

**분자 상자:** cutoff가 6 Å이므로 상자는 분자 크기 + 12 Å 이상이어야 합니다. 작은 분자는 기본값 20 Å으로 충분하고, TEMAHf·TDMAHf급 전구체는 `--box 25`를 쓰세요.

## 3. 실행 예

```bash
CK=/data/sevennet_ckpt/checkpoint_sevennet_omni.pth

# 흡착 에너지: E(slab+mol) - E(slab) - E(mol)
python reaction_energy.py --ckpt $CK --modal oc22 omat24 mpa \
    -r slab_OH.vasp TEMAHf.xyz -p slab_TEMAHf.vasp --relax --box 25 --d3

# 반쪽반응: slab-OH + TEMAHf → slab-O-Hf(NEtMe)3 + HNEtMe
python reaction_energy.py --ckpt $CK --modal oc22 omat24 \
    -r slab_OH.vasp TEMAHf.xyz -p slab_OHf.vasp HNEtMe.xyz --relax --box 25 --d3

# 계수가 있으면 "2*H2O.xyz" 형식
```

- 완화된 구조는 `relaxed/<이름>__<modal>.vasp`, 에너지 표는 `reaction_energy.csv`에 저장됩니다.
- POSCAR의 Selective dynamics(F F F)는 고정층으로 유지됩니다.
- NEB나 전이상태 계산이 필요하면 같은 `SevenNetCalculator(model=CK, modal=...)`를 ASE NEB에 그대로 넣으면 됩니다.

## 4. 검증 결과와 주의점

이 세션의 CPU에서 세 파일 모두 해시 확인과 로드에 성공했고, 13개 modal 중 아래 modal에서 에너지가 정상적으로 계산됐습니다. `verify_offline.py`의 테스트 값(H₂O/Pt(111), O-down ontop 2.3 Å, 완화 안 함, D3 없음)은 다음과 같습니다.

| 체크포인트 | omat24 | mpa | oc20 | oc22 |
|---|---|---|---|---|
| Omni | +0.029 | +0.024 | +0.162 | +0.083 |
| Omni-i8 | −0.055 | – | – | −0.065 |
| MF-ompa | −0.535 | −0.508 | – | – |

반입 후 서버에서 같은 숫자가 나오면 파일이 정상입니다. GPU에서는 소수점 셋째 자리 정도가 다를 수 있습니다.

**같은 구조인데도 모델 사이에 ~0.5 eV 차이가 납니다.** 이 표는 정확도 비교가 아니라 로드 확인용이지만, 모델·modal 선택이 결과를 크게 바꾼다는 뜻입니다. 본격적인 스크리닝 전에 **내 VASP 결과 5~10개(전구체 흡착 몇 개 + 반쪽반응 몇 개)를 같은 구조로 계산해서, 오차가 가장 작은 체크포인트·modal 조합을 고르세요.** 자세한 모델 비교와 4주 계획은 [`../mlip-adsorption/README.md`](../mlip-adsorption/README.md)에 있습니다.

## 라이선스

SevenNet 코드는 MIT License이고, 사본을 [`LICENSE-SevenNet`](LICENSE-SevenNet)에 넣었습니다. 체크포인트의 별도 라이선스는 공식 문서에서 확인하지 못했습니다. 논문에 쓸 때는 SevenNet, SevenNet-Omni, (MF-ompa를 쓴다면) multi-fidelity 논문을 인용하세요.
