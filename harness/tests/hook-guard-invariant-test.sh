#!/usr/bin/env bash
# hook-guard-invariant-test — RÀO TỰ-CẮN chống tái phát đệ quy self-test (GH#30).
#
# Bất-biến: MỌI git-op sinh-hook (commit/push/merge/rebase/am) chạy LỒNG trong
# self-test harness PHẢI vô hiệu hook — nếu không, self-test bị nối lại vào một
# commit-time hook sẽ tự-kích đệ quy bùng nổ (đã cháy thật phiên ship GH#8).
# Cửa hợp lệ: dòng có `--no-verify` HOẶC `core.hooksPath=/dev/null`.
#
# Đây là guard chống CON NGƯỜI QUÊN: council (report-027) chốt rào tự-động mới
# nhớ, sửa tay sẽ rò lần sau. Test này fail nếu ai thêm git-op trần vào tests/.
#
# Usage: bash harness/tests/hook-guard-invariant-test.sh [repo-root]   (exit 0 = pass)
set -u
ROOT="$(cd "${1:-.}" && pwd)"
TDIR="$ROOT/harness/tests"
viol=0

# git-op sinh-hook; loại các dạng KHÔNG chạy hook (add/init/config/remote/rev-parse/
# branch/clone/fetch/log/status/rm/reset/checkout/stash/diff/show/tag/-C ... list).
while IFS= read -r line; do
  # bỏ chính test này + comment
  case "$line" in \#*) continue;; esac
  file="${line%%:*}"; rest="${line#*:}"; lineno="${rest%%:*}"; code="${rest#*:}"
  case "$file" in *hook-guard-invariant-test.sh) continue;; esac
  if printf '%s' "$code" | grep -qE '\bgit +(-[^ ]+ +)*(commit|push|merge|rebase|am)\b'; then
    if ! printf '%s' "$code" | grep -qE 'no-verify|hooksPath'; then
      printf '  \033[1;31m✗\033[0m git-op sinh-hook TRẦN: %s:%s\n' "${file#$ROOT/}" "$lineno"
      printf '      %s\n' "$(printf '%s' "$code" | sed 's/^[[:space:]]*//')"
      viol=$((viol+1))
    fi
  fi
done < <(grep -rnE '\bgit +' "$TDIR" 2>/dev/null)

if [ "$viol" -eq 0 ]; then
  printf '  \033[1;32m✓\033[0m mọi git-op sinh-hook trong harness/tests/ đều vô hiệu hook (no-verify|hooksPath)\n'
  printf '\n\033[1m═══ hook-guard-invariant: \033[1;32mPASS\033[0m\033[0m\n'
  exit 0
fi
printf '\n\033[1m═══ hook-guard-invariant: \033[1;31m%d VI PHẠM\033[0m — thêm `--no-verify` hoặc `-c core.hooksPath=/dev/null`\033[0m\n' "$viol"
exit 1
