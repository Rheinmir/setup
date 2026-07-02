---
type: concept
title: "Ví dụ concept (demo template)"
id: example-concept
---

# Ví dụ concept

Đây là một trang concept **demo** trong khuôn `llmwiki/wiki/` — minh hoạ cấu trúc tối thiểu
hợp lệ cho một project dùng llmwiki: có YAML frontmatter (`type`), một tiêu đề `#`, và mục
`## Origin` để nguồn luôn truy được.

Một project thật sẽ thay file này bằng concept/entity/source của chính nó. Wiki riêng của
**framework** (ADR, rule-registry, fdk…) không nằm ở đây mà ở `fdk/wiki/`.

## Origin
- **Source:** tạo làm demo khi tách wiki framework sang `fdk/wiki/` (ADR-008) — giữ 1 file
  để CI dogfood luật wiki trên cả root `llmwiki/wiki`. Không phải nội dung framework.
