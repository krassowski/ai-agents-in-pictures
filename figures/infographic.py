"""Shared drawing code for the LLM infographics: palette, text layout, shapes, panels and page layout.

Text is wrapped with the metrics of Noto Sans and DejaVu Sans Mono, found with fontconfig, when
Pillow is installed, and with estimated widths otherwise. When fontTools is installed, each SVG
embeds the letters it uses from those fonts, so that every browser draws the text that was measured.
"""

import base64
import html
import io
import itertools
import re
import subprocess
import sys
from functools import lru_cache

try:
    from PIL import ImageFont
except ImportError:
    ImageFont = None
try:
    from fontTools import subset as ft_subset
    from fontTools.ttLib import TTFont
except ImportError:
    ft_subset = None

GAP = 24
PAD = 22


SANS = "'Noto Sans', system-ui, -apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "'DejaVu Sans Mono', Menlo, Consolas, monospace"
FAMILY = {'sans': 'Noto Sans', 'mono': 'DejaVu Sans Mono'}

# The parts of the series, in reading order, for the links at the top of each part.
SERIES = [
    ('llm-context.svg', 'How an AI agent works'),
    ('llm-reply.svg', 'Inside one reply'),
    ('llm-trust.svg', 'Trust and control'),
    ('llm-output.svg', 'Steering and judging AI output'),
]
CODE_SCALE = 0.92
# Source numbers such as [3] are drawn this much smaller, and dim.
REF_SCALE = 0.8
# Lines are wrapped this much shorter than their box, for fonts wider than the measured one.
SLACK = 1.05

LIGHT = {
    'bg': '#fbfaf7', 'panel': '#ffffff', 'panel-line': '#dddbd3', 'ink': '#1c1b19', 'ink2': '#4a4945',
    'muted': '#6b6962', 'code-bg': '#f4f3ef', 'grey-bg': '#f1f0eb', 'grey': '#9a988f', 'grey-ink': '#4a4945',
    'zoom': '#8c8a82',
    'red': '#c8463b',
    'blue-bg': '#e3eefb', 'blue': '#2b6fc6', 'blue-ink': '#133f74',
    'green-bg': '#e1f3e4', 'green': '#2f9446', 'green-ink': '#1c5a2b',
    'orange-bg': '#fde8db', 'orange': '#e0612a', 'orange-ink': '#883310',
    'purple-bg': '#ede9fb', 'purple': '#7357cf', 'purple-ink': '#3e2a86',
    'teal-bg': '#daf1ed', 'teal': '#12907e', 'teal-ink': '#0a594e',
    'yellow-bg': '#fbf1d2', 'yellow': '#c3940f', 'yellow-ink': '#654900',
    'danger-bg': '#fbe3e0', 'danger': '#cc3b30', 'danger-ink': '#7d1a13',
}
DARK = {
    'bg': '#151514', 'panel': '#1e1e1c', 'panel-line': '#3a3934', 'ink': '#f3f2ee', 'ink2': '#c9c7c0',
    'muted': '#918f88', 'code-bg': '#262623', 'grey-bg': '#272725', 'grey': '#77756e', 'grey-ink': '#c9c7c0',
    'zoom': '#9d9b93',
    'red': '#e0675c',
    'blue-bg': '#172a42', 'blue': '#5d9de9', 'blue-ink': '#d0e3fb',
    'green-bg': '#16301d', 'green': '#52b86a', 'green-ink': '#caefd3',
    'orange-bg': '#3b2116', 'orange': '#f0804b', 'orange-ink': '#fcdac8',
    'purple-bg': '#272140', 'purple': '#9b85ec', 'purple-ink': '#e1d9fc',
    'teal-bg': '#10302c', 'teal': '#38baa7', 'teal-ink': '#c7efe8',
    'yellow-bg': '#342a10', 'yellow': '#e0b43c', 'yellow-ink': '#f6e6b5',
    'danger-bg': '#3d1714', 'danger': '#ec6a5e', 'danger-ink': '#fbd3cf',
}

