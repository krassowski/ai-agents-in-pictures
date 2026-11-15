#!/usr/bin/env python3
"""Draw what the simple harness printed with /raw, next to the rows of the context window in part 1.

Usage: python3 llm-raw.py [output.svg]

The text comes from simple-harness/example-raw.txt, the /raw output of the run in simple-harness/README.md.
"""

import re
import sys
from pathlib import Path

from infographic import badge, esc, page, para, path, rect, save, text, text_width, tier

HERE = Path(__file__).resolve().parent
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'llm-raw.svg'
RAW = (HERE.parent / 'simple-harness' / 'example-raw.txt').read_text(encoding='utf-8')
W, M, TOP = 2360, 30, 150
SIZE, LH = 15, 22.5  # raw text size and line step
RX0, RX1 = M + 66, 1545  # the raw text starts at RX0 and wraps before RX1
BX = RX1 + 34  # brackets
ROW_X0, ROW_X1 = BX + 56, W - M - 24
MARKER = re.compile(r'(<bos>|<\|turn>(?:system|user|model)|<turn\|>)')
PART1 = 'llm-context.svg'

# key: (kind, role label, text), as the rows of the window in part 1
ROWS = {
    'system': ('always', None, "Harness's own instructions (system prompt)"),
    'agents': ('always', None, "AGENTS.md: your project's rules, full text"),
    'skills': ('always', None, 'Skill list: a name and a description per skill'),
    'tools': ('always', None, 'Tool list: one tool, read'),
    'task': ('you', 'YOU', 'Write a commit message for my fix of issue 123'),
    'call': ('model', 'MODEL', '`read("skills/commit-message/SKILL.md")`'),
    'skill': ('tool', 'TOOL', 'The commit-message skill: steps to follow'),
    'answer': ('model', 'MODEL', "The commit message, in the skill's format"),
}
KIND = {'always': ('blue', 1), 'you': ('green', None), 'model': ('orange', None), 'tool': ('purple', 2)}

NOTES = [
    (('task', 0), 'Markers such as `<|turn>user` and `<turn|>` come from the chat template in the model file. '
                  'They mark who wrote each part, and the model learned them in training.'),
    (('call', 1), 'The model only writes text. The harness finds the `CALL read(...)` line with a regular '
                  'expression, reads the file and asks the model for its next reply.'),
    (('skill', 1), 'The harness sends the file back in a new turn that starts with `RESULT:`. From here on, the '
                   'skill is in the window for every reply.'),
]

SOURCES = ('Recorded on 15 November 2026 with harness.py, llama-cpp-python 0.3.35 and gemma-4-E4B-it-Q4_0.gguf '
           '(ggml-org/gemma-4-E4B-it-GGUF on Hugging Face), at temperature 0.2 with seed 0. Models trained for '
           'tool calls have their own format for calls and a separate role for results.')
WRAPPED = ' A line that is too long for the picture goes on in the next line, after an arrow.'


def sections(raw):
    """The raw text as [key, lines] items, one for each row of part 1."""
    out = []
    model_turns = 0
    lines = raw.rstrip('\n').split('\n')
    for i, line in enumerate(lines):
        key = None
        if i == 0:
            key = 'system'
        elif line in ('# AGENTS.md', '# Skills', '# Tools'):
            key = {'# AGENTS.md': 'agents', '# Skills': 'skills', '# Tools': 'tools'}[line]
        elif line == '<|turn>user':
            key = 'skill' if lines[i + 1].startswith('RESULT:') else 'task'
        elif line == '<|turn>model':
            model_turns += 1
            key = 'call' if model_turns == 1 else 'answer'
        if key:
            out.append([key, []])
        out[-1][1].append(line)
    return out


def split(line, width):
    """line cut at spaces into pieces that fit in width."""
    pieces, cur = [], ''
    for word in re.split(r'(?<= )', line):
        if cur and text_width(cur + word.rstrip(), SIZE, 'mono') > width:
            pieces.append(cur)
            cur = word
        else:
            cur += word
    return pieces + [cur]


def raw_line(out, x, y, line):
    """One line of raw text, with the markers of the chat template drawn apart from the rest."""
    parts = [f'<tspan class="tok">{esc(p)}</tspan>' if MARKER.fullmatch(p) else esc(p)
             for p in MARKER.split(line) if p]
    out.append(f'<text x="{x:.1f}" y="{y:.1f}" class="mono" style="font-size:{SIZE}px" '
               f'xml:space="preserve">{"".join(parts)}</text>')


