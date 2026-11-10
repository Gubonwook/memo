#!/usr/bin/env bash
# SevenNet 설치 스크립트 — NVIDIA RTX PRO 6000 Blackwell (96GB, compute capability 12.0 / sm_120)
#
# 사용법:
#   bash setup_blackwell.sh                 # 기본: torch(cu128) + sevenn + cuEquivariance
#   WITH_FLASH=1 bash setup_blackwell.sh    # FlashTP까지 소스 빌드
#   WITH_TORCHSIM=1 WITH_OEQ=1 bash setup_blackwell.sh
#
# 전제:
#   - NVIDIA 드라이버 R570 이상 (Blackwell은 CUDA 12.8 이상 필요)
#   - conda(또는 mamba) 사용 가능
#   - D3 / FlashTP / LAMMPS 빌드를 하려면 nvcc 12.8 이상 (CUDA_HOME)
#
# 주의: 실제 RTX PRO 6000에서 끝까지 실행해 본 스크립트가 아닙니다.
#       단계별로 실행하고, 마지막에 check_env.py로 반드시 검증하세요.
set -euo pipefail

ENV_NAME="${ENV_NAME:-sevenn}"
PY_VER="${PY_VER:-3.12}"          # TorchSim은 Python >= 3.12 필요
CUDA_TAG="${CUDA_TAG:-cu128}"      # cu128 또는 cu130 (cu130이면 sevenn[cueq13], [mliap13] 사용)
WITH_CUEQ="${WITH_CUEQ:-1}"
WITH_FLASH="${WITH_FLASH:-0}"
WITH_OEQ="${WITH_OEQ:-0}"
WITH_TORCHSIM="${WITH_TORCHSIM:-0}"
WITH_MLIAP="${WITH_MLIAP:-0}"

say() { printf '\n\033[1;34m[%s]\033[0m %s\n' "$(date +%H:%M:%S)" "$*"; }

# ---------------------------------------------------------------- 0. GPU / 드라이버 확인
say "GPU / 드라이버 확인"
nvidia-smi --query-gpu=name,driver_version,compute_cap,memory.total --format=csv
CC=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader | head -1 | tr -d ' ')
if [[ "$CC" != "12.0" ]]; then
  echo "경고: compute capability가 12.0이 아닙니다 ($CC). Blackwell 워크스테이션 GPU가 맞는지 확인하세요."
fi

# ---------------------------------------------------------------- 1. conda 환경
say "conda 환경 생성: $ENV_NAME (python $PY_VER)"
eval "$(conda shell.bash hook)"
if ! conda env list | grep -qE "^${ENV_NAME}\s"; then
  conda create -y -n "$ENV_NAME" "python=${PY_VER}"
fi
conda activate "$ENV_NAME"

# ---------------------------------------------------------------- 2. PyTorch (sm_120 포함 빌드)
# cu126 이하 휠에는 sm_120 커널이 없어 "sm_120 is not compatible" 오류가 납니다.
say "PyTorch 설치 (${CUDA_TAG})"
pip install --upgrade pip
pip install torch --index-url "https://download.pytorch.org/whl/${CUDA_TAG}"
python - <<'EOF'
import torch
archs = torch.cuda.get_arch_list()
print("torch", torch.__version__, "| CUDA", torch.version.cuda, "| archs", archs)
assert torch.cuda.is_available(), "CUDA를 찾지 못했습니다"
assert "sm_120" in archs, "이 PyTorch 빌드에 sm_120 커널이 없습니다 (cu128 이상 휠 필요)"
print("GPU:", torch.cuda.get_device_name(0), torch.cuda.get_device_capability(0))
EOF

# ---------------------------------------------------------------- 3. SevenNet
say "SevenNet 설치"
pip install sevenn

# D3(ASE), pair_e3gnn 등 JIT 컴파일 대상 아키텍처를 Blackwell로 고정
export TORCH_CUDA_ARCH_LIST="12.0"
grep -q 'TORCH_CUDA_ARCH_LIST="12.0"' ~/.bashrc 2>/dev/null || \
  echo 'export TORCH_CUDA_ARCH_LIST="12.0"   # SevenNet D3/FlashTP JIT for RTX PRO 6000' >> ~/.bashrc

# ---------------------------------------------------------------- 4. 가속기 (선택)
CU_MAJOR="${CUDA_TAG:2:2}"   # cu128 -> 12, cu130 -> 13

if [[ "$WITH_CUEQ" == "1" ]]; then
  say "cuEquivariance 설치 (sevenn[cueq${CU_MAJOR}])"
  pip install "sevenn[cueq${CU_MAJOR}]"
fi

if [[ "$WITH_OEQ" == "1" ]]; then
  say "OpenEquivariance 설치"
  pip install "sevenn[oeq]"
fi

if [[ "$WITH_FLASH" == "1" ]]; then
  say "FlashTP 소스 빌드 (CUDA_ARCH_LIST=120, nvcc >= 12.8 필요)"
  command -v nvcc >/dev/null || { echo "nvcc가 없습니다. CUDA toolkit 12.8+를 설치하고 CUDA_HOME을 지정하세요."; exit 1; }
  nvcc --version | tail -2
  WORK="${WORK:-$HOME/src}"; mkdir -p "$WORK"; cd "$WORK"
  [[ -d flashTP ]] || git clone https://github.com/SNU-ARC/flashTP.git
  cd flashTP
  pip install -r requirements.txt
  # 컴파일 중 메모리 부족(exit 137)이 나면 MAX_JOBS를 줄이세요
  MAX_JOBS="${MAX_JOBS:-8}" CUDA_ARCH_LIST="120" pip install . --no-build-isolation
  cd - >/dev/null
fi

if [[ "$WITH_TORCHSIM" == "1" ]]; then
  say "TorchSim 설치"
  pip install "sevenn[torchsim]"
fi

if [[ "$WITH_MLIAP" == "1" ]]; then
  say "LAMMPS ML-IAP용 Python 의존성 설치 (LAMMPS 빌드는 README 참고)"
  pip install "sevenn[mliap${CU_MAJOR}]"
fi

say "완료. 다음으로 검증을 실행하세요:  python check_env.py"
