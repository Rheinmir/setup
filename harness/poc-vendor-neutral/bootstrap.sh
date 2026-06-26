#!/usr/bin/env bash
# bootstrap.sh — cài PoC vendor-neutral harness vào DỰ ÁN HIỆN TẠI bằng 1 dòng,
# KHÔNG cần clone repo. Tải lõi từ GitHub raw rồi gọi install.sh.
#
#   curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/bootstrap.sh | bash
#
# Kèm cờ (sau `bash -s --`):
#   ... | bash -s -- --vendor claude,opencode
#   ... | bash -s -- --clean          # cài mới = gỡ cũ rồi cài
#   ... | bash -s -- --no-verify
#
# Đổi nguồn/branch: HARNESS_BASE=https://raw.githubusercontent.com/<owner>/<repo>/<branch>/harness/poc-vendor-neutral
set -euo pipefail
BASE="${HARNESS_BASE:-https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral}"
TARGET="$PWD"
say(){ printf '\033[1;36m[bootstrap]\033[0m %s\n' "$*"; }
command -v curl >/dev/null || { echo "cần curl" >&2; exit 1; }
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
mkdir -p "$TMP/bin"
say "tải lõi từ $BASE"
for f in policy.yaml gen-converters.py demo.sh test-broad.sh install.sh uninstall.sh bin/llmwiki-validate.py bin/harness-events.py; do
  curl -fsSL "$BASE/$f" -o "$TMP/$f" || { echo "tải lỗi: $f" >&2; exit 1; }
done
chmod +x "$TMP"/*.sh "$TMP/bin/llmwiki-validate.py" 2>/dev/null || true
say "cài vào $TARGET"
bash "$TMP/install.sh" "$TARGET" "$@"