# Colours are written as literal values, because many SVG renderers outside browsers
# (librsvg, Inkscape, office suites) do not support CSS custom properties.
RULES = f"""
text {{{{ font-family: {SANS}; fill: @ink; }}}}
.bg {{{{ fill: @bg; }}}}
.panel {{{{ fill: @panel; stroke: @panel-line; stroke-width: 1.5; }}}}
.center {{{{ fill: @panel; stroke: @ink2; stroke-width: 2; }}}}
.frame {{{{ fill: none; stroke: @grey; stroke-width: 1.5; stroke-dasharray: 7 5; }}}}
.win {{{{ fill: @bg; stroke: @ink2; stroke-width: 1.5; }}}}
.b {{{{ font-weight: 700; }}}}
.c {{{{ font-family: {MONO}; font-size: {CODE_SCALE}em; }}}}
.mono {{{{ font-family: {MONO}; }}}}
.ink2 {{{{ fill: @ink2; }}}}
.muted {{{{ fill: @muted; }}}}
.on-dark {{{{ fill: @bg; }}}}
.dark {{{{ fill: @ink; }}}}
.code-bg {{{{ fill: @code-bg; stroke: @panel-line; stroke-width: 1; }}}}
.note-yellow {{{{ fill: @yellow-bg; stroke: @yellow; stroke-width: 1.2; }}}}
.note-purple {{{{ fill: @purple-bg; stroke: @purple; stroke-width: 1.2; }}}}
.note-grey {{{{ fill: @grey-bg; stroke: @grey; stroke-width: 1.2; }}}}
.ic {{{{ fill: @panel; stroke: @ink2; stroke-width: 1.5; stroke-linejoin: round; }}}}
.ic-line {{{{ fill: none; stroke: @ink2; stroke-width: 1.5; stroke-linejoin: round; stroke-linecap: round; }}}}
.axis {{{{ stroke: @ink2; stroke-width: 1.3; fill: none; }}}}
.curve {{{{ stroke: @purple; stroke-width: 3; fill: none; stroke-linecap: round; }}}}
.area {{{{ fill: @purple-bg; }}}}
.bar {{{{ fill: @purple; opacity: 0.75; }}}}
.limit {{{{ stroke: @red; stroke-width: 2; stroke-dasharray: 8 5; }}}}
.t-red {{{{ fill: @red; }}}}
.slot {{{{ fill: none; stroke: @orange; stroke-width: 1.5; stroke-dasharray: 6 4; }}}}
.bracket {{{{ stroke: @ink2; stroke-width: 2; fill: none; }}}}
.zoom {{{{ fill: none; stroke: @zoom; stroke-width: 1.8; stroke-dasharray: 7 5; }}}}
.halo {{{{ fill: none; stroke: @panel; stroke-width: 7; }}}}
.hl {{{{ fill: @orange-bg; }}}}
.ar {{{{ fill: none; stroke-width: 1.8; }}}}
.blk {{{{ opacity: 0.6; }}}}
.gen {{{{ fill: @orange-ink; stroke: @orange; stroke-width: 1.5; }}}}
.k-think {{{{ fill: @orange-bg; stroke: @orange; stroke-width: 1.4; stroke-dasharray: 5 4; }}}}
.it {{{{ font-style: italic; }}}}
.r {{{{ fill: @muted; font-size: {REF_SCALE}em; }}}}
.slot-danger {{{{ fill: none; stroke: @danger; stroke-width: 2.2; stroke-dasharray: 6 4; }}}}
.tok {{{{ fill: @muted; font-weight: 700; }}}}
a {{{{ cursor: pointer; }}}}
a:hover .lnk {{{{ text-decoration: underline; }}}}
"""

COLORS = ['ink2', 'muted', 'blue', 'green', 'orange', 'purple', 'teal', 'yellow', 'danger']
for _c in ['blue', 'green', 'orange', 'purple', 'teal', 'yellow', 'grey', 'danger']:
    RULES += (f'.k-{_c} {{{{ fill: @{_c}-bg; stroke: @{_c}; stroke-width: 1.4; }}}}\n'
              f'.t-{_c} {{{{ fill: @{_c}-ink; }}}}\n'
              f'.f-{_c} {{{{ fill: @{_c}; }}}}\n')
