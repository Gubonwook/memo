#!/usr/bin/env bash
# Avogadro AppImage 를 FUSE 없이 풀어 둔다 (root 권한 불필요).
# 사용법:  bash extract_appimage.sh /path/to/Avogadro2-x86_64.AppImage
# 결과  :  이 폴더 아래 Avogadro2/ 생성 → run_avogadro.sh 로 실행
set -e
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

IMG="$1"
if [ -z "$IMG" ]; then
  IMG="$(ls "$HERE"/*.AppImage "$HERE"/../*.AppImage 2>/dev/null | head -1)"
fi
if [ -z "$IMG" ] || [ ! -f "$IMG" ]; then
  echo "AppImage 파일을 찾을 수 없음."
  echo "사용법: bash $0 /path/to/Avogadro2-x86_64.AppImage"
  exit 1
fi
IMG="$(cd "$(dirname "$IMG")" && pwd)/$(basename "$IMG")"

ARCH="$(uname -m)"
case "$(basename "$IMG")" in
  *aarch64*|*arm64*) [ "$ARCH" = "aarch64" ] || { echo "ARM64용 AppImage인데 이 머신은 $ARCH 입니다."; exit 1; } ;;
  *x86_64*)          [ "$ARCH" = "x86_64" ]  || { echo "x86_64용 AppImage인데 이 머신은 $ARCH 입니다."; exit 1; } ;;
esac

chmod +x "$IMG"
WORK="$(mktemp -d "$HERE/.extract.XXXXXX")"
echo "[1/2] 압축 해제 중: $IMG"
( cd "$WORK" && "$IMG" --appimage-extract >/dev/null ) || {
  echo "  --appimage-extract 실패. unsquashfs 로 재시도…"
  if command -v unsquashfs >/dev/null 2>&1; then
    OFF="$("$IMG" --appimage-offset 2>/dev/null || true)"
    if [ -n "$OFF" ]; then ( cd "$WORK" && unsquashfs -q -o "$OFF" -d squashfs-root "$IMG" ); else echo "  offset 확인 실패"; exit 1; fi
  else
    echo "  unsquashfs 도 없음. 홈 폴더가 noexec 마운트인지 확인하세요 (mount | grep \$HOME)."
    exit 1
  fi
}

rm -rf "$HERE/Avogadro2"
mv "$WORK/squashfs-root" "$HERE/Avogadro2"
rm -rf "$WORK"
echo "[2/2] 완료: $HERE/Avogadro2"
echo
echo "다음 단계:"
echo "  bash $(dirname "$HERE")/check_env.sh     # 누락 라이브러리 점검"
echo "  bash $HERE/run_avogadro.sh [구조파일]     # 실행 (X 포워딩 접속 상태에서)"
