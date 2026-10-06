"""ax-scan (qc-uiux mục 5 AX) — site fixture thật qua http.server ở 127.0.0.1, đọc HTML thô như crawler."""
import functools
import http.server
import importlib.util
import struct
import threading
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
s = importlib.util.spec_from_file_location("ax_scan", ROOT / "skills/qc-uiux/scripts/ax-scan.py")
ax = importlib.util.module_from_spec(s); s.loader.exec_module(ax)

BODY = "<main><h1>Bán phần mềm kế toán cho tiệm nhỏ</h1>" + "<p>Ghi thu chi, in hoá đơn, xem lãi lỗ theo ngày. " * 12 + "</p></main>"


def png(w, h):
    ch = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d))
    return b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) + ch(b"IEND", b"")


def serve(tmp, files):
    for rel, data in files.items():
        f = tmp / rel; f.parent.mkdir(parents=True, exist_ok=True)
        f.write_bytes(data if isinstance(data, bytes) else data.encode())
    h = functools.partial(type("Q", (http.server.SimpleHTTPRequestHandler,), {"log_message": lambda *a: None}), directory=str(tmp))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}"


def good_head(base, extra=""):
    return (f'<!doctype html><html lang="vi"><head><title>Kế toán tiệm</title><meta name="description" content="Phần mềm kế toán cho tiệm nhỏ">'
            f'<link rel="canonical" href="{base}/"><meta property="og:title" content="Kế toán tiệm"><meta property="og:description" content="x">'
            f'<meta property="og:image" content="/og.png"><meta name="twitter:card" content="summary_large_image">'
            f'<script type="application/ld+json">{{"@context":"https://schema.org","@type":"SoftwareApplication","name":"Kế toán tiệm"}}</script>{extra}</head>')


def test_good_site_is_clean(tmp_path):
    srv, base = serve(tmp_path, {})
    try:
        serve_files = {"index.html": good_head(base) + f"<body>{BODY}</body></html>", "og.png": png(1200, 630),
                       "robots.txt": f"User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n",
                       "sitemap.xml": f"<urlset><url><loc>{base}/</loc></url></urlset>", "llms.txt": "# Kế toán tiệm\n"}
        for k, v in serve_files.items():
            (tmp_path / k).write_bytes(v if isinstance(v, bytes) else v.encode())
        r = ax.scan(base)
        assert not r["fail"] and not r["warn"], r
        assert not any(p["fail"] or p["warn"] for p in r["pages"]), r["pages"]
        assert ax.main([base]) == 0
    finally:
        srv.shutdown()


def test_boring_fundamentals_fail_llms_txt_only_notes(tmp_path):
    """SPA rỗng + chặn bot AI + thiếu canonical = FAIL; thiếu llms.txt chỉ là NOTE (không trừ điểm)."""
    srv, base = serve(tmp_path, {
        "index.html": '<!doctype html><html><head><title>App</title><script type="application/ld+json">{bad json</script></head>'
                      '<body><div id="root"></div><script>render()</script></body></html>',
        "robots.txt": "User-agent: GPTBot\nDisallow: /\n\nUser-agent: ClaudeBot\nDisallow: /\n"})
    try:
        r = ax.scan(base)
        page = r["pages"][0]
        assert any("chặn bot AI" in m and "GPTBot" in m and "ClaudeBot" in m for m in r["fail"])
        assert any("server-render rỗng" in m for m in page["fail"])
        assert any("canonical" in m for m in page["fail"])
        assert any("JSON-LD hỏng" in m for m in page["fail"])
        assert any("llms.txt" in m for m in r["note"]) and not any("llms.txt" in m for m in r["fail"] + r["warn"])
        assert ax.main([base]) == 1
        r2 = ax.scan(base, allow_ai_block=True)                      # cố ý chặn → hạ xuống NOTE
        assert not any("chặn bot AI" in m for m in r2["fail"]) and any("chặn bot AI" in m for m in r2["note"])
    finally:
        srv.shutdown()


def test_og_image_wrong_size_warns_and_site_origin_maps(tmp_path):
    srv, base = serve(tmp_path, {})
    try:
        prod = "https://prod.example"
        (tmp_path / "index.html").write_text(good_head(prod).replace(f'href="{prod}/"', f'href="{prod}/"') + f"<body>{BODY}</body></html>")
        (tmp_path / "og.png").write_bytes(png(400, 400))
        (tmp_path / "robots.txt").write_text(f"User-agent: *\nSitemap: {prod}/sitemap.xml\n")
        (tmp_path / "sitemap.xml").write_text(f"<urlset><url><loc>{prod}/</loc></url><url><loc>{prod}/gone</loc></url></urlset>")
        r = ax.scan(base, site_origin=prod)
        urls = [p["url"] for p in r["pages"]]
        assert f"{base}/gone" in urls, urls                             # URL production map về base đang quét
        assert any("400×400" in m for m in r["pages"][0]["warn"])
        assert any("trả 404" in m for p in r["pages"] if p["url"].endswith("/gone") for m in p["fail"])
    finally:
        srv.shutdown()


def test_unreachable_is_not_a_pass():
    assert ax.main(["http://127.0.0.1:9"]) == 3


def test_image_size_parsers():
    assert ax.image_size(png(1200, 630)) == (1200, 630)
    jpg = b"\xff\xd8" + b"\xff\xe0\x00\x04ab" + b"\xff\xc0\x00\x11\x08" + struct.pack(">HH", 630, 1200) + b"\x00" * 10
    assert ax.image_size(jpg) == (1200, 630)
    assert ax.image_size(b"GIF89a" + struct.pack("<HH", 10, 20)) == (10, 20)
