# SevenNet 코드 분석 & 사용 가이드 (격리 서버 · 전구체 흡착/반응 에너지)

2026-11-17 · **sevenn 0.13.0 소스(wheel)를 직접 읽고, 이 문서의 명령을 CPU에서 실제로 돌려 확인**했습니다. 확인하지 못한 부분은 "미검증"이라고 적었습니다.

## 0. 요약

1. **설치:** sevenn과 의존성은 모두 PyPI에 있으므로 사내 Nexus pip로 설치할 수 있습니다. 체크포인트만 이 폴더의 `ckpt/`에서 반입하면 됩니다.
2. **인터넷이 필요한 곳은 한 군데뿐입니다.** `model='7net-omni'`처럼 **키워드**를 썼는데 파일이 없을 때 GitHub에서 다운로드를 시도합니다. → **항상 파일 경로**를 넘기거나, `verify_offline.py --install`로 키워드 위치에 미리 넣어 두세요.
3. **D3는 GPU 전용이고, 처음 쓸 때 nvcc로 CUDA 코드를 컴파일합니다.** 서버에 CUDA toolkit(nvcc)이 있어야 합니다.
4. **modal 이름은 대소문자를 구분합니다.** 문서에는 "case insensitive"라고 되어 있지만 실제 코드는 정확히 일치해야 합니다(`'OC22'` → 오류).
5. **Fine-tuning:** `sevenn cp ... --get_yaml continue`가 만든 yaml은 0.13.0에서 **그대로는 안 돌아갑니다**(오류 4개). 고친 템플릿 [`finetune_omni.yaml`](finetune_omni.yaml)을 쓰세요.

| 파일 | 용도 | 동작 확인 |
|---|---|---|
| `reaction_energy.py` | 흡착·반쪽반응 ΔE, modal 비교 | ✅ |
| `neb_example.py` | NEB 장벽 | ✅ |
| `finetune_omni.yaml` | 내 VASP 데이터로 fine-tuning | ✅ |
| `verify_offline.py` | 조각 합치기·해시·로드·키워드 설치 | ✅ |

---

## 1. 설치 (격리 서버, Nexus pip)

```bash
# 1) torch: 서버 CUDA 버전에 맞게. Nexus가 download.pytorch.org를 프록시하지 않으면
#    PyPI 기본 torch(리눅스는 CUDA 포함 빌드)를 받게 됨 → 드라이버 버전과 맞는지 확인
pip install torch
# 2) SevenNet (의존성: ase, e3nn, torch_geometric, matscipy, pandas, scikit-learn, ninja 등 전부 PyPI)
pip install sevenn==0.13.0
# 3) 확인
python -c "import sevenn, torch; print(sevenn.__version__, torch.cuda.is_available())"
```

선택 패키지(속도 향상용, 없어도 결과는 같음):

| 가속기 | 설치 | 비고 |
|---|---|---|
| cuEquivariance | `pip install sevenn[cueq12]` (CUDA 12) / `[cueq13]` | PyPI에 있음 → Nexus로 가능 |
| FlashTP | GitHub 소스 빌드 | 소스를 반입해야 함 |
| OpenEquivariance | `pip install sevenn[oeq]` | PyPI |
| TorchSim(대량 배치) | `pip install sevenn[torchsim]` (Python ≥3.12) | PyPI |

가속기는 `enable_cueq=True` 같은 인자나 환경변수 `SEVENNET_ENABLE_CUEQ=1`, `SEVENNET_ENABLE_FLASH=1`, `SEVENNET_ENABLE_OEQ=1`로 켭니다. 요청한 가속기가 설치되어 있지 않으면 **경고만 내고 e3nn으로 돌아갑니다**(`checkpoint._solve_accelerator`). Omni 체크포인트는 FlashTP로 저장되어 있어서 로드할 때 "Converting model backend..."가 뜨는데, 정상입니다.

## 2. 코드 구조 지도

| 모듈 | 역할 | 알아둘 점 |
|---|---|---|
| `calculator.py` | `SevenNetCalculator`, `SevenNetD3Calculator`, `D3Calculator` (ASE) | 주로 쓰는 API |
| `util.py` | `load_checkpoint`, `pretrained_name_to_path`, `download_checkpoint` | **유일한 네트워크 접근 지점** |
| `_const.py` | 체크포인트 경로·다운로드 URL·기본 설정값 | |
| `checkpoint.py` | `SevenNetCheckpoint`: 로드, `build_model`, `yaml_dict`(get_yaml), `append_modal` | fine-tuning의 핵심 |
| `model_build.py`, `nn/` | E(3)-equivariant 모델(NequIP 구조) 구성 | 건드릴 일 없음 |
| `train/` | 데이터셋(`graph_dataset`, `modal_dataset`), trainer, loss | |
| `main/` | CLI: `sevenn train/cp/inference/graph_build/preset/get_model/patch_lammps` | |
| `torchsim.py`, `batch_d3.py` | TorchSim 배치 계산 + 배치 D3 | 수천 구조 스크리닝용 |
| `mliap.py`, `pair_e3gnn/` | LAMMPS 연동 (C++/CUDA) | MD를 크게 돌릴 때 |
| `presets/` | 학습 yaml 예시(`fine_tune`, `mf_ompa_fine_tune`, `reewc` 등) | `sevenn preset <이름>` |

