#!/usr/bin/env python3
"""
Build a dev.to cover image (1000x420) from real technology logos.

This exists because AI-generated covers are generic and garble lettering.
Composing the real marks over vector text gives a cover that is on-brand,
legible at thumbnail size, and reproducible.

Logo sources (--left/--right/--logo accept any of these):
    si:tauri            Simple Icons, official mark in its brand colour
    si:electron:FFFFFF  Simple Icons, forced to a hex colour
    gh:tauri-apps       GitHub org/user avatar
    https://…           any direct URL to an .svg or raster image
    ./path/to/logo.svg  a local file

Examples
--------
Two technologies, before/after:

    make-cover.py compare \\
        --left si:electron  --left-label ELECTRON --left-value "289 MB" \\
        --right si:tauri    --right-label TAURI   --right-value "15 MB" \\
        --middle "18.9x SMALLER" \\
        --subtitle "Migrating a macOS menu-bar app from Electron to Tauri 2" \\
        --out cover.png

No logo at all (career or opinion pieces) — still composed, never AI-generated:

    make-cover.py text \\
        --kicker "Field notes" \\
        --headline "What two years of | shipping a side project taught me" \\
        --subtitle "..." --out cover.png

One technology, headline:

    make-cover.py single \\
        --logo si:nodedotjs \\
        --headline "NODE.JS SEA" --kicker "--build-sea" \\
        --subtitle "One flag instead of five manual steps" \\
        --out cover.png

Requires `rsvg-convert` (macOS: brew install librsvg · Debian/Ubuntu: sudo apt install
librsvg2-bin).
"""

import argparse
import base64
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request

W, H = 1000, 420
FONT = "Helvetica Neue, Helvetica, Arial, sans-serif"
UA = {"User-Agent": "Mozilla/5.0 (cover-builder)"}


def die(msg):
    sys.exit(f"make-cover: {msg}")


def resolve(spec: str) -> str:
    """Turn a logo spec into a fetchable URL or a local path."""
    if spec.startswith("si:"):
        parts = spec.split(":")
        slug = parts[1]
        colour = parts[2] if len(parts) > 2 else None
        return f"https://cdn.simpleicons.org/{slug}" + (f"/{colour}" if colour else "")
    if spec.startswith("gh:"):
        return f"https://github.com/{spec[3:]}.png"
    return spec


def fetch(spec: str, tmp: pathlib.Path, name: str) -> pathlib.Path:
    src = resolve(spec)
    if src.startswith(("http://", "https://")):
        req = urllib.request.Request(src, headers=UA)
        with urllib.request.urlopen(req, timeout=30) as r:
            blob = r.read()
        if not blob:
            die(f"empty response for {src}")
    else:
        p = pathlib.Path(src).expanduser()
        if not p.is_file():
            die(f"no such file: {p}")
        blob = p.read_bytes()

    is_svg = blob.lstrip()[:200].lower().startswith((b"<svg", b"<?xml"))
    out = tmp / (name + (".svg" if is_svg else ".png"))
    out.write_bytes(blob)

    if is_svg:
        png = tmp / (name + ".png")
        subprocess.run(
            ["rsvg-convert", "-w", "400", "-h", "400", "-a", str(out), "-o", str(png)],
            check=True,
        )
        return png
    return out


def b64(p: pathlib.Path) -> str:
    return base64.b64encode(p.read_bytes()).decode()


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def render(svg: str, out: pathlib.Path):
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as f:
        f.write(svg)
        tmp_svg = f.name
    subprocess.run(
        ["rsvg-convert", "-w", str(W), "-h", str(H), tmp_svg, "-o", str(out)], check=True
    )
    pathlib.Path(tmp_svg).unlink(missing_ok=True)


def chrome(accent: str) -> str:
    return f'''<defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#1b1e25"/>
      <stop offset="100%" stop-color="#101216"/>
    </linearGradient>
    <clipPath id="discL"><circle cx="195" cy="147" r="75"/></clipPath>
    <clipPath id="discR"><circle cx="805" cy="147" r="75"/></clipPath>
  </defs>
  <rect width="{W}" height="{H}" fill="url(#bg)"/>
  <rect x="0" y="0" width="{W}" height="5" fill="{accent}"/>'''


def footer(subtitle: str) -> str:
    if not subtitle:
        return ""
    return f'''
  <rect x="120" y="366" width="760" height="1" fill="#2c313a"/>
  <text x="500" y="399" font-family="{FONT}" font-size="23" font-weight="400"
        fill="#7d8593" text-anchor="middle">{esc(subtitle)}</text>'''


