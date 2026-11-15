#!/usr/bin/env python3
"""Draw an infographic on what happens inside one reply of a language model.

Usage: python3 llm-reply.py [output.svg]
"""

import sys
from pathlib import Path

from infographic import (Geometry, Panel, arrow, build, glossary, para, path, rect, step_header,
                         text, text_width, zoom)

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_suffix('.svg')
GEO = Geometry(2360)
CX0, CX1 = GEO.CX0, GEO.CX1

# Numbered in the order a reader meets them.
SOURCES = [
    'OpenAI, "Key concepts", tokens (developers.openai.com/api/docs/concepts)',
    'Anthropic, "Pricing" (platform.claude.com/docs/en/about-claude/pricing)',
    'Anthropic, "Prompt caching" (platform.claude.com/docs/en/build-with-claude/prompt-caching)',
    'OpenAI, "Reasoning models" (developers.openai.com/api/docs/guides/reasoning)',
    'Google, "Gemini thinking" (ai.google.dev/gemini-api/docs/thinking)',
    'Anthropic, "Effort" (platform.claude.com/docs/en/build-with-claude/effort)',
    'Anthropic, "Thinking" (platform.claude.com/docs/en/build-with-claude/thinking)',
    'Anthropic, "Context windows" (platform.claude.com/docs/en/build-with-claude/context-windows)',
]

# Made-up prices in dollars per million tokens, and token counts for the example reply.
PRICE_IN, PRICE_CACHED, PRICE_OUT = 1.50, 0.15, 7.50
CACHED, NEW, THINK, ANSWER = 48_000, 2_000, 3_000, 500


def cents(tokens, price):
    return tokens * price / 1e4


def blocks(out, x, y, seq, w=12, h=26, gap=3):
    """A row of small blocks, one per class in seq. Returns the x after the last block."""
    for i, cls in enumerate(seq):
        rect(out, x + i * (w + gap), y, w, h, cls, rx=2.5)
    return x + len(seq) * (w + gap) - gap


def brace(out, x0, x1, y, label, up=True, cls='muted', size=13):
    """A square bracket over (or under) x0..x1 with a label."""
    d = 5 if up else -5
    path(out, f'M{x0},{y+d} V{y} H{x1} V{y+d}', 'ic-line')
    text(out, x0, y - 7 if up else y + 17, label, size, cls)


def window_seq(n_new, new_cls='f-purple blk'):
    seq = ['f-blue blk'] * 6 + ['f-green blk'] + ['f-orange blk', 'f-purple blk'] * 20 + ['f-orange blk']
    return seq + [new_cls] * n_new


# ----------------------------------------------------------------- panels

body_words = glossary('model', 'harness', 'provider', 'token', 'request', 'window', 'cache',
                      extra={'token': ' [1, 2]', 'cache': ' [3]'})


def body_effort(out, x, y, w):
    unit = (w - 100 - 120) / 12
    for i, (level, n, a, note_text) in enumerate([('low', 1, 1.2, 'fast, cheap'), ('medium', 4, 2, ''),
                                                  ('high', 10, 2, 'slow, costly')]):
        ry = y + i * 36
        text(out, x, ry + 19, level, 14.5, 'ink2', bold=True)
        rect(out, x + 76, ry + 4, n * unit, 22, 'k-think', rx=4)
        rect(out, x + 80 + n * unit, ry + 4, a * unit, 22, 'k-orange', rx=4)
        if note_text:
            text(out, x + 88 + (n + a) * unit, ry + 20, note_text, 13.5, 'muted')
    y += 3 * 36 + 4
    rect(out, x + 76, y, 14, 14, 'k-think', rx=3)
    text(out, x + 96, y + 12, 'thinking', 13, 'muted')
    rect(out, x + 170, y, 14, 14, 'k-orange', rx=3)
    text(out, x + 190, y + 12, 'answer', 13, 'muted')
    text(out, x + w, y + 12, 'illustrative', 13, 'muted', anchor='end')
    y += 28
    y = para(out, x, y, w, '**Effort**, or thinking level, is a setting that the harness sends with each '
             'request. The names differ between providers, for example none, minimal, low, medium, high, '
             'xhigh or max. [4, 5, 6]', 15.5) + 6
    y = para(out, x, y, w, 'Higher effort makes the model think longer and check more, often with more tool '
             'calls, and it changes the answer too. That costs time and tokens. It often helps on hard tasks '
             'and wastes both on easy ones. [4, 6]', 15.5) + 6
    return para(out, x, y, w, 'Effort is guidance, and the amount of thinking still varies from task to task. '
                '[5, 6]', 15.5)