## 3. 체크포인트 로딩 동작 (오프라인에서 가장 중요)

`SevenNetCalculator(model=X)` → `util.load_checkpoint(X)`의 순서는 다음과 같습니다.

1. **`X`가 실제 파일이면** 그 파일을 씁니다. → 네트워크 접근 없음 ✅
2. 파일이 아니면 키워드로 해석합니다(`7net-omni`, `sevennet-omni`, `7net-omni-i8`, `7net-mf-ompa`, `7net-0` …, 대소문자 무시). 그다음 아래 두 위치를 차례로 찾습니다.
   - `<site-packages>/sevenn/pretrained_potentials/SevenNet_omni/checkpoint_sevennet_omni.pth`
   - `~/.cache/sevennet/SevenNet_omni/checkpoint_sevennet_omni.pth`
3. 두 곳 모두 없으면 **GitHub Releases에서 `requests.get`(timeout 30 s)으로 다운로드를 시도** → 격리망에서는 실패합니다.

`7net-0`, `7net-l3i5`, `7net-mf-0`은 wheel 안에 포함되어 있어서 3단계까지 가지 않습니다.
→ `python verify_offline.py --dir ckpt --install`은 패키지 폴더에 쓰기 권한이 없으면 `~/.cache/sevennet/`에 복사합니다.

## 4. 계산기 API

```python
from sevenn.calculator import SevenNetCalculator
calc = SevenNetCalculator(
    model="ckpt/checkpoint_sevennet_omni.pth",  # 경로 권장
    modal="oc22",          # 멀티모달 모델은 필수. 대소문자 정확히
    device="auto",         # cuda 있으면 cuda
    enable_cueq=False, enable_flash=False, enable_oeq=False,
)
atoms.calc = calc
atoms.get_potential_energy()   # eV
atoms.get_forces()             # eV/Å
atoms.get_stress()             # ASE 규약(eV/Å³, Voigt)
atoms.get_potential_energies() # 원자별 에너지(모델 분해값, 물리량 아님)
```

- 모델이 모르는 원소가 들어오면 `set_atoms`에서 바로 오류가 납니다. Omni는 119개 원소 전부를 지원합니다.
- `modal`을 빠뜨리면 사용 가능한 목록을 보여 주며 오류가 납니다.
- PBC가 없는 분자(셀 0)도 그래프는 만들어지지만, 이 폴더의 스크립트는 일관성을 위해 상자에 넣고 PBC를 켭니다.
- ASE 계산기는 **멀티 GPU를 지원하지 않습니다**(docstring 명시). 큰 MD는 LAMMPS로 돌리세요.

### D3 (분산 보정)

```python
from sevenn.calculator import SevenNetD3Calculator
calc = SevenNetD3Calculator(model=CK, modal="oc22",
                            damping_type="damp_bj", functional_name="pbe")
```

- 내부적으로 `SumCalculator([SevenNet, D3])`이고, D3는 **CUDA 전용**입니다(CPU에서는 `NotImplementedError`).
- **처음 실행할 때 `pair_d3_for_ase.cu`를 nvcc로 JIT 컴파일**합니다(`torch.utils.cpp_extension.load` + ninja). 그래서 다음이 필요합니다.
  - GPU가 보이는 노드에서 실행할 것(`torch.cuda.get_device_capability()`를 호출함)
  - torch의 CUDA 버전과 맞는 nvcc
  - 결과 `.so`는 패키지 폴더(쓰기 가능할 때) 또는 `~/.cache/torch_extensions/`에 저장되고, 이후에는 재사용됩니다.
  - Blackwell(sm_120) 등 기본 목록 밖의 GPU는 감지된 arch가 자동으로 추가됩니다. 직접 지정하려면 `TORCH_CUDA_ARCH_LIST="12.0"`.
- **modal과 D3 functional을 맞추세요.**

  | modal | D3 functional |
  |---|---|
  | `omat24`, `mpa`, `matpes_pbe`, `oc22` | `pbe` |
  | `oc20` (RPBE) | `rpbe` (지원 목록에 있음) |
  | `omol25_*` | D3 넣지 말 것(ωB97M-V, 이미 VV10 포함) |