def build_compare(a, tmp) -> str:
    left = b64(fetch(a.left, tmp, "left"))
    right = b64(fetch(a.right, tmp, "right"))
    clipL = ' clip-path="url(#discL)"' if a.disc else ""
    clipR = ' clip-path="url(#discR)"' if a.disc else ""

    middle = ""
    if a.middle:
        middle = f'''
  <text x="500" y="262" font-family="{FONT}" font-size="26" font-weight="600"
        fill="{a.accent}" text-anchor="middle" letter-spacing="1">{esc(a.middle)}</text>'''

    def column(x, img, clip, label, value, colour):
        out = f'  <image xlink:href="data:image/png;base64,{img}" x="{x - 75}" y="72" width="150" height="150"{clip}/>'
        if label:
            out += f'''
  <text x="{x}" y="272" font-family="{FONT}" font-size="30" font-weight="500"
        fill="#9aa0ab" text-anchor="middle" letter-spacing="2">{esc(label)}</text>'''
        if value:
            out += f'''
  <text x="{x}" y="332" font-family="{FONT}" font-size="58" font-weight="700"
        fill="{colour}" text-anchor="middle">{esc(value)}</text>'''
        return out

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  {chrome(a.accent)}
{column(195, left, clipL, a.left_label, a.left_value, "#ffffff")}
  <g fill="{a.accent}">
    <rect x="425" y="138" width="110" height="18" rx="9"/>
    <path d="M527 108 L585 147 L527 186 Z"/>
  </g>{middle}
{column(805, right, clipR, a.right_label, a.right_value, a.accent)}{footer(a.subtitle)}
</svg>'''


def build_single(a, tmp) -> str:
    logo = b64(fetch(a.logo, tmp, "logo"))
    clip = ' clip-path="url(#discL)"' if a.disc else ""
    kicker = ""
    if a.kicker:
        kicker = f'''
  <text x="330" y="250" font-family="{FONT}" font-size="34" font-weight="600"
        fill="{a.accent}" text-anchor="start">{esc(a.kicker)}</text>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  {chrome(a.accent)}
  <image xlink:href="data:image/png;base64,{logo}" x="120" y="72" width="150" height="150"{clip}/>
  <text x="330" y="175" font-family="{FONT}" font-size="64" font-weight="700"
        fill="#ffffff" text-anchor="start">{esc(a.headline)}</text>{kicker}{footer(a.subtitle)}
</svg>'''


def build_text(a, tmp) -> str:
    """No-logo layout: for posts with no technology to show (career, opinion).

    Still composed rather than AI-generated — vector text is exact, and the
    result looks like it belongs beside the other covers.
    """
    kicker = ""
    if a.kicker:
        kicker = f'''
  <text x="500" y="108" font-family="{FONT}" font-size="26" font-weight="600"
        fill="{a.accent}" text-anchor="middle" letter-spacing="3">{esc(a.kicker.upper())}</text>'''
    lines = a.headline.split("|")
    if len(lines) > 2:
        die("--headline takes at most two lines (split with |)")
    size = 76 if len(lines) == 1 else 64
    y0 = 210 if len(lines) == 1 else 178
    body = "".join(
        f'''
  <text x="500" y="{y0 + i * (size + 10)}" font-family="{FONT}" font-size="{size}"
        font-weight="700" fill="#ffffff" text-anchor="middle">{esc(line.strip())}</text>'''
        for i, line in enumerate(lines)
    )
    rule = f'''
  <rect x="440" y="{y0 + len(lines) * (size + 10) - 30}" width="120" height="5" rx="2" fill="{a.accent}"/>'''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"
     width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  {chrome(a.accent)}{kicker}{body}{rule}{footer(a.subtitle)}
</svg>'''


def main():
    if not shutil.which("rsvg-convert"):
        die("rsvg-convert not found — install it with: macOS: brew install librsvg · "
            "Debian/Ubuntu: sudo apt install librsvg2-bin")

    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="layout", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--subtitle", default="")
    common.add_argument("--accent", default="#FFC131")
    common.add_argument("--out", default="cover.png")
    common.add_argument("--disc", action="store_true", default=True,
                        help="clip logos to circles (default: on, keeps mismatched "
                             "square and circular marks visually consistent)")
    common.add_argument("--no-disc", dest="disc", action="store_false")

    c = sub.add_parser("compare", parents=[common])
    c.add_argument("--left", required=True)
    c.add_argument("--left-label", default="")
    c.add_argument("--left-value", default="")
    c.add_argument("--right", required=True)
    c.add_argument("--right-label", default="")
    c.add_argument("--right-value", default="")
    c.add_argument("--middle", default="")

    s = sub.add_parser("single", parents=[common])
    s.add_argument("--logo", required=True)
    s.add_argument("--headline", required=True)
    s.add_argument("--kicker", default="")

    t = sub.add_parser("text", parents=[common])
    t.add_argument("--headline", required=True,
                   help="split into two lines with a | separator")
    t.add_argument("--kicker", default="")

    a = ap.parse_args()
    out = pathlib.Path(a.out).expanduser()

    with tempfile.TemporaryDirectory() as td:
        tmp = pathlib.Path(td)
        svg = {"compare": build_compare, "single": build_single,
               "text": build_text}[a.layout](a, tmp)
        render(svg, out)

    print(f"{out}  ({out.stat().st_size // 1024} KB, {W}x{H})")
    print("Check it before uploading — read the PNG and confirm every logo resolved.")


if __name__ == "__main__":
    main()
