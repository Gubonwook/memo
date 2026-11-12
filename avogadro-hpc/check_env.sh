#!/usr/bin/env bash
# HPC 환경 점검: 웹 뷰어 / Avogadro GUI 사용 가능 여부를 판정한다.
# 사용법:  bash check_env.sh
# 아무것도 설치/변경하지 않는다 (읽기 전용 점검).

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ok()   { printf "  [ OK ] %s\n" "$*"; }
no()   { printf "  [ -- ] %s\n" "$*"; }
info() { printf "         %s\n" "$*"; }

has_lib() {  # has_lib libGL.so.1
  if command -v ldconfig >/dev/null 2>&1 && ldconfig -p 2>/dev/null | grep -q "$1"; then return 0; fi
  for d in /usr/lib64 /usr/lib /usr/lib/x86_64-linux-gnu /usr/lib/aarch64-linux-gnu /lib64 /lib; do
    [ -e "$d/$1" ] && return 0
  done
  return 1
}

echo "================ 시스템 ================"
. /etc/os-release 2>/dev/null && info "OS      : ${PRETTY_NAME:-unknown}"
info "Arch    : $(uname -m)"
info "glibc   : $(ldd --version 2>/dev/null | head -1 | awk '{print $NF}')"
info "CPU     : $(nproc 2>/dev/null) cores, $(grep -m1 'model name' /proc/cpuinfo 2>/dev/null | cut -d: -f2 | xargs)"
info "RAM     : $(awk '/MemTotal/{printf "%.1f GB", $2/1048576}' /proc/meminfo 2>/dev/null)"
info "Host    : $(hostname)"

echo
echo "================ 1) 웹 뷰어 (권장) ================"
PY=""
for p in python3 python; do
  if command -v $p >/dev/null 2>&1 && $p -c 'import sys; sys.exit(0 if sys.version_info>=(3,6) else 1)' 2>/dev/null; then PY=$p; break; fi
done
if [ -n "$PY" ]; then
  ok "Python $($PY -c 'import platform;print(platform.python_version())') → 웹 뷰어 사용 가능"
  if $PY -c 'import ase' 2>/dev/null; then ok "ASE 설치됨 → OUTCAR / vasprun.xml / traj 도 열림"
  else no "ASE 없음 (선택). POSCAR/CONTCAR/XDATCAR/cif/xyz/cube 는 ASE 없이도 열림"; fi
  WEB=1
else
  no "Python 3.6+ 없음 → 웹 뷰어 불가"
  WEB=0
fi

echo
echo "================ 2) Avogadro GUI (선택) ================"
GUI=1
if [ -n "$DISPLAY" ]; then ok "DISPLAY=$DISPLAY"
else no "DISPLAY 없음 → 화면을 띄울 곳이 없음 (ssh -Y 로 X 포워딩 접속 필요)"; GUI=0; fi

for L in libGL.so.1 libEGL.so.1 libX11.so.6 libxcb.so.1 libfontconfig.so.1 libfreetype.so.6; do
  if has_lib "$L"; then ok "$L"; else no "$L 없음"; GUI=0; fi
done
if has_lib "swrast_dri.so" || ls /usr/lib*/dri/swrast_dri.so /usr/lib/*/dri/swrast_dri.so >/dev/null 2>&1 \
   || ls /usr/lib*/dri/llvmpipe_dri.so /usr/lib/*/dri/*_dri.so >/dev/null 2>&1; then
  ok "Mesa 소프트웨어 렌더러(DRI) 있음"
else
  no "Mesa 소프트웨어 렌더러(swrast/llvmpipe) 확인 안 됨"
fi
if [ -e /dev/fuse ]; then ok "FUSE 있음 (AppImage 직접 실행 가능)"
else info "FUSE 없음 → 괜찮음. avogadro/extract_appimage.sh 로 풀어서 실행"; fi

APP="$HERE/avogadro/Avogadro2/AppRun"
BIN="$(ls "$HERE"/avogadro/Avogadro2/usr/bin/avogadro2 2>/dev/null)"
if [ -n "$BIN" ]; then
  MISSING="$(LD_LIBRARY_PATH="$HERE/avogadro/Avogadro2/usr/lib:$LD_LIBRARY_PATH" ldd "$BIN" 2>/dev/null | grep 'not found' | awk '{print $1}' | sort -u)"
  if [ -z "$MISSING" ]; then ok "풀린 Avogadro 바이너리: 누락 라이브러리 없음"
  else no "풀린 Avogadro 바이너리 누락 라이브러리:"; echo "$MISSING" | sed 's/^/           - /'; GUI=0; fi
else
  info "Avogadro AppImage 아직 안 풀림 (avogadro/extract_appimage.sh 실행 후 다시 점검)"
fi

echo
echo "================ 판정 ================"
if [ "$WEB" = 1 ]; then
  echo "  웹 뷰어 : 사용 가능 →  $PY $HERE/viewer/serve.py <구조파일_폴더>"
else
  echo "  웹 뷰어 : 불가 (python3 필요)"
fi
if [ "$GUI" = 1 ]; then
  echo "  Avogadro: 사용 가능 →  bash $HERE/avogadro/run_avogadro.sh"
else
  echo "  Avogadro: 현재 불가 (위 [ -- ] 항목 참고). 관리자에게 mesa-libGL / libX11 설치 요청 또는 웹 뷰어 사용"
fi
