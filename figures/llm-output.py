#!/usr/bin/env python3
"""Draw an infographic on steering and judging text that a language model wrote.

Usage: python3 llm-output.py [output.svg]
"""

import sys
from pathlib import Path

from infographic import (Geometry, Panel, arrow, build, glossary, icon, mini_window, note, para,
                         path, rect, step_header, text, text_width, zoom)

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_suffix('.svg')
GEO = Geometry(2360)
CX0, CX1 = GEO.CX0, GEO.CX1

# Highlight colour for each problem in the example plan.
HIGHLIGHT = {'A': 'k-blue', 'B': 'k-danger', 'C': 'k-yellow', 'D': 'k-purple'}

# Numbered in the order a reader meets them.
SOURCES = [
    'Brzozowski and Chung, "The Ghost Couple: Correlated LLM Name Priors and Their Haunting of the Web and '
    'Academic Publishing" (2026, arxiv.org/abs/2606.02184)',
    'Hamilton and Mimno, "Elias in the Lighthouse, Again? Diagnosing Low Diversity in LLM Stories" (EMNLP 2026, '
    'arxiv.org/abs/2605.26492)',
    'Juzek and Ward, "Why Does ChatGPT \'Delve\' So Much? Exploring the Sources of Lexical Overrepresentation in '
    'Large Language Models" (COLING 2025, arxiv.org/abs/2412.11385)',
    'Kalai, Nachum, Vempala and Zhang, "Why Language Models Hallucinate" (2025, arxiv.org/abs/2509.04664)',
    'Anthropic, "Models overview" (platform.claude.com/docs/en/models/overview)',
    'Keon et al., "Galton\'s Law of Mediocrity: Why Large Language Models Regress to the Mean and Fail at '
    'Creativity in Advertising" (2025, arxiv.org/abs/2509.25767)',
    'Agarwal, Naaman and Vashistha, "AI Suggestions Homogenize Writing Toward Western Styles and Diminish Cultural '
    'Nuances" (CHI 2025, arxiv.org/abs/2409.11360)',
    'Zhang et al., "Verbalized Sampling: How to Mitigate Mode Collapse and Unlock LLM Diversity" (ICML 2026, '
    'arxiv.org/abs/2510.01171)',
    'Clark, Martin and Mahowald, "Why is AI-generated language so hard to understand?" (2026, '
    'arxiv.org/abs/2610.29162)',
    'Singhal, Goyal, Xu and Durrett, "A Long Way to Go: Investigating Length Correlations in RLHF" (COLM 2024, '
    'arxiv.org/abs/2310.03716)',
    'Claude Code docs, "Create custom subagents" (code.claude.com/docs/en/sub-agents)',
    'Panickssery, Bowman and Feng, "LLM Evaluators Recognize and Favor Their Own Generations" (2024, '
    'arxiv.org/abs/2404.13076)',
    'Sharma et al., "Towards Understanding Sycophancy in Language Models" (ICLR 2024, arxiv.org/abs/2310.13548)',
]


def heading(out, x, y, w, label, refs):
    """A small bold heading with its source numbers at the right. Returns the y below it."""
    text(out, x, y + 15, label, 14, 'ink2', bold=True)
    text(out, x + w, y + 15, refs, 14, anchor='end')
    return y + 26


def chip(out, x, y, label, cls, size=13.5):
    """One rounded label, top-left corner at x, y. Returns its width."""
    tw = text_width(label, size) + 20
    rect(out, x, y, tw, 26, cls, rx=13)
    text(out, x + tw / 2, y + 18, label, size, 't-' + cls.split('-')[1], anchor='middle')
    return tw


def chips(out, x, y, labels, cls, size=13.5, max_x=None):
    """A row of rounded labels, wrapping at max_x. Returns the y below the last row."""
    cx, row_y = x, y
    for label in labels:
        tw = text_width(label, size) + 20
        if max_x and cx + tw > max_x:
            cx, row_y = x, row_y + 32
        cx += chip(out, cx, row_y, label, cls, size) + 8
    return row_y + 26


