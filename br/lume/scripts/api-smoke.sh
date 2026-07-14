#!/usr/bin/env bash
# api-smoke — GATE THẬT cho các frame backend chưa có unit-test trong suite gốc.
#
# Vì sao tồn tại: 12 frame reverse từng để `acceptance_test: "(reverse)"` = KHÔNG CÓ GATE —
# frame "xanh" mà chưa bao giờ có ai kiểm. Frame không có gate là frame nói dối.
# Gate này gọi API THẬT trên server đang chạy và khẳng định 2 điều tối thiểu:
#   ① endpoint của vùng đó TỒN TẠI (không 404)  ② nó CÓ GÁC AUTH (ẩn danh không lọt)
# Không giả vờ test sâu — nói đúng thứ nó kiểm được.
#
# Dùng:  bash br/lume/scripts/api-smoke.sh <area> [base]
#        area ∈ shortcut | idp | instance | memo | user | attachment | auth
#   (KHÔNG có inbox/reaction: bản này KHÔNG có inbox_service/reaction_service proto —
#    reaction nằm trong memo_service, inbox chỉ có store+UI. Frame của chúng gate bằng go test / visual-qa.)
set -u
AREA="${1:?thiếu area}"; BASE="${2:-http://localhost:5230}"

case "$AREA" in
  shortcut)   EP="/api/v1/users/demo/shortcuts";   NEED_AUTH=1 ;;
  idp)        EP="/api/v1/identity-providers";      NEED_AUTH=0 ;;   # công khai: trang login cần liệt kê IdP
  instance)   EP="/api/v1/instance/profile";       NEED_AUTH=0 ;;   # công khai: SPA đọc profile trước khi login
  memo)       EP="/api/v1/memos";                  NEED_AUTH=0 ;;   # công khai: feed Explore
  user)       EP="/api/v1/users/demo/settings/GENERAL"; NEED_AUTH=1 ;;
  attachment) EP="/api/v1/attachments";            NEED_AUTH=1 ;;
  auth)       EP="/api/v1/auth/me";                NEED_AUTH=1 ;;
  *) echo "area không biết: $AREA"; exit 2 ;;
esac

CODE=$(curl -s -o /dev/null -w '%{http_code}' "$BASE$EP")
echo "[api-smoke] $AREA  $EP  → HTTP $CODE  (server: $BASE)"

# ① endpoint phải tồn tại
if [ "$CODE" = "000" ]; then echo "  ✗ server KHÔNG chạy ở $BASE"; exit 1; fi
if [ "$CODE" = "404" ]; then echo "  ✗ endpoint KHÔNG tồn tại (404) — frame khai một API không có thật"; exit 1; fi
if [ "$CODE" -ge 500 ]; then echo "  ✗ server lỗi $CODE"; exit 1; fi

# ② vùng cần auth thì ẩn danh KHÔNG được lọt
if [ "$NEED_AUTH" = "1" ] && [ "$CODE" = "200" ]; then
  echo "  ✗ LỖ AUTH: gọi ẩn danh mà vẫn 200 — dữ liệu riêng tư lộ ra"; exit 1
fi
if [ "$NEED_AUTH" = "1" ] && { [ "$CODE" = "401" ] || [ "$CODE" = "403" ]; }; then
  echo "  ✓ tồn tại + gác auth đúng ($CODE cho ẩn danh)"; exit 0
fi
if [ "$NEED_AUTH" = "0" ] && [ "$CODE" = "200" ]; then
  echo "  ✓ tồn tại + công khai đúng (200)"; exit 0
fi
echo "  ✗ mã trả về không như kỳ vọng (need_auth=$NEED_AUTH, got $CODE)"; exit 1