for _c in COLORS:
    RULES += f'.ar-{_c} {{{{ stroke: @{_c}; }}}} .mk-{_c} {{{{ fill: @{_c}; }}}}\n'


def css(palette):
    """RULES with each @name replaced by its colour, longest names first."""
    out = RULES.format()
    for name in sorted(palette, key=len, reverse=True):
        out = out.replace('@' + name, palette[name])
    return out


STYLE = css(LIGHT) + '@media (prefers-color-scheme: dark) {\n' + css(DARK) + '}\n'


# ----------------------------------------------------------------- text metrics

@lru_cache(None)
def font_file(kind, bold, italic=False):
    """The path of the font file that fontconfig picks for this face, or None."""
    pattern = FAMILY[kind] + (':bold' if bold else '') + (':italic' if italic else '')
    try:
        return subprocess.run(['fc-match', '-f', '%{file}', pattern], capture_output=True,
                              text=True, check=True).stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


@lru_cache(None)
def _font(kind, bold):
    path = font_file(kind, bold)
    if ImageFont is None or path is None:
        return None
    try:
        return ImageFont.truetype(path, 100)
    except OSError:
        return None


def text_width(s, size, kind='sans', bold=False):
    font = _font(kind, bold)
    if font is None:
        return len(s) * size * (0.61 if kind == 'mono' else 0.56)
    return font.getlength(s) * size / 100


def esc(s):
    return html.escape(s, quote=False)


STYLE_RE = re.compile(r'(\*\*.+?\*\*|`.+?`|\[[^\]]+\]\([^)\s]+\)|\[\d+(?:,\s*\d+)*\])')
REF_RE = re.compile(r'\[\d+(?:,\s*\d+)*\]')
LINK_RE = re.compile(r'\[([^\]]+)\]\(([^)\s]+)\)')


def words(markup):
    """Split markup with **bold**, `code` and [links](url) into [word, style, space_after] items.

    The style of a link is 'a' and its URL, for example 'a llm-reply.svg'.
    """
    out = []
    for part in STYLE_RE.split(markup):
        if not part:
            continue
        link = LINK_RE.fullmatch(part)
        if part.startswith('**'):
            text, style = part[2:-2], 'b'
        elif part.startswith('`'):
            text, style = part[1:-1], 'c'
        elif REF_RE.fullmatch(part):
            text, style = part, 'r'
        elif link:
            text, style = link.group(1), 'a ' + link.group(2)
        else:
            text, style = part, 'n'
        if style == 'c' and text[:1] == ' ' and (not out or out[-1][2]):
            lead = len(text) - len(text.lstrip(' '))
            text = '\u00a0' * lead + text[lead:]
        elif text[:1].isspace() and out:
            out[-1][2] = True
        # split on ordinary spaces only, so the no-break spaces of an indent stay with their word
        for m in re.finditer(r'([^ \t\n]+)([ \t\n]*)', text):
            out.append([m.group(1), style, bool(m.group(2))])
    return out


def word_width(word, style, size, bold):
    if style == 'c':
        return text_width(word, size * CODE_SCALE, 'mono')
    if style == 'r':
        return text_width(word, size * REF_SCALE)
    return text_width(word, size, 'sans', bold or style == 'b')


def wrap(markup, size, width, bold=False):
    space = text_width(' ', size)
    lines, cur, cur_w = [], [], 0.0
    for w in words(markup):
        ww = word_width(w[0], w[1], size, bold)
        extra = ww + (space if cur and cur[-1][2] else 0)
        if cur and (cur_w + extra) * SLACK > width:
            lines.append(cur)
            cur, cur_w = [w], ww
        else:
            cur.append(w)
            cur_w += extra
    if cur:
        lines.append(cur)
    return lines


def markup_width(markup, size, bold=False):
    space = text_width(' ', size)
    ws = words(markup)
    return sum(word_width(w[0], w[1], size, bold) for w in ws) + space * sum(1 for w in ws[:-1] if w[2])


