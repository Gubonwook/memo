# SevenNet 활용 가이드 + RTX PRO 6000 Blackwell 세팅

2026-11-10 · SevenNet v0.13.x (GitHub 최신 커밋 2026-10-29) 기준

| 파일 | 내용 |
|---|---|
| [`index.html`](index.html) | 그림으로 정리한 보고서: 원리, 모델 선택, 돌릴 수 있는 시뮬레이션, 학습·fine-tuning, 실행 엔진, 코드 예시, ALD 적용, **RTX PRO 6000 세팅(10절)** |
| [`setup_blackwell.sh`](setup_blackwell.sh) | conda 환경 + PyTorch(cu128) + SevenNet + 가속기를 설치하는 스크립트 |
| [`check_env.py`](check_env.py) | 설치 검증: sm_120 포함 여부, 가속기가 e3nn 결과와 일치하는지, D3 JIT, ms/step·최대 메모리 |

보고서 보기: 저장소에서 `index.html`을 내려받아 브라우저로 열거나, htmlpreview 같은 뷰어를 쓰세요.

## RTX PRO 6000 Blackwell(96GB) 요약

**세팅 가능합니다.** compute capability가 12.0(sm_120)이라서 다음 조건을 맞춰야 합니다.

1. 드라이버 **R570+**, **CUDA 12.8+**. D3·FlashTP·LAMMPS를 빌드하려면 nvcc 12.8+도 필요합니다.
2. PyTorch는 **cu128 이상 휠**을 써야 합니다. cu126 이하 휠에는 sm_120 커널이 없습니다.
   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cu128
   pip install sevenn
   export TORCH_CUDA_ARCH_LIST="12.0"
   ```
3. 가속기
   - FlashTP: `CUDA_ARCH_LIST="120"`으로 빌드합니다. README에 Blackwell 동작이 명시돼 있습니다.
   - cuEquivariance: sm_120 지원을 공식 문서에서 확인하지 못했으므로, `check_env.py`로 결과가 일치하는지 검증하세요.
4. LAMMPS
   - ML-IAP 경로(`stable_22Jul2025_update4`): cmake에 `-D Kokkos_ARCH_BLACKWELL120=ON`을 추가합니다. 내장 Kokkos 4.6.2 소스에서 지원을 확인했습니다.
   - Torch 경로: D3를 넣을 때 `TORCH_CUDA_ARCH_LIST="12.0"`을 지정합니다.

```bash
bash setup_blackwell.sh                         # 기본 설치
WITH_FLASH=1 WITH_TORCHSIM=1 bash setup_blackwell.sh
python check_env.py --model 7net-omni --modal mpa --natoms 5000
```

> ⚠️ 위 스크립트는 문서와 소스를 근거로 작성했고, 실제 RTX PRO 6000에서 끝까지 돌려 본 것은 아닙니다. 첫 설치 때는 단계별로 실행하면서 확인하세요.

## 참고
- SevenNet: https://github.com/MDIL-SNU/SevenNet · https://sevennet.readthedocs.io/en/latest/
- FlashTP: https://github.com/SNU-ARC/flashTP
- 관련 노트: [`../mlip-adsorption/README.md`](../mlip-adsorption/README.md) (SevenNet 중심 전구체 흡착 계산 준비 코스)
