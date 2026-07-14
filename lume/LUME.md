# Lume

Ứng dụng ghi chú — **dự án độc lập**, sản phẩm của dây chuyền `/br`.

## Nguồn gốc (provenance — nói thẳng, không giấu)

Lume **fork từ** `usememos/memos` @ `4bc3928` (kéo về 12/07/2026) rồi rebrand + build lại giao diện
qua dây chuyền. Code Go/React kế thừa từ đó; phần **của Lume** là:

| phần | file |
|---|---|
| Design-system neumorphism (3 theme) | `web/src/themes/neumorphism.css` · `default-dark.css` · `paper.css` |
| Brand Lume (logo/avatar/empty-state/sign-in/title) | `web/src/components/MemosLogo.tsx` · `UserAvatar.tsx` · `Placeholder/index.tsx` · `pages/SignIn.tsx` · `web/index.html` |

> Tên `memos` còn sót trong đường dẫn nội bộ (`cmd/memos`, tên package Go, API path) — đổi hết là
> một frame riêng, chưa làm. Thấy `memos` trong code = **nợ rebrand**, không phải Lume là con của memos.

## Chạy

```bash
cd web && pnpm install && pnpm release   # build SPA → nhúng vào server/router/frontend/dist
cd .. && go run ./cmd/memos --port 5230 --data ./data
```
→ http://localhost:5230 · tài khoản dev: `demo` / `demo`

`data/` (SQLite + file upload) **không commit** — dữ liệu, không phải nguồn.

## Kiến trúc hiện tại

- **Backend Go** — 1 binary serve cả API + SPA nhúng (`pnpm release` nhồi dist vào binary).
- **Frontend** React + Vite + Tailwind/shadcn; theme nạp **runtime** (inject `<style>` theo setting
  tài khoản), KHÔNG phải class `.dark` → sửa theme phải sửa đúng file app inject.
- **Store: SQL (SQLite mặc định)** — `store/db/{sqlite,mysql,postgres}`.
  **CHƯA file-first.** Frame `frame-n04-storage-file-first` mới ở giai đoạn PoC, chưa có gate thật.

## Sửa Lume thế nào

**Cấm sửa tay.** Mọi thay đổi đi qua dây chuyền:
`br/lume/br/BR.md` (clause) → `/br slice` → frame trong `br/lume/br/frames/` → `/design-twice`
(nếu có UI) → `/br run <frame>` → gate `/visual-qa` (chụp 7 route × 3 theme, chấm AAA + đơn sắc).