def tspans(line):
    parts = []
    for i, (w, st, sp) in enumerate(line):
        t = w + (' ' if sp and i < len(line) - 1 else '')
        if parts and parts[-1][1] == st:
            parts[-1][0] += t
        else:
            # a space after code goes in the next run, so it has the width of a proportional space,
            # and a space after a link goes there too, so it is not underlined
            if parts and parts[-1][1][0] in 'ca' and parts[-1][0].endswith(' '):
                parts[-1][0] = parts[-1][0][:-1]
                t = ' ' + t
            parts.append([t, st])
    out = []
    for t, st in parts:
        if st == 'n':
            out.append(esc(t))
        elif st.startswith('a '):
            out.append(f'<a href="{html.escape(st[2:])}"><tspan class="lnk">{esc(t)}</tspan></a>')
        else:
            out.append(f'<tspan class="{st}">{esc(t)}</tspan>')
    return ''.join(out)


def text(out, x, y, markup, size, cls='', anchor='start', bold=False, extra=''):
    """One line of text with its baseline at y."""
    classes = ' '.join(c for c in [cls, 'b' if bold else ''] if c)
    a = '' if anchor == 'start' else f' text-anchor="{anchor}"'
    line = [w for w in words(markup)]
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" class="{classes}" style="font-size:{size}px"{a}{extra}'
               f' xml:space="preserve">{tspans(line)}</text>')


def para(out, x, y, width, markup, size=16, cls='', lh=1.42, bold=False, anchor='start'):
    """Wrapped text whose first line box starts at y. Returns the y below the last line."""
    step = size * lh
    for i, line in enumerate(wrap(markup, size, width, bold)):
        base = y + i * step + step / 2 + size * 0.35
        classes = ' '.join(c for c in [cls, 'b' if bold else ''] if c)
        a = '' if anchor == 'start' else f' text-anchor="{anchor}"'
        out.append(f'<text x="{x:.1f}" y="{base:.1f}" class="{classes}" style="font-size:{size}px"{a}'
                   f' xml:space="preserve">{tspans(line)}</text>')
    return y + len(wrap(markup, size, width, bold)) * step


# ----------------------------------------------------------------- embedded fonts

TEXT_RE = re.compile(r'<text\b([^>]*)>(.*?)</text>', re.S)
TSPAN_RE = re.compile(r'<tspan\b([^>]*)>(.*?)</tspan>', re.S)
CLASS_RE = re.compile(r'\bclass="([^"]*)"')


def _classes(attrs):
    m = CLASS_RE.search(attrs)
    return set(m.group(1).split()) if m else set()


def faces_used(svg):
    """The letters drawn in each face, as {(kind, bold, italic): set of characters}."""
    used = {}

    def add(classes, s):
        face = ('mono' if classes & {'c', 'mono'} else 'sans', bool(classes & {'b', 'tok'}), 'it' in classes)
        used.setdefault(face, set()).update(html.unescape(s))

    for attrs, body in TEXT_RE.findall(svg):
        base = _classes(attrs)
        body = re.sub(r'</?a\b[^>]*>', '', body)
        pos = 0
        for m in TSPAN_RE.finditer(body):
            add(base, body[pos:m.start()])
            add(base | _classes(m.group(1)), m.group(2))
            pos = m.end()
        add(base, body[pos:])
    return used


@lru_cache(None)
def _woff(path, chars):
    """A WOFF subset of the font at path with only these characters, in base64."""
    options = ft_subset.Options()
    options.name_IDs = ['*']  # keeps the copyright and licence entries
    options.drop_tables += ['FFTM']  # a FontForge timestamp
    font = TTFont(path, recalcTimestamp=False)
    subsetter = ft_subset.Subsetter(options)
    subsetter.populate(text=chars)
    subsetter.subset(font)
    font.flavor = 'woff'
    buf = io.BytesIO()
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode('ascii')


