#!/usr/bin/env python3
"""ui-snapshot build: app.js + template.html → ONE self-contained HTML (Tailwind + fonts + images inlined).

python3 build.py --fe <frontend dir> --src <dir with app.js + template.html> --out snapshot.html \
    [--font "Lexend Deca"] [--asset LOGO=public/logo.png] [--asset BANNER=public/banner.svg] [--max-mb 5]

- Tailwind is compiled with the project's OWN tailwind.config + globals.css, content = only app.js/template,
  so the snapshot's classes resolve exactly like the real app.
- Material Symbols: only the icon names that literally appear in app.js (quoted) are subset from Google Fonts.
- --asset NAME=path replaces __NAME__ in app.js/template with a data URI (png/jpg are downscaled to 128px).
Exit 1 if the output exceeds --max-mb.
"""
import argparse, base64, os, re, subprocess, sys, tempfile, urllib.request, urllib.parse

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36"}
MS_CODEPOINTS = "https://raw.githubusercontent.com/google/material-design-icons/master/variablefont/MaterialSymbolsOutlined%5BFILL%2CGRAD%2Copsz%2Cwght%5D.codepoints"
get = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read()
b64 = lambda b: base64.b64encode(b).decode()
MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml", ".webp": "image/webp", ".gif": "image/gif"}


def first(fe, names):
    return next((os.path.join(fe, n) for n in names if os.path.exists(os.path.join(fe, n))), None)


def inline_fonts(css):  # keep only vietnamese/latin blocks, inline woff2 as data URIs
    blocks = ["/*" + b for b in css.split("/*")[1:]] or [css]
    css = "\n".join(b for b in blocks if not re.search(r"cyrillic|greek|arabic|hebrew", b.split("*/")[0]))
    return re.sub(r"url\((https://[^)]+)\)", lambda m: f"url(data:font/woff2;base64,{b64(get(m.group(1)))})", css)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fe", required=True); ap.add_argument("--src", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--font", default=""); ap.add_argument("--css", default=None); ap.add_argument("--asset", action="append", default=[])
    ap.add_argument("--max-mb", type=float, default=5.0)
    a = ap.parse_args()
    fe, src = os.path.abspath(a.fe), os.path.abspath(a.src)
    js, html = open(os.path.join(src, "app.js")).read(), open(os.path.join(src, "template.html")).read()

    # 1. Tailwind with the project's own config
    cfg = first(fe, ["tailwind.config.ts", "tailwind.config.js", "tailwind.config.mjs", "tailwind.config.cjs"])
    css_in = a.css or first(fe, ["styles/globals.css", "app/globals.css", "src/app/globals.css", "src/styles/globals.css", "src/index.css"])
    tw = first(fe, ["node_modules/.bin/tailwindcss"])
    css = ""
    if cfg and tw:
        tmp = tempfile.mkdtemp()
        wrap = os.path.join(tmp, "tw.config.ts")
        open(wrap, "w").write(f'import base from {os.path.splitext(cfg)[0]!r};\nexport default {{ ...(base as any), content: [{os.path.join(src, "template.html")!r}, {os.path.join(src, "app.js")!r}] }};\n')
        out = os.path.join(tmp, "out.css")
        cmd = [tw, "-c", wrap, "-o", out, "--minify"] + (["-i", css_in] if css_in else [])
        r = subprocess.run(cmd, cwd=fe, capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"tailwind failed:\n{r.stderr[-2000:]}")
        css = open(out).read()
    else:
        print("! no tailwind config/CLI found — CSS left empty (write plain CSS in template instead)", file=sys.stderr)

    # 2. Fonts
    fonts = ""
    if a.font:
        fonts += inline_fonts(get(f"https://fonts.googleapis.com/css2?family={urllib.parse.quote_plus(a.font)}:wght@300..900&display=swap").decode())
    if "material-symbols" in js + html:
        valid = {l.split()[0] for l in get(MS_CODEPOINTS).decode().splitlines() if l.strip()}
        icons = sorted(set(re.findall(r'"([a-z][a-z0-9_]+)"', js)) & valid)
        fonts += inline_fonts(get("https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0..1,0&display=block&icon_names=" + ",".join(icons)).decode())
        print(f"material symbols: {len(icons)} icons")

    # 3. Assets → data URIs
    for spec in a.asset:
        name, path = spec.split("=", 1)
        path = path if os.path.isabs(path) else os.path.join(fe, path)
        ext = os.path.splitext(path)[1].lower()
        data = open(path, "rb").read()
        if ext in (".png", ".jpg", ".jpeg") and sys.platform == "darwin":
            t = tempfile.mktemp(suffix=ext)
            subprocess.run(["sips", "-Z", "128", path, "--out", t], check=True, capture_output=True)
            data = open(t, "rb").read()
        uri = f"data:{MIME.get(ext, 'application/octet-stream')};base64,{b64(data)}"
        js, html = js.replace(f"__{name}__", uri), html.replace(f"__{name}__", uri)

    html = html.replace("/*__FONTS__*/", fonts).replace("/*__CSS__*/", css).replace("/*__JS__*/", js.replace("</script", "<\\/script"))
    open(a.out, "w").write(html)
    mb = os.path.getsize(a.out) / 1048576
    print(f"{a.out}: {mb*1024:.1f} KB")
    if mb > a.max_mb:
        sys.exit(f"FAIL: {mb:.2f} MB > {a.max_mb} MB")


if __name__ == "__main__":
    main()
