#!/usr/bin/env bash
# 웹 뷰어 실행 바로가기
# 사용법: bash start_viewer.sh [구조파일_폴더] [포트]
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIR="${1:-$PWD}"
PORT="${2:-8765}"
PY="$(command -v python3 || command -v python)"
[ -z "$PY" ] && { echo "python3 가 필요합니다."; exit 1; }
exec "$PY" "$HERE/viewer/serve.py" "$DIR" --port "$PORT"