def run(out, x, y, seg, size):
    """Draw one run of a line at x and return its width. Outer spaces become an offset, because a
    renderer drops leading whitespace in a text element."""
    lead = len(seg) - len(seg.lstrip(' '))
    if seg.strip():
        text(out, x + text_width(' ' * lead, size), y, seg.strip(), size)
    return text_width(seg, size)


def boxed(out, x, y, w, markup, cls, size=14, tcls=''):
    """A box around wrapped text. Returns the y below the box."""
    inner = []
    yb = para(inner, x + 12, y + 8, w - 24, markup, size, tcls)
    rect(out, x, y, w, yb - y + 8, cls, rx=8)
    out.extend(inner)
    return yb + 8


def why_and_tip(out, x, y, w, why, tip):
    """The training cause and the tip at the end of each panel, in the same style."""
    y = note(out, x, y, w, f'**Why:** {why}', 'note-grey') + 10
    return note(out, x, y, w, f'**Tip:** {tip}', 'note-grey')


# ----------------------------------------------------------------- panels

body_words = glossary('model', 'harness', 'session', 'training', 'ratings')


def body_names(out, x, y, w):
    y = heading(out, x, y, w, 'Stock names in some 2025 model versions', '[1]')
    for family, names in [('GPT', 'Elara Voss'), ('Claude', 'Elena Vasquez, Marcus Chen, Amara Okafor'),
                          ('Gemini', 'Aris Thorne, Lena Petrova')]:
        text(out, x, y + 17, family, 14.5, bold=True)
        text(out, x + 74, y + 17, names, 14.5, 't-blue')
        y += 26
    y = heading(out, x, y + 10, w, 'In 20,000 stories from four models', '[2]')
    rect(out, x, y, w, 24, 'win', rx=5)
    rect(out, x + 2, y + 2, (w - 4) * 0.883, 20, 'k-blue', rx=4)
    text(out, x + 10, y + 17, '88.3% contain at least one of 11 words, such as', 13.5, 't-blue', bold=True)
    y = chips(out, x, y + 32, ['Elias', 'Mara', 'Elara', 'lighthouse', 'clockmaker', 'librarian'], 'k-blue',
              max_x=x + w) + 14
    y = para(out, x, y, w, 'Ask for a story, an example or an expert, and models pick from a short list of names, '
             'places and jobs. [1, 2]', 15.5) + 6
    y = para(out, x, y, w, 'Each model version has its own names, and newer versions use them less, so the names '
             'also show roughly when a text was written. [1]', 15.5) + 6
    y = para(out, x, y, w, 'One study found 1,655 fake research records with real DOIs (permanent research '
             'identifiers). Their most frequent author, Elena Vasquez (77 records), is a Claude stock name. [1]',
             15.5) + 6
    y = para(out, x, y, w, 'Some words became far more common in scientific abstracts, likely because scientists '
             'used AI: "delve", "intricate" and "underscore". [3]', 15.5) + 12
    return why_and_tip(out, x, y, w,
                       'in OLMo, the only model in the study with public training data, these story words are '
                       'rare in books and web text. They are more frequent in the data of each later training '
                       'step, but still too rare to explain the result. [2] For words such as "delve", a '
                       'comparison of models fits training on human ratings, but a test with human raters did not '
                       'confirm it. [3]',
                       'give real names and details yourself. A stock name in a text is a sign that a model wrote '
                       'it, so check that the person exists.')