def body_think(out, x, y, w):
    inner = []
    yb = para(inner, x + 14, y + 10, w - 100, 'Users are logged out after exactly one minute. Maybe the timeout '
              'is stored in seconds but compared in milliseconds. Check session.ts first.', 14, 't-orange it')
    rect(out, x, y, w, yb - y + 10, 'k-think', rx=10)
    out.extend(inner)
    text(out, x + w - 12, y + 18, 'thinking', 12.5, 't-orange', anchor='end', bold=True)
    y = yb + 10
    arrow(out, [(x + 40, y + 2), (x + 40, y + 22)], 'orange')
    y += 26
    inner = []
    yb = para(inner, x + 14, y + 10, w - 100, 'The timeout was in seconds, not milliseconds. I changed '
              'session.ts and added a test.', 14, 't-orange')
    rect(out, x, y, w, yb - y + 10, 'k-orange', rx=10)
    out.extend(inner)
    text(out, x + w - 12, y + 18, 'answer', 12.5, 't-orange', anchor='end', bold=True)
    y = yb + 10 + 14
    y = para(out, x, y, w, 'Before it answers, the model can write text for itself: it plans, tries ideas and '
             'checks them. The answer can then use what the thinking found.', 15.5) + 6
    y = para(out, x, y, w, 'Thinking tokens are billed as output, count toward the output limit, and take '
             'space in the window. [4, 5, 7]', 15.5) + 10
    text(out, x, y + 15, 'What these providers show you: [4, 5, 7]', 14.5, 'ink2', bold=True)
    y += 26
    cx = x
    for label in ['a summary', 'nothing']:
        tw = text_width(label, 14) + 24
        rect(out, cx, y, tw, 28, 'k-think', rx=14)
        text(out, cx + tw / 2, y + 19, label, 14, 't-orange', anchor='middle')
        cx += tw + 10
    y += 28 + 12
    return para(out, x, y, w, 'Whether the next request still contains the thinking depends on the model: some '
                'keep it, some drop it. [4, 7]', 15.5)


def body_probs(out, x, y, w):
    text(out, x, y + 15, 'After "The tests", the next token could be:', 15, 'ink2')
    y += 28
    items = [(' pass', 46), (' fail', 22), (' are', 12), (' now', 7), (' still', 5), ('others', 8)]
    bx = x + 86
    scale = (w - 86 - 50) / 46
    for i, (tok, pct) in enumerate(items):
        ry = y + i * 30
        text(out, x, ry + 18, f'"{tok}"' if tok != 'others' else 'others', 14, 'mono ink2')
        rect(out, bx, ry + 4, pct * scale, 20, 'bar', rx=3)
        text(out, bx + pct * scale + 8, ry + 19, f'{pct}%', 14, 'ink2')
    y += len(items) * 30 + 2
    y = para(out, x, y, w, 'Numbers are illustrative.', 12.5, 'muted') + 10
    y = para(out, x, y, w, 'At each step the model gives every possible next token a probability. The provider '
             'then picks one at random, weighted by those probabilities.', 15.5) + 6
    y = para(out, x, y, w, '**Temperature** sets how often the pick goes past the most likely token. Some models '
             'let the harness set it, and on others it is fixed. [7]', 15.5) + 10
    text(out, x, y + 15, 'Two runs with the same window:', 14.5, 'ink2', bold=True)
    y += 26
    for i, (pick, rest) in enumerate([(' pass', '. Done.'), (' fail', ' on CI because the timeout...')]):
        ry = y + i * 34
        tx = x
        for tok, cls in [('The', 'k-orange'), (' tests', 'k-orange'), (pick, 'gen'), (rest, 'k-orange')]:
            tw = text_width(tok, 14, 'mono') + 14
            rect(out, tx, ry, tw, 26, cls, rx=5)
            text(out, tx + 7, ry + 18, tok, 14, 'mono on-dark' if cls == 'gen' else 'mono t-orange')
            tx += tw + 4
    y += 2 * 34 + 6
    return para(out, x, y, w, 'Each picked token becomes part of the text for the next step, so one different '
                'pick can change the rest of the reply.', 15.5)


