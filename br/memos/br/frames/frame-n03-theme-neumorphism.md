---
schema_version: 0
frame_id: frame-n03-theme-neumorphism
created_by: human
kind: frame
parent_br: br/BR.md
clause_ids: [N03]
parent_br_hash: reverse-no-hash
muc_tieu: "Build lại UI memos theo system theme neumorphism của dây chuyền, đạt AAA contrast và accent đối-nghịch-nền"
scope_code: ["web/src/themes/neumorphism.css","web/src/index.css","web/src/components/MemosLogo.tsx","web/src/components/UserAvatar.tsx","web/src/components/Placeholder/index.tsx","web/src/pages/SignIn.tsx"]
scope_test: ["(gate = visual-qa --assert)"]
acceptance_test: "node skills/visual-qa/assets/route-shots.mjs --base http://localhost:5230 --assert --user demo --pass demo --out br/memos/qa-gate --baseline br/memos/qa-baseline"
ui_role: screen
ui_screen:
---
# frame-n03-theme-neumorphism

## Nghiệp vụ

Frame THEME: quyết định toàn bộ diện mạo Lume. Mọi thay đổi UI (token màu, bóng, brand, empty-state)
phải đi qua frame này — **cấm sửa tay ngoài `/br run`** (đã vi phạm 2 lần → quyết định thất lạc, lỗi vỡ lại).

## Input / Output

- **Input:** token shadcn của memos (`themes/default.css`), component brand (logo/avatar/placeholder).
- **Output:** `themes/neumorphism.css` override + component rebrand → UI đạt gate `visual-qa --assert`.

## Tiêu chí nghiệm thu (ĐỊNH LƯỢNG — máy chấm, không cảm tính)

Gate = `visual-qa --assert`. FAIL cứng khi vi phạm bất kỳ điều nào:

1. **contrast: bar là AAA `7:1`, KHÔNG phải AA `4.5:1`.**
   Bài học 13/07/26: pass ở SÀN AA vẫn ra giao diện **"chìm"** — user nhìn phát biết ngay.
   *Sàn a11y ≠ đủ tương phản để đọc thoải mái.* (Chữ lớn ≥24px, hoặc ≥18.66px bold: 4.5:1.)
2. **monochrome-surface:** mọi pane lớn (sidebar/aside/nav) phải CÙNG `background-color` với body
   → phải override cả token RIÊNG của memos: `--sidebar*` (quên là sidebar giữ màu kem gốc).
3. **baseline diff = 0%:** thay đổi ngoài ý muốn đều FAIL; đổi cố ý → duyệt bằng `--update-baseline`.
4. **Không route nào là vùng mù:** gate chụp cả trạng thái **chưa-đăng-nhập** (trang sign-in).
5. **THEME LÀ MỘT TRẠNG THÁI, không phải tuỳ chọn:** mỗi route phải chụp + audit **CẢ light VÀ dark**.
   App bật dark bằng class `.dark` trên `<html>` (theo setting app), KHÔNG theo `prefers-color-scheme`
   ⇒ headless mặc định **chỉ bao giờ thấy light** ⇒ dark là vùng mù tuyệt đối. Bật ra: **172 chỗ**
   vi phạm AAA ở dark trong khi light xanh sạch.
6. **Login hỏng = gate CHẾT:** login fail ⇒ mọi route redirect `/auth` ⇒ gate audit 8 bản sao trang
   sign-in rồi hô "design-ok" = **xanh GIẢ**, tệ hơn đỏ.

## Token đã CHỐT (kèm số ĐO — đừng đổi mù)

| token | giá trị | đo được |
|---|---|---|
| `--neu-bg` (= card, = sidebar) | `#e0e5ec` | mặt đơn sắc; luminance 0.778 |
| `--neu-ink` (body text) | `#14171c` | gần đen |
| `--muted-foreground` | `#3a4049` | `#454b56` chỉ **6.93:1** → trượt AAA, phải đậm hơn |
| **`--neu-accent`** (CTA) | **`#1c1f26`** | near-black, cool-tinted → AAA rất thoải mái cả 2 chiều |
| `--neu-dark` / `--neu-light` | `#bec3c9` / `#ffffff` | cặp bóng 9px/18px (card) · 3px/6px (nút) |