- 이 세션은 GPU가 없어 **D3 경로는 실행해 보지 못했습니다(미검증).**

## 5. 용도별 레시피

### 5-A. 흡착·반응 에너지
[`README.md`](README.md) 2–3절과 `reaction_energy.py`를 참고하세요. 요점: 모든 항을 같은 modal·같은 D3 설정으로 계산하고, 여러 modal을 비교한 뒤 DFT로 고릅니다.

### 5-B. NEB (반쪽반응 장벽)
```bash
python neb_example.py --ckpt ckpt/checkpoint_sevennet_omni.pth --modal oc22 \
    --initial IS.vasp --final FS.vasp --nimages 7
```
계산기 하나를 모든 image가 공유합니다(`allow_shared_calculator=True`). 이전에 Matlantis로 만든 TEMAHf/HZO 단계별 NEB 워크플로가 있다면, 계산기 생성 줄만 위 `SevenNetCalculator(...)`로 바꾸면 됩니다. ASE 인터페이스가 같기 때문입니다.

### 5-C. 내 DFT 결과와 대량 비교 (modal 선택용) ← 가장 먼저 할 일
```bash
# VASP OUTCAR/vasprun.xml/extxyz를 그대로 넣으면 DFT 구조에서 단일점 계산
sevenn inference ckpt/checkpoint_sevennet_omni.pth OUTCAR_* -m oc22 -d cuda -o inf_oc22
sevenn inference ckpt/checkpoint_sevennet_omni.pth OUTCAR_* -m omat24 -d cuda -o inf_omat24
```
결과는 `per_graph.csv`(DFT `total_energy`와 예측 `inferred_total_energy`), `per_atom.csv`(힘 비교), `errors.txt`입니다. **총에너지는 modal마다 기준점이 달라서 절대값으로 비교하면 안 됩니다.** 같은 계에서 **흡착 에너지(차이값)**를 만들어 비교하세요. 라벨이 없는 파일은 `-au`를 붙입니다.

### 5-D. MD (ASE)
```python
from ase.md.langevin import Langevin
from ase import units
atoms.calc = calc
Langevin(atoms, 1*units.fs, temperature_K=500, friction=0.01).run(10000)
```
수천 원자·ns 단위라면 LAMMPS를 쓰세요(5-F).

### 5-E. 대량 스크리닝 (TorchSim, 미검증)
`sevenn.torchsim.SevenNetModel` / `SevenNetD3Model`은 여러 구조를 한 번에 GPU 배치로 완화·MD합니다(D3도 배치 커널). `pip install sevenn[torchsim]`이 필요하며, 이 세션에서는 설치·실행하지 않았습니다.

### 5-F. LAMMPS
```bash
sevenn get_model ckpt/checkpoint_sevennet_omni.pth -m oc22          # deployed_serial.pt
sevenn get_model ckpt/checkpoint_sevennet_omni.pth -m oc22 -p       # 멀티 GPU용
sevenn patch_lammps /path/to/lammps --d3                            # LAMMPS 소스에 pair_style 추가 후 빌드
```
modal은 deploy할 때 고정됩니다. LAMMPS 소스 tarball은 반입해야 합니다. **미검증**입니다.

## 6. Fine-tuning (내 VASP 데이터)

### 데이터 준비
VASP OUTCAR나 vasprun.xml을 그대로 쓸 수 있습니다(ASE가 읽음). 하나로 모으려면 이렇게 합니다.
```python
from ase.io import read, write
frames = []
for f in ["run1/OUTCAR", "run2/OUTCAR"]:
    frames += read(f, index=":")      # 완화 경로 전체 = 학습 데이터
write("train.extxyz", frames)
```
흡착체, 깨끗한 slab, 기체 분자, 반응 중간체를 모두 섞어 넣어야 흡착·반응 에너지가 맞습니다. 분자만 빠지면 E_ads 오차가 그대로 남습니다.

### 6-A. 기존 modal에 이어 학습 (권장, 간단)
**내 VASP 설정이 특정 modal의 DFT와 같을 때**(예: PBE, PAW_PBE, MP식 U) 그 modal 이름으로 학습합니다.
```bash
cp finetune_omni.yaml my_ft.yaml   # [수정] 줄만 바꿈: data_modality, 파일 경로, epoch
sevenn train my_ft.yaml -s
# 결과: checkpoint_best.pth → SevenNetCalculator("checkpoint_best.pth", modal="oc22")
```