def body_limits(out, x, y, w):
    text(out, x, y + 15, 'Context window, for example 1,000,000 tokens [8]', 14, 'ink2', bold=True)
    y += 24
    kx = x
    for cls, label in [('k-blue', 'input, 50,000 tokens'), ('k-orange', 'this reply, up to the output limit'),
                       ('win', 'free')]:
        rect(out, kx, y + 2, 14, 14, cls, rx=3)
        text(out, kx + 20, y + 14, label, 13, 'muted')
        kx += 20 + text_width(label, 13) + 18
    y += 24
    rect(out, x, y, w, 30, 'win', rx=6)
    seg = (w - 6) / 1000
    rect(out, x + 2, y + 3, 50 * seg, 24, 'k-blue', rx=4)
    rx0 = x + 4 + 50 * seg
    rect(out, rx0, y + 3, 128 * seg, 24, 'k-orange', rx=4)
    y += 30
    path(out, f'M{rx0},{y} L{x},{y+26} M{rx0 + 128 * seg},{y} L{x + w},{y+26}', 'zoom')
    y += 30
    text(out, x, y + 15, 'Output limit for one reply, for example 128,000 tokens [8]', 14, 'ink2', bold=True)
    y += 24
    rect(out, x, y, w, 34, 'win', rx=6)
    think_w = (w - 8) * 0.8
    rect(out, x + 3, y + 4, think_w, 26, 'k-think', rx=4)
    text(out, x + 12, y + 22, 'thinking', 13, 't-orange it')
    rect(out, x + 6 + think_w, y + 4, w - 12 - think_w, 26, 'k-orange', rx=4)
    text(out, x + 14 + think_w, y + 22, 'answer, cut', 13, 't-orange')
    path(out, f'M{x + w - 3},{y - 6} V{y + 40}', 'limit')
    y += 34 + 8
    text(out, x + w, y + 12, 'the reply stops here', 13, 't-red', anchor='end')
    y += 26
    y = para(out, x, y, w, 'The window limit covers everything in one request, what the model reads and what '
             'it writes. The output limit is smaller and covers one reply, thinking and answer together. [8]',
             15.5) + 6
    y = para(out, x, y, w, 'When a reply reaches the output limit, it stops in the middle. Long thinking can '
             'use up the whole limit before any answer appears. [4, 5]', 15.5) + 6
    return para(out, x, y, w, 'Input and reply share the window, so a nearly full window leaves less room '
                'for the reply. [5, 8]', 15.5)


