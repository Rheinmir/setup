# Tự-kiểm auto-draw vector (wiki-graph.html) cho dự án downstream

Prompt + cấu trúc chẩn đoán để verify: cài harness xuống một dự án thì **vector có tự vẽ không**,
nếu **không** thì kẹt ở mắt xích nào. Đã kiểm chứng ở repo framework (reachability test 17/17 pass).

---

## Cách dùng

**Nhanh nhất** — có sẵn script tự-verdict, copy 1 file `wiki-graph-selfcheck.sh` vào dự án rồi:

```bash
bash wiki-graph-selfcheck.sh
```

Script tự dò 5 mắt xích, ép chạy generator, và in verdict (mắt xích ✗ đầu tiên + cách sửa).

**Hoặc** — paste nguyên khối prompt dưới đây vào session phụ trách dự án đó.

---

## Prompt paste cho session phụ

```
Kiểm tra hệ auto-draw wiki-graph (vector) trong dự án này. Chạy các lệnh sau, đọc kết
quả theo cây quyết định bên dưới, rồi kết luận: vector CÓ tự vẽ không, nếu KHÔNG thì
kẹt ở mắt xích nào.

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"; cd "$ROOT"; echo "ROOT=$ROOT"

echo "── [A] engine reachable? (repo-local → global ~/.claude/harness) ──"
ls -la fdk/tools/build-wiki-graph.py 2>/dev/null \
  || ls -la ~/.claude/harness/fdk/tools/build-wiki-graph.py 2>/dev/null \
  || echo "✗ KHÔNG thấy engine ở cả repo-local lẫn global"

echo "── [B] cờ opt-in OVERSTACK_WIKIGRAPH=1 trong settings.json? ──"
grep -rn "OVERSTACK_WIKIGRAPH" .claude/settings.json ~/.claude/settings.json 2>/dev/null \
  || echo "✗ chưa set ở đâu → downstream sẽ return sớm, không vẽ"

echo "── [C] Stop hook có wired? ──"
grep -n "stop.py" .claude/settings.json 2>/dev/null || echo "✗ Stop hook chưa wire"

echo "── [D] .harness-stamp có? (guard cho hook global fire) ──"
ls -la llmwiki/.harness-stamp 2>/dev/null || echo "✗ thiếu stamp → hook global không fire"

echo "── [E] file kết quả + tuổi ──"
ls -la llmwiki/html/wiki-graph.html 2>/dev/null || echo "✗ chưa có file graph"

echo "── [F] ÉP chạy generator (tách lỗi engine vs lỗi trigger) ──"
WG="$(ls fdk/tools/build-wiki-graph.py 2>/dev/null || echo ~/.claude/harness/fdk/tools/build-wiki-graph.py)"
python3 "$WG" llmwiki/wiki --code-root . 2>&1 | tail -3
grep -c "nodes" llmwiki/html/wiki-graph.html 2>/dev/null && echo "→ file có data blob (vẽ được)"

Cây quyết định:
- [F] in "✓ … N node, M cạnh" và [E] file tươi + có data blob → ENGINE OK, vector vẽ được.
    Nếu vậy mà "tự động" không chạy → nguyên nhân là 1 trong:
      · [B] thiếu cờ → thêm  "env": { "OVERSTACK_WIKIGRAPH": "1" }  vào .claude/settings.json
      · git-status không có diff ở  wiki/  hay file code → hook (B) không có gì để regen
        (KHÔNG phải bug — auto-draw chỉ fire khi nguồn đổi; đổi 1 file wiki/code rồi Stop lại).
- [A] "✗ không thấy engine" → chưa cài harness global:
      bash <repo-framework>/harness/scripts/install-harness.sh --global
- [C] "✗ Stop hook chưa wire" hoặc [D] "✗ thiếu stamp"
      → chưa cài harness vào repo. Chạy install-harness.sh (bản mới ghi luôn cờ [B]).
- [F] in lỗi argparse / traceback → lỗi engine THẬT (không phải trigger). Dán nguyên
      output [F] + `cat .overstack.yaml 2>/dev/null` (scope wiki_dir/code_root) để soi.

Báo lại: mắt xích nào ✗ đầu tiên, và [F] ra bao nhiêu node.
```

---

## Cấu trúc đường auto-draw (để dự đoán vấn đề nếu không chạy được)

```
Stop hook → stop.regen_docs(root)
  ├─ [A] wg = resolve_tool(root, "fdk/tools/build-wiki-graph.py")   repo-local → global
  ├─ [B] wikigraph_on = wg AND (is_framework OR env OVERSTACK_WIKIGRAPH==1)
  │        └─ downstream: is_framework=False → BẮT BUỘC có cờ [B], không thì return sớm
  ├─      git-status khớp (wiki/ | build-wiki-graph.py | file code đổi)?   ← trigger
  └─ [F]  chạy generator → llmwiki/html/wiki-graph.html
           (đọc .overstack.yaml: wiki_dir + code_root để định scope)
```

## 4 điểm gãy thường gặp (xếp theo tần suất)

| # | Điểm gãy | Dấu hiệu | Cách sửa |
|---|----------|----------|----------|
| 1 | **[B] thiếu cờ opt-in** | grep OVERSTACK_WIKIGRAPH trống | Thêm `"env": {"OVERSTACK_WIKIGRAPH": "1"}` vào `.claude/settings.json` — hoặc chạy lại `install-harness.sh` (bản đã push tự ghi cờ) |
| 2 | **git-status không có diff** | engine chạy tay OK, nhưng Stop không tự vẽ | KHÔNG phải bug — đổi 1 file `wiki/` hoặc code rồi Stop lại; hoặc chạy tay lệnh [F] |
| 3 | **[A] engine chưa cài global** | [A] báo ✗ | `bash <repo-framework>/harness/scripts/install-harness.sh --global` |
| 4 | **[D] thiếu `.harness-stamp`** | [D] báo ✗ | Chạy `install-harness.sh` vào repo (ghi stamp) |

## Ghi chú

- Bản `install-harness.sh` đã push (commit `549a891`) **tự ghi `OVERSTACK_WIKIGRAPH=1`** vào
  `.claude/settings.json` ROOT khi cài. Dự án nào cài **trước** commit đó thì settings cũ chưa có cờ
  → chạy lại installer, hoặc thêm cờ tay.
- Auto-draw chạy **im lặng, fail-open** — không spam nhắc nhở. Đầu phiên downstream, hook
  `SessionStart` mới in orientation (code-index / wiki / CAPABILITIES) + wiki-sync nếu code lệch.