def embed_fonts(svg):
    """svg with @font-face rules for the letters it draws, so that it looks the same everywhere."""
    if ft_subset is None:
        print('fontTools is not installed, so the SVG uses the fonts of the computer that shows it',
              file=sys.stderr)
        return svg
    rules = []
    for (kind, bold, italic), chars in sorted(faces_used(svg).items()):
        path = font_file(kind, bold, italic)
        chars = ''.join(sorted(chars - {'\n'}))
        if path is None or not chars.strip():
            continue
        rules.append(f"@font-face {{ font-family: '{FAMILY[kind]}'; font-weight: {700 if bold else 400}; "
                     f"font-style: {'italic' if italic else 'normal'}; "
                     f"src: url(data:font/woff;base64,{_woff(path, chars)}) format('woff'); }}")
    return svg.replace('<style>', '<style>\n' + '\n'.join(rules), 1)


# ----------------------------------------------------------------- shapes

def rect(out, x, y, w, h, cls, rx=8):
    out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" class="{cls}"/>')


def path(out, d, cls):
    out.append(f'<path d="{d}" class="{cls}"/>')


def arrow(out, pts, color='ink2', both=False, dash=False):
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    start = f' marker-start="url(#ah-{color})"' if both else ''
    style = ' stroke-dasharray="6 4"' if dash else ''
    out.append(f'<path d="{d}" class="ar ar-{color}" marker-end="url(#ah-{color})"{start}{style}/>')


def badge(out, cx, cy, label, r=14, cls='dark', tcls='on-dark'):
    out.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" class="{cls}"/>')
    text(out, cx, cy + r * 0.36, label, r * 1.05, tcls, anchor='middle', bold=True)


def tier(out, x, y, n, size=22):
    """Square badge for the context tiers 1, 2 and 3."""
    color = {1: 'blue', 2: 'purple', 3: 'teal'}[n]
    rect(out, x, y, size, size, f'f-{color}', rx=5)
    text(out, x + size / 2, y + size * 0.72, str(n), size * 0.68, 'on-dark', anchor='middle', bold=True)


def icon(out, kind, x, y):
    """Small icons, about 24 by 24, top-left corner at x, y."""
    if kind == 'file':
        path(out, f'M{x+3},{y} h13 l6,6 v18 h-19 z', 'ic')
        path(out, f'M{x+16},{y} v6 h6 M{x+7},{y+12} h10 M{x+7},{y+17} h10', 'ic-line')
    elif kind == 'folder':
        path(out, f'M{x},{y+4} h9 l3,3 h12 v15 h-24 z', 'ic')
    elif kind == 'term':
        rect(out, x, y + 2, 24, 20, 'ic', rx=3)
        path(out, f'M{x+5},{y+8} l4,4 l-4,4 M{x+12},{y+17} h6', 'ic-line')
    elif kind == 'plug':
        rect(out, x + 5, y + 7, 14, 11, 'ic', rx=2)
        path(out, f'M{x+9},{y+1} v6 M{x+15},{y+1} v6 M{x+12},{y+18} v6', 'ic-line')
    elif kind == 'window':
        rect(out, x, y + 2, 24, 20, 'ic', rx=3)
        path(out, f'M{x},{y+8} h24', 'ic-line')
    elif kind == 'person':
        out.append(f'<circle cx="{x+12}" cy="{y+7}" r="5" class="ic"/>')
        path(out, f'M{x+3},{y+23} a9,9 0 0 1 18,0 z', 'ic')
    elif kind == 'globe':
        out.append(f'<circle cx="{x+12}" cy="{y+12}" r="10" class="ic"/>')
        path(out, f'M{x+2},{y+12} h20 M{x+12},{y+2} c-6,6 -6,14 0,20 c6,-6 6,-14 0,-20', 'ic-line')
    elif kind == 'key':
        out.append(f'<circle cx="{x+7}" cy="{y+12}" r="5" class="ic"/>')
        path(out, f'M{x+12},{y+12} h11 M{x+19},{y+12} v4 M{x+22},{y+12} v3', 'ic-line')
    elif kind == 'cloud':
        path(out, f'M{x+6},{y+20} a5,5 0 0 1 0,-10 a7,7 0 0 1 13,-2 a5,5 0 0 1 1,12 z', 'ic')
    elif kind == 'clock':
        out.append(f'<circle cx="{x+12}" cy="{y+12}" r="10" class="ic"/>')
        path(out, f'M{x+12},{y+6} v6 h5', 'ic-line')
    elif kind == 'shield':
        path(out, f'M{x+12},{y+1} l9,4 v6 c0,6 -4,10 -9,12 c-5,-2 -9,-6 -9,-12 v-6 z', 'ic')


