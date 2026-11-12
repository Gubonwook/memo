#!/usr/bin/env bash
# GPU 없는 HPC에서 Avogadro 를 CPU(소프트웨어 OpenGL)로 실행한다.
# 전제: (1) extract_appimage.sh 로 풀어 둠, (2) ssh -Y 로 X 포워딩 접속 (DISPLAY 존재)
# 사용법: bash run_avogadro.sh [구조파일 ...]
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP="$HERE/Avogadro2/AppRun"

if [ ! -x "$APP" ]; then
  echo "Avogadro 가 아직 풀리지 않았습니다:  bash $HERE/extract_appimage.sh <AppImage 경로>"
  exit 1
fi
if [ -z "$DISPLAY" ]; then
  cat <<'EOF'
DISPLAY 가 비어 있어 창을 띄울 수 없습니다.
  - 데스크톱에서 X 서버가 있는 터미널(MobaXterm 등)로  ssh -Y user@hpc  접속 후 다시 실행
  - X 포워딩이 막혀 있으면 웹 뷰어를 쓰세요:  python3 ../viewer/serve.py <폴더>
EOF
  exit 1
fi

# --- GPU 없이 CPU로 OpenGL 렌더링 (Mesa llvmpipe/softpipe) ---
export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER="${GALLIUM_DRIVER:-llvmpipe}"
export LP_NUM_THREADS="${LP_NUM_THREADS:-4}"        # 렌더링 CPU 스레드 (로그인 노드 예의상 4)
unset LIBGL_ALWAYS_INDIRECT                          # 데스크톱 X서버로 GL 넘기지 않음
# Qt / X 포워딩 호환
export QT_XCB_GL_INTEGRATION="${QT_XCB_GL_INTEGRATION:-xcb_glx}"
export QT_X11_NO_MITSHM=1
export QT_QPA_PLATFORM=xcb
export QT_AUTO_SCREEN_SCALE_FACTOR=0

echo "Avogadro 실행 (software OpenGL, threads=$LP_NUM_THREADS) …"
echo "창이 안 뜨거나 바로 꺼지면:  bash $HERE/run_avogadro.sh --debug"
if [ "$1" = "--debug" ]; then
  shift
  export QT_DEBUG_PLUGINS=1 LIBGL_DEBUG=verbose MESA_DEBUG=1
fi
exec "$APP" "$@"