### 6-B. 새 modal 추가 (설정이 다를 때: D3 포함 에너지, 다른 U, r²SCAN 등)
```bash
# 1) my_ft.yaml에서 data_modality를 새 이름(my_vasp)으로, shift/scale 주석 해제
# 2) 기존 13개 modal을 유지한 채 새 modal 가중치를 추가한 체크포인트 생성
sevenn cp ckpt/checkpoint_sevennet_omni.pth --append_modal_yaml my_ft.yaml
#    → checkpoint_modal_appended.pth
# 3) my_ft.yaml의 continue.checkpoint를 checkpoint_modal_appended.pth로 바꾸고 학습
sevenn train my_ft.yaml -s
# 4) SevenNetCalculator("checkpoint_best.pth", modal="my_vasp")
```

### get_yaml 출력을 직접 쓸 때 고쳐야 하는 4가지 (0.13.0 버그, 실제로 겪음)
`sevenn cp <ckpt> --get_yaml continue > x.yaml`의 출력은 다음 4곳을 고쳐야 돌아갑니다. `finetune_omni.yaml`에는 이미 반영되어 있습니다.

| 증상 | 원인 | 수정 |
|---|---|---|
| `Given input 'custom' for 'dataset_type' is not valid` | 무효값 출력 | `dataset_type: graph` |
| `'dict' object has no attribute 'lower'` | Omni의 dict형 loss를 파서가 못 읽음 | `loss: Huber`, `loss_param: {delta: 0.01}` |
| `_read_dict() got an unexpected keyword argument 'index'` | modal별 dict 입력에 `data_format_args.index` | `data_format_args: {}` |
| FlashTP 미설치 시 문제 가능 | `use_flash_tp: true`로 저장됨 | `use_flash_tp: false` |

그 밖에 원본 학습용 `scheduler: onecyclelr`(total_steps 175만)와 `batch_size: 256`도 바꿔야 합니다.

### 이 세션의 테스트 결과와 주의점
- EMT로 라벨을 붙인 Pt+H₂O 장난감 데이터 20개로 **6-A, 6-B 모두 학습이 끝까지 돌고, 결과 체크포인트를 계산기로 불러오는 것까지 확인**했습니다(CPU, epoch당 약 1분, 25.8M 파라미터).
- 다만 EMT 에너지는 DFT와 기준점이 전혀 달라서, 2 epoch 후에도 에너지 MAE가 수 eV/atom이었습니다. **즉 파이프라인이 돈다는 확인일 뿐, 정확도 검증은 아닙니다.**
- 실제 VASP 데이터로 할 때는 **epoch 1 직후의 Energy MAE를 꼭 보세요.**
  - 0.0x eV/atom 수준: modal 선택이 맞은 것입니다.
  - 수 eV/atom: 에너지 기준이 다른 것이므로 6-B(새 modal + shift)로 가야 합니다.
- 6-B에서 조성이 다양한 데이터라면 `shift: elemwise_reference_energies`가 더 적합할 것으로 보이지만 **미검증**입니다. 같은 조성만 있으면 회귀가 불가능하므로 `per_atom_energy_mean`을 쓰세요.
- 사전학습 지식이 지워지는 것(catastrophic forgetting)을 막고 싶으면 `sevenn preset reewc`(replay + EWC)를 참고하세요. 단, 이 preset은 single-modal 모델용입니다.

## 7. 반입 체크리스트

- [ ] `sevennet-checkpoints/` 폴더 전체(ckpt 조각, 스크립트, 템플릿)
- [ ] pip: `torch`, `sevenn==0.13.0` (Nexus) — 버전을 이 문서와 맞추기
- [ ] D3를 쓸 경우: GPU 노드 + nvcc(CUDA toolkit), `ninja`(sevenn 의존성으로 설치됨)
- [ ] (선택) FlashTP 소스, LAMMPS 소스
- [ ] 첫 실행: `python verify_offline.py --dir ckpt --install` → README 4절 표와 같은 숫자가 나오는지 확인

## 8. 이 세션에서 실제로 실행한 것

| 항목 | 결과 |
|---|---|
| 3개 체크포인트 해시·로드, 4개 modal 단일점 | ✅ |
| `reaction_energy.py` (완화 포함, 3 modal) | ✅ |
| `neb_example.py` (H fcc→hcp, Pt(111), oc20) | ✅ Ea 0.062 eV |
| `sevenn inference` (extxyz, -m oc22) | ✅ csv 출력 |
| fine-tune 6-A (`finetune_omni.yaml`) / 6-B (append_modal → train → 로드) | ✅ (장난감 데이터) |
| modal 대소문자 | ❌ `OC22` 거부 확인 |
| D3, FlashTP/cuEq, TorchSim, LAMMPS | 미검증 (GPU·패키지 없음) |

환경: CPU, torch 2.15.0, Python 3.13, sevenn 0.13.0.