def body_cost(out, x, y, w):
    y = para(out, x, y, w, 'Reading is fast because the model processes all the new input at once. Writing is '
             'slow because each token takes its own step. So you wait mostly for thinking and long answers.',
             15.5) + 12
    text(out, x, y + 15, 'Price for the example reply, in cents', 14, 'ink2', bold=True)
    y += 26
    parts = [('cached input', cents(CACHED, PRICE_CACHED), 'f-blue blk'),
             ('new input', cents(NEW, PRICE_IN), 'f-blue'),
             ('thinking', cents(THINK, PRICE_OUT), 'k-think'),
             ('answer', cents(ANSWER, PRICE_OUT), 'f-orange')]
    total = sum(p[1] for p in parts)
    without = cents(CACHED + NEW, PRICE_IN) + cents(THINK + ANSWER, PRICE_OUT)
    scale = (w - 4) / without
    bx = x
    for name, c, cls in parts:
        rect(out, bx, y, c * scale - 2, 26, cls, rx=3)
        bx += c * scale
    text(out, bx + 8, y + 18, f'{total:.1f} with the cache', 14, 'ink2', bold=True)
    y += 34
    rect(out, x, y, (cents(CACHED + NEW, PRICE_IN)) * scale - 2, 26, 'f-blue', rx=3)
    rect(out, x + cents(CACHED + NEW, PRICE_IN) * scale, y, cents(THINK + ANSWER, PRICE_OUT) * scale - 2, 26,
         'f-orange', rx=3)
    text(out, x + 8, y + 18, f'{without:.1f} without it', 14, 'on-dark', bold=True)
    y += 26 + 8
    lx = x
    for name, _, cls in parts:
        rect(out, lx, y + 2, 14, 14, cls, rx=3)
        text(out, lx + 20, y + 14, name, 13, 'muted')
        lx += 20 + text_width(name, 13) + 18
    y += 26
    y = para(out, x, y, w, f'Made-up prices per million tokens, in the range of real ones: input '
             f'${PRICE_IN:.2f}, cached input ${PRICE_CACHED:.2f}, output ${PRICE_OUT:.2f}.', 12.5, 'muted') + 8
    y = para(out, x, y, w, 'Providers charge per token. Output costs several times more than input, and cached '
             'input a fraction of input. [2, 3] Thinking is charged as output. [4, 5, 7]', 15.5) + 6
    y = para(out, x, y, w, 'Writing to the cache can cost a little extra the first time, for example 1.25 times '
             'the input price at Anthropic. [3]', 15.5) + 6
    return para(out, x, y, w, 'An agent sends the whole window again for every tool call, so over a session the '
                'cache cuts most of the cost of reading it. [3]', 15.5)


# ----------------------------------------------------------------- centre

