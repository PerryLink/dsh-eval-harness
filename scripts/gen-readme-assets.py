#!/usr/bin/env python3
"""README visuals for dsh-eval-pack — v5.

Both figures are derived from the real surface in this repo:

* ``src/core/harness.ts`` — ``lintPack`` (name / version / non-empty tasks /
  unique ids), ``canonical`` (recursive key sort, arrays kept in order) and
  ``grade`` (one string equality), ``summarize`` (total / passed / failed /
  pass_rate / failures) and ``passAtK`` (1 - C(n-c,k)/C(n,k), BigInt).
* ``samples/quickstart`` — the shipped synthetic run: 3 tasks, grade case-01
  pass, case-02 fail, case-03 pass, ``pass_rate 0.666667``, failure
  ``case-02``, pass@1 mean 0.633333, pass@3 mean 0.9. case-03 only differs in
  key order (net/tax/gross vs gross/tax/net) yet passes; case-02 differs by one
  character (``"12.35"`` vs ``"12.34"``) and fails.
* ``src/plugin/tools.ts`` — the four tool names and their R0 read-only nature.
* ``cordis.patch.yml`` — a single insert, no plugin config keys.

Outputs
-------
``dsh-eval-pack-hero-{zh,en}-{light,dark}.webp`` (1440x576) — left column is
kicker / title / two value lines / sub / meta / footer; the right side is the
grade receipt: the two JSON documents with different key order, the ``=`` seam,
the canonical string, the three verdicts and the run numbers.

``dsh-eval-pack-flow-v5-{light,dark}.svg`` (1100x660) — grammar: **clause
comparison / dual-column adjudication** (not a five-node chain). Three stacked
tiers: 01 pack gate -> 02 pairwise bench (both documents sit on opposite sides
of one comparison gutter) -> 03 readouts (tally + pass@k estimator).

Run:  python scripts/gen-readme-assets.py
"""
from __future__ import annotations

import os

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")

FONT_CJK = r"C:\Windows\Fonts\msyh.ttc"
FONT_CJK_BOLD = r"C:\Windows\Fonts\msyhbd.ttc"
FONT_MONO = r"C:\Windows\Fonts\consola.ttf"
FONT_MONO_BOLD = r"C:\Windows\Fonts\consolab.ttf"
for _p in (FONT_CJK, FONT_CJK_BOLD, FONT_MONO, FONT_MONO_BOLD):
    if not os.path.exists(_p):
        raise SystemExit(f"FATAL: font missing: {_p}")

# Shapes are composited at 2x and downsampled: crisp card edges.
S = 2

SKIN = {
    "light": dict(bg_from="#f9f6fd", bg_to="#e4eaf8", card="#ffffff",
                  edge="#e2dff0", text="#141419", sub="#4d5261",
                  faint="#8f94a4", accent="#4B67B4", green="#15803d",
                  danger="#b3261e", pill="#ece7f9", track="#f3f0fb",
                  shadow=(38, 30, 72), shadow_a=26),
    "dark": dict(bg_from="#131a2a", bg_to="#0c1016", card="#1b2231",
                 edge="#2e374b", text="#f0f3f9", sub="#a8b1c4",
                 faint="#737b8d", accent="#8496f5", green="#3fb950",
                 danger="#f87171", pill="#242d42", track="#222b3d",
                 shadow=(0, 0, 0), shadow_a=110),
}


def font(size: int, kind: str = "cjk_bold") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(
        {"cjk": FONT_CJK, "cjk_bold": FONT_CJK_BOLD,
         "mono": FONT_MONO, "mono_bold": FONT_MONO_BOLD}[kind], size)


def hx(s: str):
    s = s.lstrip("#")
    return tuple(int(s[i:i + 2], 16) for i in (0, 2, 4))


def mix(a: str, b: str, t: float):
    return tuple(int(x + (y - x) * t) for x, y in zip(hx(a), hx(b)))