def row(out, x0, x1, y, h, key):
    """A row of the window, drawn as in part 1."""
    kind, role, label = ROWS[key]
    color, t = KIND[kind]
    rect(out, x0, y, x1 - x0, h, 'win' if kind == 'always' else f'k-{color}', rx=7)
    if t:
        tier(out, x0 + 9, y + (h - 22) / 2, t)
    tx = x0 + 42
    if role:
        text(out, tx, y + h / 2 + 4.5, role, 12, f't-{color}', bold=True)
        tx += 54
    text(out, tx, y + h / 2 + 5, label, 14.5, '' if kind == 'always' else f't-{color}')


def main():
    raw, spans, ends = [], {}, {}
    wrapped = False
    text(raw, M + 24, TOP + 40, 'What `/raw` printed', 22, bold=True)
    text(raw, M + 24, TOP + 66, 'The model reads these tokens from top to bottom.', 15.5, 'ink2')
    y = TOP + 96
    for key, lines in sections(RAW):
        blank = 0
        while lines and not lines[-1].strip():
            lines.pop()
            blank += 1
        top = y
        for i, line in enumerate(lines):
            pieces = split(line, RX1 - RX0)
            for j, piece in enumerate(pieces):
                if j:
                    text(raw, RX0 - 24, y + LH * 0.7, '↪', SIZE, 'muted')
                    wrapped = True
                raw_line(raw, RX0, y + LH * 0.7, piece)
                y += LH
            ends[(key, i)] = (RX0 + text_width(pieces[-1], SIZE, 'mono'), y - LH / 2)
        spans[key] = (top, y)
        y += LH * blank if blank else LH * 0.4
    raw_bottom = y + 16

    # a band of the row's colour behind each part of the raw text
    bands = []
    for key, (top, bottom) in spans.items():
        kind = ROWS[key][0]
        rect(bands, RX0 - 34, top - 3, RX1 - RX0 + 50, bottom - top + 6,
             'k-blue' if kind == 'always' else f'k-{KIND[kind][0]}', rx=8)

    # a bracket from each band to its row
    rows = []
    text(rows, ROW_X0, TOP + 40, f'Rows of the window in [part 1]({PART1})', 22, bold=True)
    text(rows, ROW_X0, TOP + 66, 'Colours and numbers match part 1.', 15.5, 'ink2')
    for key, (top, bottom) in spans.items():
        mid = (top + bottom) / 2
        path(rows, f'M{BX - 9},{top:.1f} H{BX} V{bottom:.1f} H{BX - 9} M{BX},{mid:.1f} H{ROW_X0}', 'bracket')
        row(rows, ROW_X0, ROW_X1, mid - 19, 38, key)
    text(rows, ROW_X0, spans['system'][0] + 3, 'SENT FIRST, EVERY TIME', 12.5, 't-blue', bold=True)
    text(rows, ROW_X0, spans['task'][0] - 8, 'THE CONVERSATION, GROWING DOWNWARDS', 12.5, 'ink2', bold=True)

    # numbered notes: a badge after the line they are about, and the text under the raw text
    col = (W - 2 * M - 2 * 24) / len(NOTES)
    bottoms = []
    for n, ((key, i), note) in enumerate(NOTES, start=1):
        ex, ey = ends[(key, i)]
        badge(rows, ex + 22, ey, str(n), r=12)
        nx = M + (n - 1) * (col + 24)
        badge(rows, nx + 12, raw_bottom + 40, str(n), r=12)
        bottoms.append(para(rows, nx + 34, raw_bottom + 28, col - 34, note, 15.5))
    bottom = max(bottoms) + 16

    height = bottom + 64
    out = page(W, height, 'What the model reads, as raw text',
               'The simple harness ran one task with Gemma 4 E4B, a small open model that runs on your own computer. '
               f"Its /raw command printed the model's whole window. Each part of it is a row of [part 1]({PART1}).",
               'The raw text that a small model read and wrote during one task in the simple harness: the '
               "harness's instructions, AGENTS.md, the skill list, the tool list, the task, one tool call that "
               'reads a skill, the result and the answer, each matched to a row of the context window in part 1.',
               M)
    rect(out, M, TOP, W - 2 * M, raw_bottom - TOP, 'panel', rx=16)
    out.extend(bands)
    out.extend(raw)
    out.extend(rows)
    para(out, M, bottom + 8, W - 2 * M, SOURCES + (WRAPPED if wrapped else ''), 13, 'muted')
    save(out, OUT)
    print(f'wrote {OUT} ({W}x{height:.0f})')


if __name__ == '__main__':
    main()