def body_wrong(out, x, y, w):
    y = heading(out, x, y, w, 'How often a fact is in the training text', '[4, 5]')
    tx, tw = x + 156, 140
    for label, share, cls, result, rcls in [('many times', 1.0, 'k-green', 'usually right', 't-green'),
                                            ('once', 0.07, 'k-yellow', 'often guessed', 't-yellow'),
                                            ('after the cutoff date', 0, '', 'guessed or out of date',
                                             't-danger')]:
        text(out, x, y + 17, label, 14)
        rect(out, tx, y + 1, tw, 24, 'win', rx=5)
        if share:
            rect(out, tx + 3, y + 4, (tw - 6) * share, 18, cls, rx=4)
        else:
            rect(out, tx + 3, y + 4, tw - 6, 18, 'slot-danger', rx=4)
        text(out, tx + tw + 12, y + 17, result, 14, rcls, bold=True)
        y += 31
    y = para(out, x, y + 8, w, 'A wrong answer reads as sure as a right one: an invented expert, a number with no '
             'source, a function that does not exist.', 15.5) + 6
    y = para(out, x, y, w, 'If 20% of birthdays appear only once in the training text, expect wrong answers to at '
             'least 20% of birthday questions. [4]', 15.5) + 6
    y = para(out, x, y, w, 'The training text stops at a cutoff date, for example June 2026 for current Claude '
             'models. Later events and software versions are not in it. [5]', 15.5) + 12
    return why_and_tip(out, x, y, w,
                       'a fact that appears only once in the training text is often not learned, and the model '
                       'writes a likely answer instead. Tests, and the training that uses them, score "I don\'t '
                       'know" like a wrong answer, so a guess scores better on average. [4]',
                       'give the model the sources and ask for quotes from them. Check every number, name and '
                       'quote yourself.')


def body_typical(out, x, y, w):
    steps = [('k-green', '**Original idea:** a heat-wave poster. A row of balconies, everyone outside except '
              'behind one closed curtain: "Knock on that door."', 'an image and a feeling'),
             ('k-grey', '**Shortened:** heat wave. Check on older neighbours.', 'only the facts are left'),
             ('k-orange', '**Written again:** stay safe this summer! Remember to check on elderly neighbours and '
              'stay hydrated in hot weather!', 'longer, more varied words, no idea')]
    bw = w - 150
    for i, (cls, m, side) in enumerate(steps):
        yb = boxed(out, x, y, bw, m, cls, 14, 't-' + cls[2:])
        para(out, x + bw + 14, y + 4, w - bw - 14, side, 13, 'muted')
        y = yb
        if i < 2:
            arrow(out, [(x + 30, y + 2), (x + 30, y + 20)])
            y += 22
    y = para(out, x, y + 4, w, 'The example is made up to show the finding.', 12.5, 'muted') + 10
    y = para(out, x, y, w, 'In a study on advertising, models shortened creative ideas step by step. The '
             'metaphors, emotion and images went first, and the plain facts stayed. [6]', 15.5) + 6
    y = para(out, x, y, w, 'Written again from the short version, the text got longer and used more varied words, '
             'but the original ideas did not come back. It looked new without being original. [6]', 15.5) + 6
    y = para(out, x, y, w, 'Giving the model a metaphor, an emotion or an image to use helped, but only in part. '
             '[6]', 15.5) + 6
    y = para(out, x, y, w, 'People who write with AI move toward the typical too. In a study with 118 writers from '
             'India and the US, AI suggestions moved the Indian writers toward Western writing styles. [7]',
             15.5) + 12
    return why_and_tip(out, x, y, w,
                       'people who rate answers tend to prefer familiar text. Training on human ratings therefore '
                       'makes typical answers more likely, while models before this step give more varied '
                       'answers. [8]',
                       'ask for five options together with how likely each one is, then look at the unlikely ones. '
                       'In one study this made stories, poems and jokes 1.6 to 2.1 times more varied. [8]')


