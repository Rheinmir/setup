#!/usr/bin/env bash
# bootstrap.sh — cài PoC vendor-neutral harness vào DỰ ÁN HIỆN TẠI bằng 1 dòng,
# KHÔNG cần clone repo. Tải lõi từ GitHub raw rồi gọi install.sh.
#
#   curl -fsSL https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral/bootstrap.sh | bash
#
# MẶC ĐỊNH = cài/update CẢ 3 TRỤ (harness + skills + llmwiki). Khỏi nhớ cờ gì.
#
# Kèm cờ (sau `bash -s --`):
#   ... | bash -s -- --harness-only   # CHỈ harness (bỏ skills + llmwiki)
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
# MẶC ĐỊNH: cài/UPDATE CẢ 3 TRỤ (harness + skills + llmwiki) — 1 lệnh, khỏi nhớ cờ.
# Opt-out: --harness-only (chỉ harness). Tự chỉ --with-skills/--with-wiki/--full → tôn trọng.
WANT_FULL=1; NEWARGS=()
for a in "$@"; do
  case "$a" in
    --harness-only) WANT_FULL=0;;
    --full|--with-skills|--with-wiki) WANT_FULL=0; NEWARGS+=("$a");;
    *) NEWARGS+=("$a");;
  esac
done
[ "$WANT_FULL" = 1 ] && NEWARGS+=(--full)
say "cài/update vào $TARGET $([ "$WANT_FULL" = 1 ] && echo '— CẢ 3 TRỤ' || echo '(harness-only)')"
# repo-root raw (strip /harness/poc-vendor-neutral) → install.sh tải overstack.html từ đúng nguồn/branch
export REPO_RAW="${BASE%/harness/poc-vendor-neutral}"
bash "$TMP/install.sh" "$TARGET" ${NEWARGS[@]+"${NEWARGS[@]}"}
