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
#   ... | bash -s -- --no-graph       # KHÔNG kéo module orca-graph (repo riêng Rheinmir/orca-graph)
#
# Module orca-graph: mặc định ĐÃ TICK. Chạy trong terminal → hiện checklist, Enter là kéo đủ (gõ số để bỏ tick);
# agent/CI chạy (không terminal) → kéo luôn, không hỏi. Đổi nhánh/tag engine: ORCA_GRAPH_REF=<ref>.
#
# Đổi nguồn/branch: HARNESS_BASE=https://raw.githubusercontent.com/<owner>/<repo>/<branch>/harness/poc-vendor-neutral
set -euo pipefail
# Windows (Git Bash + Python native): stdout mặc định cp1252/cp437 → mọi print tiếng Việt/“→” crash UnicodeEncodeError
# giữa chừng cài (GH#168, GH#169). Ép UTF-8 cho MỌI python con của installer; Linux/macOS vốn UTF-8 nên không đổi gì.
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
BASE="${HARNESS_BASE:-https://raw.githubusercontent.com/Rheinmir/setup/orca/harness/poc-vendor-neutral}"
TARGET="$PWD"
say(){ printf '\033[1;36m[bootstrap]\033[0m %s\n' "$*"; }
command -v curl >/dev/null || { echo "cần curl" >&2; exit 1; }
# GH#169 A: trong cmd/PowerShell, `bash` thường là WSL bash → $HOME=/home/<user> (filesystem WSL). Nếu Claude Code là bản
# WINDOWS (claude.exe) thì nó chỉ đọc C:\Users\<user>\.claude — skills/hook/orca-graph cài vào WSL coi như mất. Cảnh báo to, không chặn
# (người dùng Claude Code bản Linux TRONG WSL là trường hợp hợp lệ). Bỏ cảnh báo: OVERSTACK_WSL_OK=1.
if [ -z "${OVERSTACK_WSL_OK:-}" ] && grep -qi microsoft /proc/version 2>/dev/null && ! command -v claude >/dev/null 2>&1 \
   && for c in /mnt/c/Users/*/.local/bin/claude.exe /mnt/c/Users/*/AppData/Roaming/npm/claude.cmd; do [ -e "$c" ] && break; c=""; done && [ -n "$c" ]; then
  # (bản đầu dùng `ls a b` → rc≠0 khi THIẾU một trong hai → cảnh báo chỉ hiện khi máy có CẢ hai bản Claude — review t8 #5)
  printf '\033[1;33m[bootstrap] CẢNH BÁO:\033[0m đang chạy trong WSL (HOME=%s) nhưng Claude Code là bản Windows.\n' "$HOME" >&2
  printf '  Phần global (skills, hook, orca-graph) sẽ vào HOME của WSL — Claude Code Windows KHÔNG thấy.\n' >&2
  printf '  Cài đúng: mở PowerShell và chạy bằng Git Bash:\n' >&2
  printf '    curl.exe -fsSL %s/bootstrap.sh | & "C:\\Program Files\\Git\\bin\\bash.exe"\n' "$BASE" >&2
  printf '  Cố ý dùng Claude Code trong WSL → đặt OVERSTACK_WSL_OK=1 để tắt cảnh báo.\n' >&2
fi
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