def body_dense(out, x, y, w):
    fact = 'open the cooling rooms on heat-warning days.'
    long_text = ('Great question! Heat safety is an important topic, and there are many factors to consider. '
                 f'In short, {fact} I hope this helps!')
    short_text = fact[0].upper() + fact[1:]
    for label, body, cls in [(f'{len(long_text.split())} words', long_text, 'k-orange'),
                             (f'{len(short_text.split())} words, same content', short_text, 'k-green')]:
        text(out, x, y + 14, label, 13.5, 'ink2', bold=True)
        y = boxed(out, x, y + 22, w, body, cls, 14, 't-' + cls[2:]) + 10
    y = para(out, x, y + 2, w, 'Both happen at once: padding around the answer, and dense phrasing inside it.',
             15.5) + 10

    sentence = [('isolation-driven heat-risk clustering', 'k-teal'), (' ', None), ('outruns', 'k-orange'),
                (' our outreach', None)]
    rect(out, x, y, w, 92, 'code-bg', rx=8)
    tx = x + 14
    marks = []
    for seg, cls in sentence:
        sw = text_width(seg, 16)
        if cls:
            tx += 6
            rect(out, tx - 4, y + 12, sw + 8, 28, cls, rx=5)
            marks.append((tx, cls))
        tx += run(out, tx, y + 32, seg, 16) + (6 if cls else 0)
    if tx > x + w - 10:
        print('panel D sentence too wide', file=sys.stderr)
    labels = {'k-teal': 'stacked nouns', 'k-orange': 'a thing that acts like a living being'}
    for k, (mx, cls) in enumerate(marks):
        lx = min(mx - 3, x + w - 14 - text_width(labels[cls], 12.5, bold=True))
        text(out, lx, y + 60 + k * 20, labels[cls], 12.5, 't-' + cls[2:], bold=True)
    y = boxed(out, x, y + 100, w, '**Plainer:** people who live alone are most at risk, and our outreach does not '
              'reach them.', 'k-green', 14.5, 't-green') + 10

    y = para(out, x, y, w, 'A 2026 study compared nine leading models with human writing. All nine used more '
             'rare word sequences, and more often made a thing act like a living being, as in "is_file() swallows '
             'that". '
             'Most also used more stacked nouns. Each of these makes the reader hold more in mind, or read the '
             'sentence again. [9]', 15.5) + 6
    y = para(out, x, y, w, 'Claude Opus 5.5 used these features less than Claude Opus 5 in 19 of 21 comparisons, '
             'clearly in 8. [9]', 15.5) + 6
    y = para(out, x, y, w, 'A long answer looks thorough, but length is not a measure of quality.', 15.5) + 12
    return why_and_tip(out, x, y, w,
                       'in training on human ratings, the scoring models give longer answers higher scores. [10] '
                       'In training on math and code problems, there is pressure for short solutions. One study '
                       'suggests that this makes text dense: in its small test, a penalty for long answers made a '
                       'model\'s phrasing less like human phrasing. [9]',
                       'ask for a short answer in plain words for the people who will read it, then edit it '
                       'yourself.')


def body_fresh(out, x, y, w):
    half = (w - 20) / 2
    text(out, x, y + 15, 'Give the reviewer', 14, 't-green', bold=True)
    text(out, x + half + 20, y + 15, 'Leave out', 14, 't-danger', bold=True)
    y += 24
    for i, (give, leave) in enumerate([('the task', "the writer's reasoning"), ('the output', "the writer's claims"),
                                       ('a way to check it', 'your opinion')]):
        ry = y + i * 32
        rect(out, x, ry, half, 26, 'k-green', rx=13)
        text(out, x + 14, ry + 18, give, 13.5, 't-green')
        rect(out, x + half + 20, ry, half, 26, 'k-danger', rx=13)
        text(out, x + half + 34, ry + 18, leave, 13.5, 't-danger')
    y += 3 * 32 + 10
    y = para(out, x, y, w, 'A reviewer in the same session reads the writer\'s plan, reasoning and claims, such as '
             '"the plan is complete and evidence-based", and starts from them.', 15.5) + 6
    y = para(out, x, y, w, 'Some harnesses start a subagent with only the task and the output, and it works like '
             'a fresh session. A fork starts with a copy of the conversation, so it does not. [11]', 15.5) + 6
    y = para(out, x, y, w, 'Models score their own text higher, and the better a model recognises its own text, '
             'the larger this bias. A fresh session of the same model still has it. [12]', 15.5) + 6
    y = para(out, x, y, w, 'Models also tend to agree with the person asking. This is called **sycophancy**. [13]',
             15.5) + 12
    return why_and_tip(out, x, y, w,
                       'people rate answers that agree with them higher, so training on human ratings rewards '
                       'agreeing. [13]',
                       'review in a fresh session, with another model or a person [12], and keep your opinion out '
                       'of the request.')