def zoom(out, x, y, w, h, letter, side):
    """Dashed outline around a part of the centre, with its letter on one side. Returns the letter's centre."""
    rect(out, x, y, w, h, 'zoom', rx=10)
    cx = x + w if side == 'right' else x
    cy = y + h / 2
    return cx, cy


# ----------------------------------------------------------------- panels

class Panel:
    def __init__(self, letter, title, body):
        self.letter, self.title, self.body = letter, title, body

    def draw(self, out, x, y, w, h=None):
        inner = []
        x0, iw = x + PAD, w - 2 * PAD
        tx = x0 + (44 if self.letter else 0)
        ty = y + 16
        yb = para(inner, tx, ty, x0 + iw - tx, self.title, size=22, lh=1.3, bold=True)
        if self.letter:
            badge(inner, x0 + 16, ty + 14, self.letter, r=16)
        yb = max(yb, ty + 32) + 12
        yend = self.body(inner, x0, yb, iw)
        height = yend + PAD - y if h is None else h
        rect(out, x, y, w, height, 'panel', rx=14)
        out.extend(inner)
        return height


def numbered(out, x, y, w, items, size=15.5, color='ink2'):
    for i, item in enumerate(items):
        badge(out, x + 11, y + size * 0.71, str(i + 1), r=11, cls=f'f-{color}' if color != 'ink2' else 'dark')
        y = para(out, x + 30, y, w - 30, item, size) + 6
    return y


def note(out, x, y, w, markup, cls='note-yellow', size=15.5):
    inner = []
    yb = para(inner, x + 14, y + 10, w - 28, markup, size)
    rect(out, x, y, w, yb - y + 10, cls, rx=10)
    out.extend(inner)
    return yb + 10



def mini_window(out, x, y, w, rows, title, rh=22, rs=27):
    """A small window drawn as coloured rows; rows maps a row index to (colour, label)."""
    n = max(rows) + 1
    text(out, x, y + 12, title, 13, 'ink2', bold=True)
    rect(out, x, y + 20, w, n * rs + 8, 'win', rx=8)
    centres = {}
    for i, (c, label) in rows.items():
        ry = y + 26 + i * rs
        if c:
            rect(out, x + 6, ry, w - 12, rh, f'k-{c}', rx=4)
            text(out, x + 13, ry + 15.5, label, 12.5, f't-{c}')
        else:
            text(out, x + w / 2, ry + 15.5, label, 12.5, 'muted', anchor='middle')
        centres[i] = ry + rh / 2
    return y + 20 + n * rs + 8, centres



def step_header(out, x, y, n, title, desc, w):
    badge(out, x + 16, y + 16, str(n), r=16)
    text(out, x + 44, y + 23, title, 20, bold=True)
    tw = markup_width(title, 20, bold=True)
    text(out, x + 56 + tw, y + 23, desc, 15.5, 'ink2')
    if markup_width(desc, 15.5) > w - 60 - tw:
        print(f'step {n} description too wide', file=sys.stderr)
    return y + 46