def draw_centre(out, top, extra=0):
    anchors = {}
    x0, x1 = CX0 + 30, CX1 - 30
    text(out, CX0 + 24, top + 42, 'One reply, step by step', 27, bold=True)
    text(out, CX0 + 24, top + 70, 'Panels A to E show parts of it in more detail. The numbers are for one '
         'example reply.', 15.5, 'ink2')
    gap = 30 + extra / 6
    y = top + 104
    vx = x0 + 44  # visuals line up with the step titles

    # 1 read
    y = step_header(out, x0, y, 1, 'Read the window', 'The model gets the whole window, and processes only the '
                    'part that is not cached.', x1 - x0)
    seq = window_seq(2)
    bar_y = y + 30
    end = blocks(out, vx, bar_y, seq)
    brace(out, vx, end, bar_y - 6, '50,000 tokens in the window')
    cached_end = vx + (len(seq) - 2) * 15 - 3
    brace(out, vx, cached_end, bar_y + 26 + 6, '48,000 tokens read for the last request: cached', up=False)
    brace(out, cached_end + 3, end, bar_y + 26 + 6, '', up=False)
    text(out, end + 12, bar_y + 18, '2,000 new tokens: the latest tool result', 13, 'muted')
    y = para(out, vx, bar_y + 26 + 30, x1 - vx, 'Without the cache, all 50,000 tokens would be processed again '
             'on every request. [3] Most harnesses send the whole window each time, and some providers can keep '
             'it on their servers. [4, 5]', 15, 'ink2') + gap

    # 2 think
    y = step_header(out, x0, y, 2, 'Think', 'The model writes text for itself, one token at a time.', x1 - x0)
    th_y = y + 34
    rect(out, vx, th_y - 1, 150, 28, 'k-grey', rx=14)
    text(out, vx + 75, th_y + 18, 'effort: medium', 14, anchor='middle', bold=True)
    bx0 = vx + 300
    th_end = blocks(out, bx0, th_y, ['k-think'] * 30)
    arrow(out, [(vx + 162, th_y + 13), (bx0 - 16, th_y + 13)])
    text(out, (vx + 160 + bx0 - 14) / 2, th_y - 2, 'sets how long', 12.5, 'muted', anchor='middle')
    text(out, bx0, th_y - 16, 'users are logged out after a minute, so check the timeout units ...', 13.5,
         't-orange it')
    text(out, bx0, th_y + 26 + 26, '3,000 thinking tokens', 13, 'muted')
    anchors['A'] = zoom(out, vx - 7, th_y - 8, 164, 42, 'A', 'left')
    anchors['B'] = zoom(out, bx0 - 8, th_y - 8, th_end - bx0 + 16, 42, 'B', 'right')
    think_top = th_y - 4
    y = para(out, vx, th_y + 26 + 40, x1 - vx, 'You wait here: the thinking is written before any answer '
             'appears.', 15, 'ink2') + gap

    # 3 answer
    y = step_header(out, x0, y, 3, 'Answer', 'It writes the reply or a tool call, one token at a time.', x1 - x0)
    ans_y = y + 6
    tx = vx + 14
    for i, tok in enumerate(['The', ' timeout', ' was', ' in', ' seconds', ',', ' not', ' ms', '.']):
        tw = text_width(tok, 14, 'mono') + 14
        rect(out, tx, ans_y, tw, 28, 'gen' if i == 0 else 'k-orange', rx=5)
        text(out, tx + 7, ans_y + 19, tok, 14, 'mono on-dark' if i == 0 else 'mono t-orange')
        if i == 0:
            anchors['C'] = zoom(out, tx - 7, ans_y - 7, tw + 14, 42, 'C', 'left')
        tx += tw + 4
    text(out, vx, ans_y + 28 + 20, '500 answer tokens, shown to you as they are written', 13, 'muted')
    think_bottom = ans_y + 32
    lim_x = x1 - 14
    path(out, f'M{lim_x - 8},{think_top} H{lim_x} V{think_bottom} H{lim_x - 8}', 'bracket')
    text(out, lim_x - 16, ans_y + 28 + 20, 'Thinking and answer together count toward the output limit.', 13.5,
         'ink2', anchor='end')
    y = ans_y + 28 + 26 + gap

    # 4 stop
    y = step_header(out, x0, y, 4, 'Stop', 'The reply ends in one of three ways.', x1 - x0)
    bw = (x1 - vx - 40) / 3
    boxes = [('k-green', '**End of answer:** the harness shows the reply to you.'),
             ('k-purple', '**Tool call:** the harness runs it, adds the result and sends a new request.'),
             ('k-danger', '**Output limit reached:** the reply is cut off in the middle.')]
    bh = max(para([], 0, 0, bw - 28, m, 15) for _, m in boxes) + 20
    for i, (cls, m) in enumerate(boxes):
        bx = vx + i * (bw + 20)
        rect(out, bx, y + 4, bw, bh, cls, rx=10)
        para(out, bx + 14, y + 14, bw - 28, m, 15, 't-' + cls[2:])
    anchors['D'] = zoom(out, vx + 2 * (bw + 20) - 7, y - 3, bw + 14, bh + 14, 'D', 'right')
    y += bh + 4 + gap

    # 5 next request
    y = step_header(out, x0, y, 5, 'Next request', 'After a tool call, the whole window is read again, and only '
                    'the new part is processed.', x1 - x0)
    seq = window_seq(2) + ['f-orange blk', 'f-purple blk']
    bar_y = y + 10
    end = blocks(out, vx, bar_y, seq)
    cached_end = vx + (len(seq) - 2) * 15 - 3
    brace(out, vx, cached_end, bar_y + 26 + 6, 'cached: read for the last request', up=False)
    text(out, end + 12, bar_y + 18, 'new: the tool call and its result', 13, 'muted')
    y = para(out, vx, bar_y + 26 + 30, x1 - vx, 'In an agent this repeats for every tool call, often dozens '
             'of times in one task.', 15, 'ink2') + gap

    # receipt
    text(out, vx, y + 20, 'Receipt for the example reply', 18, bold=True)
    y += 34
    cols = [vx, vx + 230, vx + 360, vx + 450]
    total = sum(cents(t, p) for t, p in [(CACHED, PRICE_CACHED), (NEW, PRICE_IN), (THINK, PRICE_OUT),
                                         (ANSWER, PRICE_OUT)])
    rows = [('', 'tokens', 'time', 'price'),
            ('read, cached', f'{CACHED:,}', '', f'{cents(CACHED, PRICE_CACHED):.1f}¢'),
            ('read, new', f'{NEW:,}', '1 s', f'{cents(NEW, PRICE_IN):.1f}¢'),
            ('think', f'{THINK:,}', '30 s', f'{cents(THINK, PRICE_OUT):.1f}¢'),
            ('answer', f'{ANSWER:,}', '5 s', f'{cents(ANSWER, PRICE_OUT):.1f}¢'),
            ('total', f'{CACHED + NEW + THINK + ANSWER:,}', '36 s', f'{total:.1f}¢')]
    for i, row in enumerate(rows):
        ry = y + i * 28
        if i == len(rows) - 1:
            path(out, f'M{vx},{ry + 4} H{cols[3] + 70}', 'axis')
        for j, cell in enumerate(row):
            cx = cols[j] if j == 0 else cols[j] + (60 if j < 3 else 70)
            text(out, cx, ry + 22, cell, 15, 'muted' if i == 0 else '', anchor='start' if j == 0 else 'end',
                 bold=(i == len(rows) - 1))
    rec_bottom = y + len(rows) * 28 + 8
    anchors['E'] = zoom(out, vx - 10, y - 46, cols[3] + 70 - vx + 44, rec_bottom - y + 46, 'E', 'right')
    y = para(out, vx, rec_bottom + 10, x1 - vx, 'Times are illustrative and prices are made up. Thinking is the '
             'biggest part of this bill: the 3,000 thinking tokens cost three times as much as the 48,000 cached '
             'tokens of the window.', 15, 'ink2') + 20

    # key
    kx = vx
    for cls, label in [('f-blue blk', 'set-up text'), ('f-green blk', 'what you write'),
                       ('f-orange blk', 'what the model writes'), ('f-purple blk', 'tool output'),
                       ('k-think', 'thinking')]:
        rect(out, kx, y, 16, 16, cls, rx=3)
        text(out, kx + 24, y + 13, label, 14, 'ink2')
        kx += 24 + text_width(label, 14) + 26
    return anchors, y + 26


def main():
    left = [Panel(None, 'Words used here', body_words),
            Panel('A', 'Effort: how much to think', body_effort),
            Panel('C', 'Each token is picked by chance', body_probs)]
    right = [Panel('B', 'Thinking: notes before the answer', body_think),
             Panel('D', 'Two limits: the window and the reply', body_limits),
             Panel('E', 'What sets the wait and the price', body_cost)]
    build(GEO, OUT, 'Inside one reply',
          'What happens between sending the window and getting an answer: how each token is picked, what '
          'thinking is, and what sets the wait and the price.',
          'One reply of a language model, step by step: reading the window, thinking, answering and stopping, '
          'with panels on effort, thinking, token sampling, output limits, time and price.',
          left, right, draw_centre,
          'Sources, read in November 2026: ' + '; '.join(f'[{i}] {s}' for i, s in enumerate(SOURCES, start=1)) +
          '. Token counts, times and probabilities are illustrative, and prices are made up.')


if __name__ == '__main__':
    main()