# ----------------------------------------------------------------- centre

PLAN = [
    [('According to ', None), ('Dr. Elara Voss', 'A'), (', a heat-safety expert, every town must act now.', None)],
    [('Cooling rooms cut heat deaths by 80%, studies show.', 'B')],
    [('The town should ', None), ('raise awareness, plant more trees and launch an app', 'C'), ('.', None)],
    [('Meanwhile, ', None), ('isolation-driven heat-risk clustering outruns our outreach', 'D'), ('.', None)],
    [('In conclusion, protecting residents from heat matters because everyone deserves to be safe.', 'D')],
]
LINE = 44


def steer_tag(out, x1, y):
    """A green 'you steer' label at the right end of a step header."""
    label = 'you steer here'
    tw = text_width(label, 13.5, bold=True) + 44
    rect(out, x1 - tw, y + 4, tw, 26, 'k-green', rx=13)
    icon(out, 'person', x1 - tw + 8, y + 5)
    text(out, x1 - tw + 34, y + 22, label, 13.5, 't-green', bold=True)


def check(out, x, y):
    """A green tick, 14 px wide, top-left corner at x, y."""
    out.append(f'<path d="M{x:.1f},{y + 7:.1f} l5,6 l9,-12" class="ar ar-green" style="stroke-width:2.6"/>')


def card_text(out, x, y, w):
    """Card 1: the next word, by how often it followed in the text."""
    rect(out, x, y, w, 30, 'code-bg', rx=6)
    text(out, x + 10, y + 20, 'Heat waves are most dangerous for ...', 13.5, 'ink2')
    y += 38
    for label, share in [('older people', 0.8), ('children', 0.32), ('pets', 0.08)]:
        text(out, x, y + 14, label, 13)
        rect(out, x + 96, y + 2, (w - 96) * share, 16, 'k-blue', rx=4)
        y += 22
    return para(out, x, y + 2, w, 'The longer the bar, the more often that word came next in the text.', 13, 'muted')


def card_ratings(out, x, y, w):
    """Card 2: a rater picks one of two answers."""
    for label, cls, picked in [('"Great question! ... I hope this helps!"', 'k-orange', True),
                               ('"Open the cooling rooms."', 'k-grey', False)]:
        rect(out, x, y, w - 76, 28, cls, rx=6)
        text(out, x + 10, y + 19, label, 13, 't-' + cls[2:])
        if picked:
            check(out, x + w - 66, y + 7)
            text(out, x + w - 46, y + 19, 'picked', 13, 't-green', bold=True)
        y += 34
    return para(out, x, y, w, 'The model learns to write more like the picked answer.', 13, 'muted')


def card_scores(out, x, y, w):
    """Card 3: how a test with right or wrong answers scores."""
    for label, cls in [('right answer: 1 point', 'k-green'), ('wrong answer: 0 points', 'k-danger'),
                       ('"I don\'t know": 0 points', 'k-grey')]:
        chip(out, x, y, label, cls, 13)
        y += 31
    return y - 5