GLOSSARY = {
    'model': '**Model:** the neural network that reads text and images and writes text, for example Claude '
             'Opus, GPT-5 or Gemini. Open-weight models such as Qwen or DeepSeek can also run on your own '
             'hardware.',
    'harness': '**Harness:** the program around the model. It builds the context window, sends it to the model, '
               'runs the tools and asks for your permission. For example Claude Code, Codex CLI, Gemini CLI, '
               'Cursor, Pi or OpenCode.',
    'agent': '**Agent:** a model and a harness in a loop: the model writes tool calls, and the harness runs them '
             'and adds the results, until the task is done.',
    'provider': '**Provider:** the company that runs the model on its servers, for example Anthropic, OpenAI or '
                'Google. It bills per token, or per month with limits counted in tokens. An open-weight model '
                'can also run on your own computer.',
    'token': '**Token:** a piece of a word. 1,000 tokens are roughly 550 to 750 English words, depending on the '
             'model.',
    'window': '**Context window:** all the text the model reads to write its next reply. Its size has a limit, '
              'for example 1,000,000 tokens.',
    'session': '**Session:** one conversation with its own context window. A new session starts with an empty '
               'conversation.',
    'tool': '**Tool:** a program that the harness runs for the model, for example to read or change a file, run '
            'a command or call another system.',
    'tool-call': '**Tool call:** text in an agreed format that names a tool and its inputs. The model writes it, '
                 'and the harness runs the tool.',
    'skill': '**Skill:** a folder with instructions in a SKILL.md file. The model reads the file with a tool '
             'call when a task needs it.',
    'mcp': '**MCP:** a standard way for a harness to use tools from other programs, called MCP servers.',
    'setup': '**Set-up text:** what every request starts with: the harness\'s instructions, AGENTS.md, the '
             'memory index, and the lists of skills and tools.',
    'request': '**Request:** one round trip. The model gets the whole context window and writes one reply.',
    'cache': "**Cache:** the provider's store of work already done on the start of a window. It is reused for a "
             'few minutes, when the next request starts with the same text.',
    'training': '**Training:** how a model is built, from text collected up to a cutoff date. The model does not '
                'change while you use it.',
    'ratings': '**Training on human ratings:** a late step in training, where people, or models built from their '
               'choices, score answers. The model learns to write the answers that score well.',
}


def glossary(*keys, extra=None):
    """A panel body with the shared definitions for keys, in that order."""
    def body(out, x, y, w):
        for key in keys:
            y = para(out, x, y, w, GLOSSARY[key] + (extra.get(key, '') if extra else ''), 15) + 5
        return y - 5
    return body


# ----------------------------------------------------------------- page

class Geometry:
    """Canvas width, side column width and where the centre starts and ends."""

    def __init__(self, width, col=540, top=150, margin=30):
        self.W, self.COL, self.TOP = width, col, top
        self.LX = margin
        self.RX = width - margin - col
        self.CX0 = self.LX + col + 30
        self.CX1 = self.RX - 30


def stack(out, panels, x, y0, y1, col):
    heights = [p.draw([], x, 0, col) for p in panels]
    need = sum(heights) + GAP * (len(panels) - 1)
    spare = max(0, (y1 - y0) - need)
    heights = [h + spare / len(panels) for h in heights]
    boxes = {}
    y = y0
    for p, h in zip(panels, heights):
        p.draw(out, x, y, col, h)
        boxes[p.letter] = (x, y, col, h)
        y += h + GAP
    return boxes, y0 + need


def crossings(ends, xs):
    """How often the elbow connectors cross when connector i turns at xs[i]."""
    def horizontals(e, gx):
        return [(e[1], e[0], gx), (e[3], gx, e[2])]

    count = 0
    for i, j in itertools.permutations(range(len(ends)), 2):
        y0, y1 = sorted((ends[j][1], ends[j][3]))
        for hy, hx0, hx1 in horizontals(ends[i], xs[i]):
            if y0 < hy < y1 and min(hx0, hx1) < xs[j] < max(hx0, hx1):
                count += 1
    return count