**LUẬT MÀU ACCENT (đã sửa — lần đầu tôi suy luận SAI):**

Đối nghịch ở đây là đối nghịch **ĐỘ SÁNG**, **KHÔNG PHẢI** đối nghịch **HUE**.

- ❌ **Sai lần 1:** accent xanh (`#4d6bfe`) — **cùng họ với nền xanh-xám ⇒ hoà vào nền ⇒ "chìm"**, dù pass AA.
- ❌ **Sai lần 2:** tôi hiểu "đối nghịch" = complementary hue → chọn **nâu-rust ấm** (`#7c2d12`).
  Đạt AAA nhưng **lạc quẻ**: nó *cãi nhau* với bảng màu trung tính của neumorphism.
- ✅ **Đúng:** dùng **HỌ TRUNG TÍNH QUANH ĐEN** (`#1c1f26` / `#14171c` / xám đậm). Tương phản
  tối đa bằng **độ sáng**, **không thêm hue mới** ⇒ vừa AAA, vừa cohesive, vừa premium.

**Quy tắc chung:** trên mặt neumorphic đơn sắc, accent = **near-black**, không phải màu-rực.
Muốn thêm màu thì chỉ dùng cho **semantic** (đỏ = destructive), không dùng làm accent chính.

**ACCENT PHẢI LẬT THEO THEME** (bài học 13/07/26 — bản dark bị BỎ QUÊN suốt vì gate không chụp dark):

| | mặt (bg) | accent | chữ trên accent | đo được |
|---|---|---|---|---|
| light | `#e0e5ec` | `#1c1f26` (near-black) | `#ffffff` | accent vs nền 5.49:1 · chữ trên accent 6.96:1 |
| **dark** | `#2d3239` | **`#eef1f5`** (near-white) | **`#14171c`** | accent vs nền **11.39:1** · chữ trên accent **15.86:1** |

- ❌ dark cũ giữ nguyên accent xanh `#6d86ff` + chữ trắng ⇒ **3.23:1** (nút `Save`/`Create` mờ tịt).
- ❌ `--muted-foreground: #98a1ad` ở dark chỉ **4.94:1** → trượt AAA trên 7 route → đổi `#c3cad3` (7.81:1).
- ❌ **Cấm hardcode `color:#fff` cho `.bg-primary`**: accent lật theo theme thì chữ phải lật ngược lại;
  hardcode ⇒ ở dark là **trắng-trên-trắng 1.13:1** (chữ tàng hình). Dùng `var(--primary-foreground)`.

Luật gốc không đổi: accent = đối nghịch **ĐỘ SÁNG** với MẶT ĐANG DÙNG. Mặt sáng → accent tối;
mặt tối → accent sáng. Một hằng số accent cho cả 2 theme là **sai từ định nghĩa**.

## Ngoài phạm vi

Không sửa logic component; chỉ override token + rebrand + layer bóng. Không đụng API/store/backend.

## UI hoạt động ra sao

- Áp mọi màn. Card/dialog **raised** (bóng lớn) · input + nút-nhấn **inset** · CTA **phẳng accent** (không neumorph).
- **Trong container `overflow:hidden`** (rail sidebar hẹp, tab bar): **CẤM bóng outset** — sẽ bị cắt.
  Đo được: logo rộng 58px trong rail clip 55px → **tràn trước cả khi tính aura**. Dùng **inset** (không thể tràn).
  `overflow-x:visible` KHÔNG khả thi khi trục kia là `auto` (CSS ép về `auto`).
- **Hàng chip sát nhau** (gap ~6px): cấm outset — bóng tối rơi vào khe → **vệt cứng**.
- **Đè specificity:** rule cũ `[data-slot=button]:not(.bg-primary):not(.bg-destructive)` = **(0,3,0)**;
  rule mới phải ≥ specificity đó, nếu không `!important` cũng **vô hiệu** (đã mất 3 lần sửa vì lỗi này).