def draw_centre(out, top, extra=0):
    anchors = {}
    x0, x1 = CX0 + 30, CX1 - 30
    vx = x0 + 44
    text(out, CX0 + 24, top + 42, 'One realistic problem, from question to decision', 27, bold=True)
    text(out, CX0 + 24, top + 70, 'Panels A to E show parts of it in more detail. The town and its numbers are made '
         'up.', 15.5, 'ink2')
    gap = 30 + extra / 5
    y = top + 104

    # 1 ask
    steer_tag(out, x1, y)
    y = step_header(out, x0, y, 1, 'Ask', 'You describe the problem with the facts you know.', x1 - x0 - 170)
    steps = [('k-green', '**You:** 14 people in our town died in last summer\'s heat wave, most of them over 75 '
              'and living alone. What can we do before next summer?', 't-green'),
             ('k-think', '(thinking) heat plans, cooling rooms, awareness campaigns ...', 't-orange it'),
             ('k-orange', '**Model:** writes the plan below.', 't-orange'),
             ('k-orange', '**Model:** "Done. The plan is complete and evidence-based."', 't-orange')]
    widths = [0.34, 0.22, 0.18, 0.26]
    total = x1 - vx - 3 * 30
    bh = max(para([], 0, 0, total * f - 24, m, 14) for (_, m, _), f in zip(steps, widths)) + 16
    bx = vx
    for i, ((cls, m, tcls), f) in enumerate(zip(steps, widths)):
        bw = total * f
        rect(out, bx, y, bw, bh, cls, rx=8)
        para(out, bx + 12, y + 8, bw - 24, m, 14, tcls)
        if i < 3:
            arrow(out, [(bx + bw + 3, y + bh / 2), (bx + bw + 27, y + bh / 2)])
        bx += bw + 30
    y += bh + gap

    # 2 the output
    y = step_header(out, x0, y, 2, 'The output', 'A plan of five sentences, with a common problem in each.', x1 - x0)
    oh = 24 + len(PLAN) * LINE
    rect(out, vx, y, x1 - vx, oh, 'win', rx=10)
    rows = {}
    for i, line in enumerate(PLAN):
        ly = y + 22 + i * LINE
        tx = vx + 24
        for seg, cat in line:
            sw = text_width(seg, 16.5)
            if cat:
                tx += 6
                rect(out, tx - 4, ly - 4, sw + 8, 32, HIGHLIGHT[cat], rx=6)
                rows.setdefault(cat, []).append(ly + 12)
            # each run sits at its measured position, so a narrower font cannot shift a highlight
            tx += run(out, tx, ly + 18, seg, 16.5) + (6 if cat else 0)
        if tx > x1 - 20:
            print(f'plan line {i + 1} too wide', file=sys.stderr)
    for cat, ys in rows.items():
        cy = (ys[0] + ys[-1]) / 2
        if len(ys) > 1:
            path(out, f'M{x1 - 16:.1f},{ys[0] - 14:.1f} H{x1 - 8:.1f} V{ys[-1] + 14:.1f} H{x1 - 16:.1f}', 'bracket')
        anchors[cat] = (vx - 18, cy) if cat in 'AC' else (x1 + 16, cy)
    y += oh + gap

    # 3 review
    steer_tag(out, x1, y)
    y = step_header(out, x0, y, 3, 'Review', 'The same output and the same request, in two sessions.',
                    x1 - x0 - 170)
    lw = (x1 - vx - 40) / 2
    request = 'you: review this plan for the town council'
    same = {0: ('blue', 'set-up'), 1: ('green', 'you: what can we do before next summer?'), 2: ('orange', 'the plan'),
            3: ('orange', '"Done. The plan is complete and evidence-based."'), 4: ('green', request),
            5: ('orange', '"Looks good: complete and evidence-based."')}
    fresh = {0: ('blue', 'set-up'), 1: ('green', request), 2: ('purple', 'the plan, and nothing else'),
             3: (None, 'no reasoning and no claims'), 4: (None, 'from the writer'),
             5: ('orange', '"Five problems, from the invented expert to the padding."')}
    yb1, _ = mini_window(out, vx, y, lw, same, 'In the same session', rh=24, rs=30)
    fx = vx + lw + 40
    yb2, _ = mini_window(out, fx, y, lw, fresh, 'In a fresh session', rh=24, rs=30)
    vy = max(yb1, yb2) + 8
    va = para(out, vx, vy, lw, 'Starts from the writer\'s own claims, and here it misses all five problems.', 14.5,
              't-danger')
    vb = para(out, fx, vy, lw, 'Gets only what a council member gets, and here it finds all five.', 14.5, 't-green')
    anchors['E'] = zoom(out, fx - 8, y - 6, lw + 16, vb - y + 14, 'E', 'right')
    y = para(out, vx, max(va, vb) + 10, x1 - vx, 'Both results are made up to show the difference.', 13, 'muted')
    y += gap

    # 4 ask again
    steer_tag(out, x1, y)
    y = step_header(out, x0, y, 4, 'Ask again', 'You send back what the review found, with the tips from panels B, '
                    'C and D.', x1 - x0 - 170)
    ideas = [('an awareness campaign', 0.35), ('plant more trees', 0.25), ('a heat-warning app', 0.20),
             ('volunteers phone people over 75', 0.12), ('free buses to cooling rooms', 0.08)]
    yw = 0.4 * (x1 - vx - 30)
    you = ('**You:** Leave out the expert and the 80%, unless you can quote a source. Give five ideas, with how '
           'likely each one is. Write in plain words for the council.')
    ybox = para([], 0, 0, yw - 24, you, 14) + 16
    mx = vx + yw + 30
    mw = x1 - mx
    mh = 38 + len(ideas) * 26 + 6
    rect(out, vx, y, yw, ybox, 'k-green', rx=8)
    para(out, vx + 12, y + 8, yw - 24, you, 14, 't-green')
    arrow(out, [(vx + yw + 3, y + 30), (mx - 3, y + 30)])
    rect(out, mx, y, mw, mh, 'k-orange', rx=8)
    text(out, mx + 12, y + 24, '**Model:** five ideas, each with how likely it is', 14, 't-orange')
    for i, (idea, p) in enumerate(ideas):
        ry = y + 36 + i * 26
        tail = i >= 3
        if tail:
            rect(out, mx + 8, ry, mw - 16, 24, 'k-green', rx=5)
        text(out, mx + 18, ry + 17, idea, 13.5, 't-green' if tail else 't-orange', bold=tail)
        text(out, mx + 300, ry + 17, f'{p:.2f}', 13.5, 't-green' if tail else 't-orange', extra='')
        if tail:
            text(out, x1 - 18, ry + 17, 'you keep it', 13, 't-green', anchor='end', bold=True)
    y += max(ybox, mh) + 8
    y = para(out, vx, y, x1 - vx, 'The two unlikely ideas reach the people who live alone, so you keep them.', 14,
             'ink2') + gap

    # 5 decide
    steer_tag(out, x1, y)
    y = step_header(out, x0, y, 5, 'Decide', 'Add facts that are not in the training text or the conversation, '
                    'check every claim, and choose.', x1 - x0 - 170)
    edited = ["Most of last summer's deaths were people over 75 who lived alone, many in top-floor flats.",
              'Volunteers will phone every registered resident over 75 on heat-warning days, and visit anyone who '
              'does not answer.',
              'The library and two schools will open as cooling rooms until 9 pm, with free buses from the tower '
              'blocks.']
    inner = []
    ey = y + 14
    for line in edited:
        ey = para(inner, vx + 54, ey, x1 - vx - 74, line, 16, 't-green') + 6
    ey = para(inner, vx + 54, ey + 2, x1 - vx - 74, 'You add who died and where they lived, and which buildings can '
              'open. Residents and the care service review the plan before the council votes.', 14, 'muted') + 12
    rect(out, vx, y, x1 - vx, ey - y, 'k-green', rx=10)
    icon(out, 'person', vx + 16, y + 16)
    out.extend(inner)
    y = ey + gap

    # where the habits come from
    head = 'Where these habits come from'
    text(out, x0, y + 20, head, 20, bold=True)
    text(out, x0 + text_width(head, 20, bold=True) + 14, y + 20, 'Simplified: three kinds of training, and the '
         'habits linked to each one.', 15.5, 'ink2')
    y += 36
    cards = [
        ('Learning from a huge amount of text', 'The model learns which words usually follow which, from text '
         'collected up to a cutoff date.', card_text,
         ['Facts seen only once, and events after the cutoff, get guessed. **B** [4, 5]']),
        ('Training on human ratings', 'People, or models trained on their choices, score answers.', card_ratings,
         ['Familiar text scores well: stock names, typical ideas. **A, C** [2, 8]',
          'Agreeing and longer answers score well. **D, E** [10, 13]']),
        ('Training and tests with checkable answers', 'Math, code and quiz questions, where a program marks each '
         'answer right or wrong.', card_scores,
         ['A guess scores better than "I don\'t know". **B** [4]',
          'Short solutions win, and text may get dense. **D** [9]']),
    ]
    cw = (x1 - x0 - 2 * 24) / 3
    pad = 14
    # rows line up across the cards: heads, then pictures, then effects
    heads = [para([], 0, 0, cw - 2 * pad, t, 15.5, bold=True) + para([], 0, 0, cw - 2 * pad, d, 14) for t, d, _, _ in
             cards]
    pic_y = y + 10 + max(heads) + 10
    pics = [draw([], 0, 0, cw - 2 * pad) for _, _, draw, _ in cards]
    eff_y = pic_y + max(pics) + 14
    inners, bottoms = [], []
    for k, (title, desc, draw, effects) in enumerate(cards):
        cx = x0 + k * (cw + 24)
        inner = []
        cy = para(inner, cx + pad, y + 10, cw - 2 * pad, title, 15.5, bold=True)
        para(inner, cx + pad, cy, cw - 2 * pad, desc, 14, 'ink2')
        draw(inner, cx + pad, pic_y, cw - 2 * pad)
        cy = eff_y
        for effect in effects:
            arrow(inner, [(cx + 16, cy + 11), (cx + 34, cy + 11)])
            cy = para(inner, cx + 42, cy, cw - 56, effect, 14) + 4
        inners.append(inner)
        bottoms.append(cy + 8)
    card_h = max(bottoms) - y
    for k, inner in enumerate(inners):
        rect(out, x0 + k * (cw + 24), y, cw, card_h, 'k-blue' if k == 1 else 'note-grey', rx=10)
        out.extend(inner)
    return anchors, y + card_h + 10


def main():
    left = [Panel(None, 'Words used here', body_words),
            Panel('A', 'The same few names and words', body_names),
            Panel('C', 'Pulled toward the typical', body_typical)]
    right = [Panel('B', 'Confident and wrong', body_wrong),
             Panel('D', 'Dense inside, padded outside', body_dense),
             Panel('E', 'Review in a fresh session', body_fresh)]
    build(GEO, OUT, 'Steering and judging AI output',
          'AI text tends to sound alike, state guesses as facts, lose what made an idea distinctive and pack too '
          'much into each sentence. These habits are linked to how models are trained. Steer with what you know, '
          'and review in a fresh session.',
          'How text written by a language model reads, why, and how to steer and judge it: stock names and words, '
          'confident wrong answers, typical ideas, dense and padded text, and review in a fresh session.',
          left, right, draw_centre,
          'Sources, read in November 2026: ' + '; '.join(f'[{i}] {s}' for i, s in enumerate(SOURCES, start=1)) +
          '. The town, its numbers and the example texts are made up.')


if __name__ == '__main__':
    main()