def build(geo, out_path, title, subtitle, desc, left, right, draw_centre, sources):
    """Lay out the side panels and the centre, join them with zoom connectors and write the SVG.

    draw_centre(out, top, extra) draws the centre, spreading extra height where it fits,
    and returns the zoom anchors by letter and the bottom of its content.
    """
    W, TOP, LX, RX, CX0, CX1 = geo.W, geo.TOP, geo.LX, geo.RX, geo.CX0, geo.CX1
    _, centre_bottom = draw_centre([], TOP)
    _, lneed = stack([], left, LX, TOP, TOP, geo.COL)
    _, rneed = stack([], right, RX, TOP, TOP, geo.COL)
    bottom = max(centre_bottom + 22, lneed, rneed)
    print(f'left column {lneed:.0f}, right column {rneed:.0f}, centre {centre_bottom + 22:.0f}')
    centre = []
    anchors, _ = draw_centre(centre, TOP, bottom - centre_bottom - 22)
    body = []
    lboxes, _ = stack(body, left, LX, TOP, bottom, geo.COL)
    rboxes, _ = stack(body, right, RX, TOP, bottom, geo.COL)
    boxes = {**lboxes, **rboxes}

    # the sources are drawn below the panels, and the page ends one side margin below their last line
    height = para([], LX, bottom + 22, W - 2 * LX, sources, 13) + LX
    out = page(W, height, title, subtitle, desc, LX, out_path.name)
    rect(out, CX0, TOP, CX1 - CX0, bottom - TOP, 'center', rx=16)
    out.extend(centre)
    out.extend(body)

    # zoom connectors on top of everything; one that cannot run straight turns in the gap between columns
    ends = {}
    for letter, (ax, ay) in anchors.items():
        bx, by, bw, bh = boxes[letter]
        right = bx > ax
        ends[letter] = (ax, ay, bx if right else bx + bw, min(max(ay, by + 30), by + bh - 30), right)
    turns = {}
    for right, gap in ((False, (LX + geo.COL, CX0)), (True, (RX, CX1))):
        bent = sorted((k for k, e in ends.items() if e[4] == right and abs(e[3] - e[1]) >= 1),
                      key=lambda k: ends[k][1])
        slots = [gap[0] + (gap[1] - gap[0]) * (i + 1) / (len(bent) + 1) for i in range(len(bent))]
        best = min(itertools.permutations(slots), key=lambda xs: crossings([ends[k] for k in bent], xs))
        turns.update(zip(bent, best))
    for letter, (ax, ay, px, py, _) in ends.items():
        if letter in turns:
            d = f'M{ax:.1f},{ay:.1f} H{turns[letter]:.1f} V{py:.1f} H{px:.1f}'
        else:
            d = f'M{ax:.1f},{ay:.1f} L{px:.1f},{py:.1f}'
        out.append(f'<path d="{d}" class="halo"/>')
        out.append(f'<path d="{d}" class="zoom"/>')
        badge(out, ax, ay, letter, r=15)

    para(out, LX, bottom + 22, W - 2 * LX, sources, 13, 'muted')
    save(out, out_path)
    print(f'wrote {out_path} ({W}x{height:.0f})')


def page(W, height, title, subtitle, desc, margin, name=None):
    """The start of an SVG page: style, arrow heads, background and heading.

    A part of the series, named by its file name, also gets links to the other parts.
    """
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {height:.0f}" width="{W}" '
           f'height="{height:.0f}" role="img" aria-labelledby="title desc" font-family="{SANS}">',
           f'<title id="title">{esc(title)}</title>',
           f'<desc id="desc">{esc(desc)}</desc>',
           f'<style>{STYLE}</style>', '<defs>']
    for c in COLORS:
        out.append(f'<marker id="ah-{c}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="6.5" '
                   f'markerHeight="6.5" orient="auto-start-reverse"><path d="M0,0.5 L10,5 L0,9.5 z" '
                   f'class="mk-{c}"/></marker>')
    out.append('</defs>')
    rect(out, 0, 0, W, height, 'bg', rx=0)
    text(out, margin, 64, title, 42, bold=True)
    text(out, margin, 104, subtitle, 20, 'ink2')
    if name in dict(SERIES):
        items = [f'**{i}. {t}**' if n == name else f'{i}. [{t}]({n})' for i, (n, t) in enumerate(SERIES, 1)]
        gap = 28
        x = W - margin - sum(markup_width(m, 16) for m in items) - gap * (len(items) - 1)
        for markup in items:
            text(out, x, 62, markup, 16, 'ink2' if markup.startswith('**') else 'muted')
            x += markup_width(markup, 16) + gap
    return out


def save(out, out_path):
    """Close the SVG, embed the letters of its fonts and write it."""
    out_path.write_text(embed_fonts('\n'.join(out + ['</svg>']) + '\n'))