def gradient(w: int, h: int, c1: str, c2: str) -> Image.Image:
    base = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(base)
    for y in range(h):
        t = 0.18 * (y / h) + 0.82 * (y / h) ** 1.6
        d.line([(0, y), (w, y)], fill=mix(c1, c2, t))
    return base


def glow(img: Image.Image, cx: int, cy: int, r: int, color, alpha=40):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(12, 0, -1):
        rr = r * i / 12
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=color + (int(alpha * (1 - i / 13)),))
    layer = layer.filter(ImageFilter.GaussianBlur(28))
    return Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")


MEASURE = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def tw(text: str, size: int, kind: str = "cjk") -> float:
    return MEASURE.textlength(text, font=font(size, kind))


def is_cjk(ch: str) -> bool:
    return ord(ch) > 0x2E7F


def runs_of(s: str):
    """Split a label into CJK / non-CJK runs so no glyph ever falls back to a
    mono face that has no CJK coverage (that renders as tofu boxes)."""
    out, cur, cur_cjk = [], "", None
    for ch in s:
        flag = is_cjk(ch)
        if cur and flag != cur_cjk:
            out.append((cur, cur_cjk))
            cur = ""
        cur += ch
        cur_cjk = flag
    if cur:
        out.append((cur, cur_cjk))
    return out


def mixed_width(s: str, size: float, mono_kind: str = "mono") -> float:
    return sum(tw(run, size, "cjk" if cjk else mono_kind)
               for run, cjk in runs_of(s))


def draw_mixed(d, x, y, s, size, fill, mono_kind="mono", anchor="ls"):
    """Draw a mixed CJK/Latin label; returns the advance width."""
    total = mixed_width(s, size, mono_kind)
    start = x
    if anchor[0] == "r":
        start = x - total
    elif anchor[0] == "m":
        start = x - total / 2
    cursor = 0.0
    for run, cjk in runs_of(s):
        f = font(size, "cjk" if cjk else mono_kind)
        d.text((start + cursor, y), run, font=f, fill=hx(fill), anchor="ls")
        cursor += d.textlength(run, font=f)
    return total


def fit_mixed(s, size, maxw, mono_kind="mono", floor=11):
    while size > floor and mixed_width(s, size, mono_kind) > maxw:
        size -= 0.5
    return size


class Layer:
    """Vector layer in design coordinates (1440x576), rasterised at 2x."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        self.img = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
        self.d = ImageDraw.Draw(self.img)

    def refresh(self):
        self.d = ImageDraw.Draw(self.img)

    def rect(self, box, radius=0, fill=None, outline=None, width=1.0):
        self.d.rounded_rectangle([v * S for v in box], radius=radius * S,
                                 fill=fill, outline=outline,
                                 width=max(1, round(width * S)))

    def line(self, p1, p2, fill, width=1.0):
        self.d.line([p1[0] * S, p1[1] * S, p2[0] * S, p2[1] * S],
                    fill=fill, width=max(1, round(width * S)))

    def circle(self, cx, cy, r, fill=None, outline=None, width=1.0):
        self.d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S,
                        (cy + r) * S], fill=fill, outline=outline,
                       width=max(1, round(width * S)))

    def poly(self, points, fill):
        self.d.polygon([(x * S, y * S) for x, y in points], fill=fill)

    def shadow(self, box, radius=20, blur=14, color=(0, 0, 0), alpha=30, dy=10):
        sh = Image.new("RGBA", self.img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(sh)
        d.rounded_rectangle([box[0] * S, (box[1] + dy) * S, box[2] * S,
                             (box[3] + dy) * S], radius=radius * S,
                            fill=color + (alpha,))
        sh = sh.filter(ImageFilter.GaussianBlur(blur * S))
        self.img = Image.alpha_composite(self.img, sh)
        self.refresh()

    def flatten(self):
        return self.img.resize((self.w, self.h), Image.LANCZOS)


def text(d, xy, s, f, fill, anchor="ls"):
    d.text(xy, s, font=f, fill=hx(fill), anchor=anchor)


def arrow(L, x1, y1, x2, y2, color, width=2.0, head=9):
    """Horizontal/vertical arrow with a filled triangular head at (x2, y2)."""
    L.line((x1, y1), (x2 - head * 0.75, y2), color, width)
    if y1 == y2:
        sign = 1 if x2 > x1 else -1
        L.poly([(x2, y2), (x2 - head * sign, y2 - head * 0.52),
                (x2 - head * sign, y2 + head * 0.52)], hx(color))


HERO = {
    "zh": dict(
        kicker="DEEPSEEK HARNESS 插件 · 评测评分",
        title="dsh-eval-pack",
        value=["一小包样本，逐条精确比对", "通过率、失败项与 pass@k，当场出"],
        sub="四个 R0 只读工具；不写文件、不联网、不调用模型",
        meta="pack.json · cases/*.json · run.json · 终端摘要",
        foot="Apache-2.0 · PerryLink DSH plugin family · v0.1.1",
        panel="评分回执 · eval.grade",
        panel_right="synthetic · 2026-11-02",
        expected="expected", actual="actual",
        path_left="cases/case-03.json",
        path_right="run.json · results[]",
        canonical_label="canonical( )",
        canonical_value='{"gross":108,"net":100,"tax":8}',
        verdict="PASS",
        caption="两侧键序不同，排序后逐字节相等",
        chips=["case-01 pass", "case-02 fail", "case-03 pass"],
        chip_note="3 个样本 · 1 个失败",
        tally="TALLY",
        pk="PASS@K",
        big="2/3",
        line1="pass_rate 0.666667",
        line2="failures [case-02]",
        pk1="pass@1 mean 0.633333",
        pk2="pass@3 mean 0.9",
        foot_note="docs/assets/quickstart.log · 同一次真实运行",
        r0="R0 · read-only",
    ),
    "en": dict(
        kicker="DEEPSEEK HARNESS PLUGIN · EVAL SCORING",
        title="dsh-eval-pack",
        value=["A tiny eval pack, compared exactly",
               "Pass rate, failures, pass@k — now"],
        sub="R0 read-only · no writes · no network · no model call",
        meta="pack.json · cases/*.json · run.json · terminal summary",
        foot="Apache-2.0 · PerryLink DSH plugin family · v0.1.1",
        panel="GRADE RECEIPT · eval.grade",
        panel_right="synthetic · 2026-11-02",
        expected="expected", actual="actual",
        path_left="cases/case-03.json",
        path_right="run.json · results[]",
        canonical_label="canonical( )",
        canonical_value='{"gross":108,"net":100,"tax":8}',
        verdict="PASS",
        caption="different key order — identical bytes after sorting",
        chips=["case-01 pass", "case-02 fail", "case-03 pass"],
        chip_note="3 cases · 1 failure",
        tally="TALLY",
        pk="PASS@K",
        big="2/3",
        line1="pass_rate 0.666667",
        line2="failures [case-02]",
        pk1="pass@1 mean 0.633333",
        pk2="pass@3 mean 0.9",
        foot_note="docs/assets/quickstart.log · the same real run",
        r0="R0 · read-only",
    ),
}


def hero(lang: str, skin: str) -> None:
    """1440x576 banner: the pitch on the left, the grade receipt on the right."""
    s = SKIN[skin]
    H = HERO[lang]
    W, HT = 1440, 576
    img = gradient(W, HT, s["bg_from"], s["bg_to"])
    img = glow(img, 1150, 40, 430, hx(s["accent"]),
               20 if skin == "light" else 38)
    L = Layer(W, HT)

    # ---------------------------------------------------------- receipt panel
    pb = (754, 40, 1386, 536)
    L.shadow(pb, radius=22, blur=18, color=s["shadow"], alpha=s["shadow_a"],
             dy=11)
    L.rect(pb, radius=22, fill=hx(s["card"]), outline=hx(s["edge"]), width=1.2)
    L.line((786, 98), (1354, 98), hx(s["edge"]), 1.0)

    left, right = (786, 106, 1026, 232), (1114, 106, 1354, 232)
    for box in (left, right):
        L.rect(box, radius=16, fill=hx(s["track"]), outline=hx(s["edge"]),
               width=1.1)
    # seam badge
    L.circle(1070, 169, 19, fill=hx(s["card"]), outline=hx(s["green"]),
             width=2.4)
    L.line((1026, 169), (1047, 169), hx(s["green"]), 1.8)
    L.poly([(1051, 169), (1044, 164.6), (1044, 173.4)], hx(s["green"]))
    L.line((1114, 169), (1093, 169), hx(s["green"]), 1.8)
    L.poly([(1089, 169), (1096, 164.6), (1096, 173.4)], hx(s["green"]))
    L.line((1070, 190), (1070, 242), hx(s["green"]), 1.8)
    L.poly([(1070, 246), (1065.6, 239), (1074.4, 239)], hx(s["green"]))

    # canonical strip
    L.rect((786, 250, 1354, 288), radius=19, fill=hx(s["pill"]))

    # per-case chips
    chip_boxes = []
    x = 786
    for label in H["chips"]:
        w = tw(label, 12.5, "mono") + 26
        chip_boxes.append((x, 322, x + w, 350, label))
        x += w + 12
    for x0, y0, x1, y1, label in chip_boxes:
        ok = label.endswith("pass")
        col = s["green"] if ok else s["danger"]
        L.rect((x0, y0, x1, y1), radius=14, fill=hx(s["card"]), outline=hx(col),
               width=1.2)

    base = Image.alpha_composite(img.convert("RGBA"), L.flatten())
    d = ImageDraw.Draw(base)

    # ------------------------------------------------------------- left column
    kx = 60
    kw = tw(H["kicker"], 15, "cjk") + 36
    L2 = Layer(W, HT)
    L2.rect((kx, 44, kx + kw, 78), radius=17, fill=hx(s["pill"]))
    base = Image.alpha_composite(base, L2.flatten())
    d = ImageDraw.Draw(base)

    text(d, (kx + 18, 67), H["kicker"], font(15, "cjk"), s["accent"])

    draw_mixed(d, kx, 208, H["title"], 80, s["text"], "mono_bold")

    y = 276
    for line in H["value"]:
        vs = fit_mixed(line, 36, 656, "cjk_bold", 30)
        draw_mixed(d, kx, y, line, vs, s["text"], "cjk_bold")
        y += 47

    ss = fit_mixed(H["sub"], 26, 656, "cjk", 23)
    draw_mixed(d, kx, 380, H["sub"], ss, s["sub"], "cjk")
    ms = fit_mixed(H["meta"], 20, 656, "mono", 18)
    draw_mixed(d, kx, 428, H["meta"], ms, s["faint"], "mono")
    d.line([kx, 450, kx + 640, 450], fill=hx(s["edge"]), width=2)
    fs = fit_mixed(H["foot"], 16, 656, "cjk", 14)
    draw_mixed(d, kx, 488, H["foot"], fs, s["faint"], "cjk")

    # ------------------------------------------------------------ panel texts
    draw_mixed(d, 786, 86, H["panel"], 15, s["accent"], "mono")
    draw_mixed(d, 1354, 86, H["panel_right"], 12.5, s["faint"], "mono",
               anchor="rs")

    draw_mixed(d, 802, 130, H["expected"], 13, s["accent"], "mono")
    draw_mixed(d, 802, 222, H["path_left"], 12, s["faint"], "mono")
    draw_mixed(d, 1130, 130, H["actual"], 13, s["accent"], "mono")
    draw_mixed(d, 1130, 222, H["path_right"], 12, s["faint"], "mono")

    exp_lines = ['{ "net": 100,', '  "tax": 8,', '  "gross": 108 }']
    act_lines = ['{ "gross": 108,', '  "tax": 8,', '  "net": 100 }']
    for i, (a, b) in enumerate(zip(exp_lines, act_lines)):
        text(d, (802, 160 + i * 20), a, font(14, "mono"), s["text"])
        text(d, (1130, 160 + i * 20), b, font(14, "mono"), s["text"])

    text(d, (1070, 169), "=", font(20, "mono_bold"), s["green"], anchor="mm")

    draw_mixed(d, 802, 274, H["canonical_label"], 13, s["accent"], "mono")
    draw_mixed(d, 926, 274, H["canonical_value"], 13, s["text"], "mono")
    draw_mixed(d, 1338, 274, H["verdict"], 13, s["green"], "mono_bold",
               anchor="rs")

    cs = fit_mixed(H["caption"], 13, 556, "cjk", 12)
    draw_mixed(d, 786, 308, H["caption"], cs, s["sub"], "cjk")

    for x0, y0, x1, y1, label in chip_boxes:
        col = s["green"] if label.endswith("pass") else s["danger"]
        text(d, (x0 + 13, y1 - 8), label, font(12.5, "mono"), col)
    draw_mixed(d, 1354, 344, H["chip_note"], 12.5, s["faint"], "cjk",
               anchor="rs")

    draw_mixed(d, 786, 386, H["tally"], 12, s["accent"], "mono")
    draw_mixed(d, 786, 432, H["big"], 40, s["text"], "mono_bold")
    draw_mixed(d, 874, 406, H["line1"], 13, s["sub"], "mono")
    draw_mixed(d, 874, 430, H["line2"], 12.5, s["danger"], "mono")

    draw_mixed(d, 1150, 386, H["pk"], 12, s["accent"], "mono")
    draw_mixed(d, 1150, 410, H["pk1"], 13, s["sub"], "mono")
    draw_mixed(d, 1150, 434, H["pk2"], 13, s["text"], "mono_bold")

    draw_mixed(d, 786, 508, H["foot_note"], 12.5, s["faint"], "mono")
    draw_mixed(d, 1354, 508, H["r0"], 12.5, s["accent"], "mono", anchor="rs")

    path = os.path.join(OUT, f"dsh-eval-pack-hero-{lang}-{skin}.webp")
    base.convert("RGB").save(path, "WEBP", quality=92)
    print(os.path.basename(path))


# ---------------------------------------------------------------------------
# flow SVG: 1100x660, clause comparison / dual-column adjudication
# ---------------------------------------------------------------------------
FLOW = {
    "light": dict(bg1="#f9f6fd", bg2="#e4eaf8", dots="#d9d3ea",
                  card="#ffffff", edge="#e2dff0", text="#171a24",
                  sub="#555c70", faint="#8a8fa2", accent="#4B67B4",
                  green="#15803d", danger="#b3261e", pill="#ece7f9",
                  track="#f3f0fb", grid="#e6e1f2", shadow="#1b1735",
                  shadow_op=".10"),
    "dark": dict(bg1="#131a2a", bg2="#0c1016", dots="#1e2637",
                 card="#1b2231", edge="#2e374b", text="#eef2fa",
                 sub="#a8b1c4", faint="#737b8d", accent="#8496f5",
                 green="#3fb950", danger="#f87171", pill="#242d42",
                 track="#222b3d", grid="#1b2434", shadow="#000000",
                 shadow_op=".55"),
}

SANS = ("'Microsoft YaHei', 'Segoe UI', system-ui, -apple-system, "
        "sans-serif")
MONO = "Consolas, 'Cascadia Mono', 'Courier New', monospace"


def esc(body: str) -> str:
    return (str(body).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def est_w(body: str, size: float, mono: bool) -> float:
    """Conservative width estimate (CJK ~1em, Latin ~0.6em)."""
    total = 0.0
    for ch in body:
        o = ord(ch)
        if o > 0x2E7F:
            total += size
        elif ch == " ":
            total += size * 0.30
        elif ch in "·•—–≠=≤≥→←":
            total += size * 0.62
        else:
            total += size * (0.62 if mono else 0.56)
    return total


def flow_svg(skin: str) -> str:
    """1100x660: pack gate -> pairwise bench -> two readouts."""
    s = FLOW[skin]
    W, H = 1100, 660
    lines = []
    add = lines.append
    shrunk = []

    def t(x, y, body, size=12.5, fill=None, weight="400", family=SANS,
          anchor="start", ls=None, opacity=None, maxw=None):
        if maxw is not None:
            while size > 11 and est_w(body, size, family == MONO) > maxw:
                size -= 0.25
            if est_w(body, size, family == MONO) > maxw:
                shrunk.append((body, round(size, 2)))
        extra = ""
        if ls:
            extra += f' letter-spacing="{ls}"'
        if opacity:
            extra += f' opacity="{opacity}"'
        add(f'<text x="{x}" y="{y}" fill="{fill or s["text"]}" '
            f'font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'text-anchor="{anchor}"{extra}>{esc(body)}</text>')

    def card(x, y, w, h, r=20, fill=None, stroke=None, sw=1.2):
        add(f'<g filter="url(#soft)"><rect x="{x}" y="{y}" width="{w}" '
            f'height="{h}" rx="{r}" fill="{fill or s["card"]}" '
            f'stroke="{stroke or s["edge"]}" stroke-width="{sw}"/></g>')

    def pill(x, y, w, h, fill, stroke=None, sw=1.1):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
        add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{h / 2}" '
            f'fill="{fill}"{st}/>')

    add(f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="dsh-eval-pack structure: a pack gate (eval.pack_lint) checks pack.json, then the two documents — expected from cases and actual from run.json — are canonicalised on opposite sides of one comparison gutter and compared byte for byte, then eval.summary and eval.pass_at_k produce the readouts">
<title>dsh-eval-pack: one pack gate, one comparison gutter, two readouts</title>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0.25" y2="1">
    <stop offset="0" stop-color="{s['bg1']}"/>
    <stop offset="1" stop-color="{s['bg2']}"/>
  </linearGradient>
  <filter id="soft" x="-30%" y="-30%" width="160%" height="180%">
    <feDropShadow dx="0" dy="7" stdDeviation="10" flood-color="{s['shadow']}" flood-opacity="{s['shadow_op']}"/>
  </filter>
  <pattern id="dots" width="28" height="28" patternUnits="userSpaceOnUse">
    <circle cx="1.4" cy="1.4" r="1.4" fill="{s['dots']}"/>
  </pattern>
  <marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
    <path d="M0 1 L10 5 L0 9 z" fill="{s['accent']}"/>
  </marker>
  <marker id="g" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
    <path d="M0 1 L10 5 L0 9 z" fill="{s['green']}"/>
  </marker>
  <marker id="d" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" orient="auto-start-reverse">
    <path d="M0 1 L10 5 L0 9 z" fill="{s['danger']}"/>
  </marker>
</defs>
<rect width="{W}" height="{H}" fill="url(#bg)"/>
<rect width="{W}" height="{H}" fill="url(#dots)" opacity=".42"/>''')

    # ---------------------------------------------------------------- header
    t(40, 50, "dsh-eval-pack", 28, s["text"], "700", MONO)
    t(40, 76, "one pack gate · one comparison gutter · two readouts", 15,
      s["sub"])
    t(1060, 50, "R0 · v0.1.1 · no writes · no network · no model call", 13,
      s["faint"], "400", MONO, "end", maxw=480)
    t(1060, 74, "4 tools · 9 error codes · alpha · synthetic only", 13,
      s["faint"], "400", MONO, "end", maxw=480)
    add(f'<line x1="40" y1="94" x2="1060" y2="94" stroke="{s["grid"]}"/>')

    # ------------------------------------------------------- 01 pack gate tier
    card(40, 106, 1020, 118, r=20)
    t(62, 132, "01 · PACK GATE · eval.pack_lint", 13, s["accent"], "700",
      MONO, ls="1.1")
    t(1038, 132, "synthetic-invoice-basics@1.0.0 · 3 tasks", 13, s["faint"],
      "400", MONO, "end", maxw=400)

    card(62, 146, 190, 62, r=14, fill=s["track"])
    t(78, 172, "pack.json", 16, s["text"], "700", MONO)
    t(78, 194, "name · version · tasks", 11.5, s["faint"], "400", MONO)

    add(f'<line x1="252" y1="177" x2="272" y2="177" stroke="{s["accent"]}" '
        f'stroke-width="2" marker-end="url(#a)"/>')

    checks = [("name", "non-empty"), ("version", "non-empty"),
              ("tasks", "non-empty"), ("id", "unique")]
    for i, (tag, note) in enumerate(checks):
        x = 278 + i * 112
        card(x, 146, 104, 62, r=12, fill=s["card"])
        add(f'<path d="M{x + 12} {173} l4 5 8 -11" fill="none" '
            f'stroke="{s["green"]}" stroke-width="2.2" stroke-linecap="round" '
            f'stroke-linejoin="round"/>')
        t(x + 32, 176, tag, 14.5, s["text"], "700", MONO)
        t(x + 12, 197, note, 12, s["faint"], "400", MONO)

    add(f'<line x1="728" y1="177" x2="748" y2="177" stroke="{s["accent"]}" '
        f'stroke-width="2" marker-end="url(#a)"/>')

    card(754, 146, 166, 62, r=14, fill=s["track"])
    t(770, 172, "ok = true", 16, s["green"], "700", MONO)
    t(770, 194, "0 errors", 11.5, s["faint"], "400", MONO)
    t(940, 176, "→ grade", 13, s["accent"], "700", MONO)
    t(940, 196, "fail → E_*", 12, s["danger"], "400", MONO)

    # ------------------------------------------------------ 02 comparison tier
    card(40, 252, 1020, 260, r=20)
    t(62, 278, "02 · CANONICAL COMPARE · eval.grade", 13, s["accent"],
      "700", MONO, ls="1.1")
    t(1038, 278, "keys sorted · arrays in order · bytes compared", 13,
      s["faint"], "400", MONO, "end", maxw=400)

    t(62, 302, "cases/*.json · expected", 13.5, s["faint"], "400", MONO)
    t(550, 302, "canonical( )", 13.5, s["accent"], "700", MONO, "middle")
    t(1038, 302, "run.json · results[].actual", 13.5, s["faint"], "400", MONO,
      "end")

    # the single comparison gutter: one channel between the two document columns
    add(f'<rect x="414" y="312" width="272" height="186" rx="18" '
        f'fill="{s["track"]}" opacity=".85"/>')

    rows = [
        dict(y=312, case="case-02", left='{"amount":"12.35","currency":"EUR"}',
             right='{"amount":"12.34","currency":"EUR"}',
             left_path="cases/case-02.json", right_path="run.json · results[]",
             why="one byte differs", sym="≠", verdict="fail",
             col=s["danger"], accent="d"),
        dict(y=408, case="case-03", left='{"net":100,"tax":8,"gross":108}',
             right='{"gross":108,"tax":8,"net":100}',
             left_path="cases/case-03.json", right_path="run.json · results[]",
             why="key order only", sym="=", verdict="pass",
             col=s["green"], accent="g"),
    ]

    for row in rows:
        y0 = row["y"]
        card(62, y0, 342, 90, r=14, fill=s["card"], stroke=row["col"], sw=1.3)
        card(696, y0, 342, 90, r=14, fill=s["card"], stroke=row["col"], sw=1.3)
        # verdict rails, inset from the rounded border
        add(f'<rect x="66" y="{y0 + 19}" width="3" height="52" rx="1.5" '
            f'fill="{row["col"]}"/>')
        add(f'<rect x="1031" y="{y0 + 19}" width="3" height="52" rx="1.5" '
            f'fill="{row["col"]}"/>')

        t(80, y0 + 22, f'{row["case"]} · expected', 13.5, s["faint"], "400",
          MONO)
        t(80, y0 + 58, row["left"], 13.75, s["text"], "400", MONO, maxw=310)
        t(80, y0 + 80, row["left_path"], 12.5, s["faint"], "400", MONO)

        t(1020, y0 + 22, f'{row["case"]} · actual', 13.5, s["faint"], "400",
          MONO, "end")
        t(1020, y0 + 58, row["right"], 13.75, s["text"], "400", MONO, "end",
          maxw=310)
        t(1020, y0 + 80, row["right_path"], 12.5, s["faint"], "400", MONO,
          "end")

        # both sides enter the gutter
        add(f'<line x1="404" y1="{y0 + 52}" x2="428" y2="{y0 + 52}" '
            f'stroke="{row["col"]}" stroke-width="2" '
            f'marker-end="url(#{row["accent"]})"/>')
        add(f'<line x1="696" y1="{y0 + 52}" x2="672" y2="{y0 + 52}" '
            f'stroke="{row["col"]}" stroke-width="2" '
            f'marker-end="url(#{row["accent"]})"/>')

        t(550, y0 + 28, row["why"], 13.5, row["col"], "700", MONO, "middle")
        t(550, y0 + 66, row["sym"], 30, row["col"], "700", MONO, "middle")
        t(550, y0 + 86, row["verdict"], 13.5, row["col"], "700", MONO,
          "middle")

    # --------------------------------------------------------- 03 readouts tier
    card(40, 528, 1020, 96, r=20)
    t(62, 552, "03 · TALLY · eval.summary", 13, s["accent"], "700", MONO,
      ls="1.1")
    t(660, 552, "eval.pass_at_k · k = 3 · sampling[]", 13, s["accent"], "700",
      MONO, ls="1.1")
    add(f'<line x1="646" y1="540" x2="646" y2="612" stroke="{s["grid"]}"/>')

    tally = [("case-01", "pass"), ("case-02", "fail"), ("case-03", "pass")]
    for i, (name, verdict) in enumerate(tally):
        x = 62 + i * 104
        card(x, 560, 96, 46, r=12, fill=s["track"])
        t(x + 10, 578, name, 12.5, s["faint"], "400", MONO)
        t(x + 10, 598, verdict, 13, s["green"] if verdict == "pass"
          else s["danger"], "700", MONO)

    t(384, 600, "2/3", 26, s["text"], "700", MONO)
    t(444, 582, "passed · 0.666667", 13.5, s["sub"], "400", MONO)
    t(444, 604, "failures: case-02", 13.5, s["danger"], "400", MONO)

    t(682, 580, "1 − C(10−3, 3) / C(10, 3)", 13.5, s["text"], "400", MONO,
      maxw=300)
    t(682, 604, "0.991667 · 0.708333 · 1", 13.5, s["sub"], "400", MONO)
    t(1038, 580, "pass@3 mean", 12, s["faint"], "400", MONO, "end")
    t(1038, 606, "0.9", 24, s["text"], "700", MONO, "end")

    # ------------------------------------------------------------------ footer
    add(f'<line x1="40" y1="636" x2="1060" y2="636" stroke="{s["grid"]}"/>')
    t(40, 652, "read-only R0 · no file writes · no network · no model call · "
               "input JSON untouched", 12.5, s["faint"], "400", SANS, maxw=660)
    t(1060, 652, "src/core/harness.ts · src/plugin/tools.ts", 12, s["faint"],
      "400", MONO, "end", maxw=320)

    add("</svg>")
    if shrunk:
        print("  shrunk to fit:", shrunk)
    return "\n".join(lines) + "\n"


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ("light", "dark"):
        for lang in ("zh", "en"):
            hero(lang, skin)
    for skin in ("light", "dark"):
        path = os.path.join(OUT, f"dsh-eval-pack-flow-v5-{skin}.svg")
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(flow_svg(skin))
        print(os.path.basename(path))


if __name__ == "__main__":
    main()
