#!/usr/bin/env python3
"""Draw an infographic on how an AI agent builds and uses its context window.

Usage: python3 llm-context.py [output.svg]
"""

import sys
from pathlib import Path

from infographic import (Geometry, Panel, arrow, build, glossary, icon, markup_width,
                         mini_window, note, numbered, para, path, rect, text, tier, zoom)

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_suffix('.svg')
GEO = Geometry(2360)
CX0, CX1 = GEO.CX0, GEO.CX1

# Numbered in the order a reader meets them.
SOURCES = [
    'OpenAI, "Key concepts", tokens (developers.openai.com/api/docs/concepts)',
    'Anthropic, "Pricing", tokenizer note (platform.claude.com/docs/en/about-claude/pricing)',
    'Claude Code docs, "Explore the context window" (code.claude.com/docs/en/context-window)',
    'Claude Code docs, "How Claude remembers your project" (code.claude.com/docs/en/memory)',
    'Anthropic, "Agent Skills" (platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)',
    'Anthropic, "Effort" (platform.claude.com/docs/en/build-with-claude/effort)',
    'Anthropic, "Prompt caching" (platform.claude.com/docs/en/build-with-claude/prompt-caching)',
    'OpenAI, "Reasoning models" (developers.openai.com/api/docs/guides/reasoning)',
    'Google, "Gemini thinking" (ai.google.dev/gemini-api/docs/thinking)',
    'Anthropic, "Tool use" (platform.claude.com/docs/en/agents-and-tools/tool-use/overview)',
    'Model Context Protocol specification, "Tools" (modelcontextprotocol.io/specification)',
    'Claude Code docs, "Connect Claude Code to tools via MCP" (code.claude.com/docs/en/mcp)',
    'Claude Code docs, "Create custom subagents" (code.claude.com/docs/en/sub-agents)',
    'Claude Code docs, "Orchestrate teams of Claude Code sessions" (code.claude.com/docs/en/agent-teams)',
    'Anthropic, "Effective context engineering for AI agents" (2025, anthropic.com/engineering)',
    'Chroma, "Context Rot" (2025, research.trychroma.com/context-rot)',
    'Liu et al., "Lost in the Middle" (TACL 2024, arxiv.org/abs/2307.03172)',
]

body_words = glossary('model', 'harness', 'agent', 'provider', 'token', 'window', 'session', 'skill', 'mcp',
                      'training', extra={'token': ' [1, 2]'})


def body_model(out, x, y, w):
    base = ['blue'] * 4 + ['green'] + ['orange', 'purple'] * 3
    outputs = ['"Fix"', '"ed"', '" the"']
    bx = x + 62
    unit = 13.5
    text(out, bx, y + 12, 'all the tokens so far', 12.5, 'muted')
    path(out, f'M{bx},{y+20} v-4 h{len(base) * unit - 2.5} v4', 'ic-line')
    y += 24
    mx = bx + (len(base) + 2) * unit + 30
    for i in range(3):
        ry = y + i * 40
        text(out, x, ry + 20, f'step {i + 1}', 13, 'muted')
        seq = base + ['gen'] * i
        for j, c in enumerate(seq):
            cls = 'gen' if c == 'gen' else f'f-{c} blk'
            rect(out, bx + j * unit, ry + 4, 11, 22, cls, rx=2.5)
        arrow(out, [(bx + len(seq) * unit + 4, ry + 15), (mx - 4, ry + 15)])
        rect(out, mx, ry + 2, 66, 26, 'dark', rx=13)
        text(out, mx + 33, ry + 20, 'Model', 13.5, 'on-dark', anchor='middle', bold=True)
        arrow(out, [(mx + 70, ry + 15), (mx + 92, ry + 15)])
        rect(out, mx + 96, ry + 2, x + w - mx - 96, 26, 'k-orange', rx=6)
        text(out, mx + 106, ry + 20, outputs[i], 14, 'mono t-orange')
    y += 3 * 40 + 2
    y = para(out, x, y, w, 'and so on, one step per token, until the reply or a tool call is done.',
             13.5, 'muted') + 10
    y = para(out, x, y, w, 'To pick each next token, the model uses all the tokens before it: the set-up '
             'text, the conversation, the tool output and its own new words. It keeps its work on earlier '
             'tokens, so it does not process them again during the reply.', 15.5) + 6
    y = para(out, x, y, w, 'The model keeps no state between requests: for every reply it reads the whole window '
             'again. Most harnesses send the whole window each time, and some providers can keep it on their '
             'servers. [8, 9]', 15.5) + 12
    return note(out, x, y, w, '[Part 2](llm-reply.svg) shows thinking, effort, caching and price '
                'in detail.', 'note-grey')


def body_tool(out, x, y, w):
    y = para(out, x, y, w, 'The model cannot run anything itself. It writes a tool call, in the format that the '
             'tool list describes:', 15.5) + 8
    lines = ['I will follow the debug skill first.', '<call tool="Read" path="skills/debug/SKILL.md"/>']
    rect(out, x, y, w, 96, 'code-bg', rx=8)
    text(out, x + 14, y + 20, 'model output (format simplified)', 12.5, 'muted')
    rect(out, x + 6, y + 60, w - 12, 26, 'hl', rx=5)
    text(out, x + 14, y + 48, lines[0], 14, 'mono ink2')
    text(out, x + 14, y + 78, lines[1], 14, 'mono t-orange', bold=True)
    y += 96 + 12
    y = numbered(out, x, y, w, [
        "**Find:** the provider's software finds the call in the output, much like grep, ends the reply there "
        'and sends the call to the harness as data. [10]',
        '**Run:** the harness runs the matching program, here a file read. It can ask you for permission '
        'first.',
        "**Add:** the harness adds the program's output to the window as text: the tool result.",
        '**Repeat:** the harness sends the longer window, and the model continues.',
    ]) + 6
    y = para(out, x, y, w, 'Some tools, such as web search, run at the provider instead, and the provider adds '
             'their results to the window. [10]', 15.5) + 10
    return note(out, x, y, w, 'A skill loads the same way: the model reads its SKILL.md file with a tool call. [5]',
                'note-purple')


def body_mcp(out, x, y, w):
    cw, ch = 118, 146
    rect(out, x, y, cw, ch, 'k-grey', rx=10)
    text(out, x + cw / 2, y + ch / 2 - 2, 'Harness', 17, anchor='middle', bold=True)
    text(out, x + cw / 2, y + ch / 2 + 18, 'on your computer', 12, 'muted', anchor='middle')
    servers = [('GitHub server', 'get_issue'), ('Database server', 'run_query'), ('Browser server', 'open_page')]
    sx = x + cw + 64
    sw = x + w - sx
    for i, (name, tool) in enumerate(servers):
        sy = y + 6 + i * 50
        rect(out, sx, sy, sw, 38, 'k-yellow', rx=8)
        icon(out, 'plug', sx + 8, sy + 7)
        text(out, sx + 40, sy + 24, name, 14.5, 't-yellow', bold=True)
        text(out, sx + sw - 10, sy + 24, tool, 12.5, 'mono t-yellow', anchor='end')
        arrow(out, [(x + cw + 4, sy + 19), (sx - 4, sy + 19)], 'yellow', both=True)
    y += ch + 16
    y = numbered(out, x, y, w, [
        'At the start, the harness asks each MCP server for its list of tools. [11]',
        'It adds each tool to the tool list in the window, with its description. Claude Code adds only the '
        'names, and adds a description when the model searches for that tool. [12]',
        'When the model calls one, the harness passes the call to that server and adds the answer to the '
        'window. [11]',
    ]) + 6
    return para(out, x, y, w, '**MCP** (Model Context Protocol) is a standard plug, so any harness can use any '
                'MCP server. To the model, an MCP tool is one more tool in the list.', 15.5)


def body_sub(out, x, y, w):
    mw, sw = 158, 206
    sx = x + w - sw
    yb1, mc = mini_window(out, x, y, mw, {
        0: ('blue', 'set-up'), 1: ('green', 'you: fix the bug'), 2: ('orange', '`Agent(task)`'),
        4: (None, 'no file reads here'), 7: ('teal', 'summary')}, 'your window')
    yb2, sc = mini_window(out, sx, y, sw, {
        0: ('blue', 'own set-up'), 1: ('green', 'task text only'), 2: ('orange', '`Read(a.ts)`'),
        3: ('purple', 'a.ts: 900 lines'), 4: ('orange', '`Read(b.ts)`'), 5: ('purple', 'b.ts: 700 lines'),
        6: (None, '...'), 7: ('orange', 'summary')}, "subagent's window")
    arrow(out, [(x + mw - 2, mc[2]), (sx + 2, sc[1])], 'orange')
    text(out, (x + mw + sx) / 2, (mc[2] + sc[1]) / 2 - 8, 'task', 12.5, 't-orange', anchor='middle', bold=True)
    arrow(out, [(sx + 2, sc[7]), (x + mw - 2, mc[7])], 'teal')
    text(out, (x + mw + sx) / 2, sc[7] - 8, 'summary', 12.5, 't-teal', anchor='middle', bold=True)
    y = max(yb1, yb2) + 14
    y = para(out, x, y, w, 'A subagent is a second conversation that the harness runs, with its own window and '
             'the same model or another one. A standard subagent gets only the task text, so the task must '
             'contain all the details. A fork gets a copy of your conversation. [13]', 15.5) + 6
    y = para(out, x, y, w, 'The file reads stay in the subagent\'s window, and only its summary is added to yours. '
             '[3, 13]', 15.5) + 10
    y = note(out, x, y, w, '**Why use one?** A big search can fill a window with file text. In a subagent, that '
             "text stays out of your window, so yours stays short. The reads still cost tokens. [13]",
             'note-purple') + 16
    aw = (w - 70) / 2
    ya, ac = mini_window(out, x, y, aw, {0: ('blue', 'set-up'), 1: ('orange', '`send(B, "tests pass")`')},
                         'agent A')
    yb, bc = mini_window(out, x + w - aw, y, aw, {0: ('blue', 'set-up'), 1: ('teal', 'from A: tests pass')},
                         'agent B')
    arrow(out, [(x + aw - 2, ac[1]), (x + w - aw + 2, bc[1])], 'teal')
    y = max(ya, yb) + 12
    return para(out, x, y, w, 'Agents in a team exchange messages the same way: the harness adds each message as '
                "new text to the other agent's window. Agents can also share a task list in a file on disk. In Claude "
                'Code, agent teams are experimental and off by default. [14]', 15.5)


def body_recall(out, x, y, w):
    cw, ch = w - 20, 110
    text(out, x, y + 13, 'Details used correctly, by amount of text', 13.5, 'ink2', bold=True)
    cy = y + 26
    ox = x + 6
    path(out, f'M{ox},{cy} V{cy+ch} H{x+cw}', 'axis')
    curve = (f'M{ox+2},{cy+ch*0.1:.1f} C{ox+cw*0.35:.1f},{cy+ch*0.12:.1f} {ox+cw*0.62:.1f},{cy+ch*0.3:.1f} '
             f'{x+cw-6},{cy+ch*0.62:.1f}')
    path(out, curve + f' V{cy+ch} H{ox+2} Z', 'area')
    path(out, curve, 'curve')
    text(out, ox + 8, cy + ch + 18, 'little text', 12.5, 'muted')
    text(out, x + cw, cy + ch + 18, 'full window', 12.5, 'muted', anchor='end')
    y = cy + ch + 26
    y = para(out, x, y, w, 'The curve is illustrative, not measured data.', 12.5, 'muted') + 8
    y = para(out, x, y, w, "All tokens share the model's attention. The fuller the window, the more often a "
             'detail is missed or mixed up. [15, 16] Models from 2023 also missed more in the middle of a long '
             'window than at its start or end. [17]', 15.5) + 6
    y = para(out, x, y, w, 'So agents load text only when needed and give big searches to subagents. A new '
             'task is better done in a new session.', 15.5) + 12
    y = note(out, x, y, w, '**Compaction.** When the window is almost full, the harness replaces the old '
             'conversation with a short summary. Details that are not in the summary are lost. [3]', 'note-grey')
    y += 16
    text(out, x, y + 14, 'What carries over to the next session', 13.5, 'ink2', bold=True)
    y += 24
    half = (w - 30) / 2
    for k, (label, rows) in enumerate([
        ('this session', [('k-orange', 'the conversation'), ('k-green', 'files: code, AGENTS.md, memory')]),
        ('next session', [(None, 'empty conversation'), ('k-green', 'files: code, AGENTS.md, memory')]),
    ]):
        bx = x + k * (half + 30)
        text(out, bx, y + 12, label, 12.5, 'muted', bold=True)
        for j, (cls, row) in enumerate(rows):
            ry = y + 20 + j * 30
            if cls:
                rect(out, bx, ry, half, 24, cls, rx=5)
                text(out, bx + 10, ry + 17, row, 13, 't-' + cls[2:])
            else:
                rect(out, bx, ry, half, 24, 'slot', rx=5)
                text(out, bx + 10, ry + 17, row, 13, 'muted')
    arrow(out, [(x + half + 4, y + 20 + 30 + 12), (x + half + 26, y + 20 + 30 + 12)], 'green')
    y += 20 + 2 * 30 + 6
    return para(out, x, y, w, 'Only files carry over, so to keep a lesson for later sessions, write it in a '
                'file that the harness loads. [4]', 15.5)


# ----------------------------------------------------------------- centre

# (key, kind, role label, text)
ROWS = [
    ('system', 'always', None, "Harness's own instructions (system prompt)"),
    ('agents', 'always', None, "AGENTS.md: your project's rules, full text"),
    ('memory', 'always', None, 'Memory index: one line per saved note'),
    ('skills', 'always', None, 'Skill list: a name and a description per skill'),
    ('tools', 'always', None, 'Tool list: Read, Edit, Bash, Agent, MCP tools'),
    ('task', 'you', 'YOU', 'Fix the logout bug from issue 123'),
    ('think', 'think', 'MODEL', '(thinking) users are logged out after a minute'),
    ('skill-call', 'model', 'MODEL', '`Read("skills/debug/SKILL.md")`'),
    ('skill', 'tool', 'TOOL', 'The debug skill: steps to follow'),
    ('mcp-call', 'model', 'MODEL', '`get_issue(123)`'),
    ('mcp', 'tool', 'TOOL', 'Issue 123: users are logged out after a minute'),
    ('note-call', 'model', 'MODEL', '`Read("memory/ci-notes.md")`'),
    ('note', 'tool', 'TOOL', 'Note: test_session fails at random on CI'),
    ('agent-call', 'model', 'MODEL', '`Agent("find all callers of logout()")`'),
    ('summary', 'sub', 'TOOL', 'Summary: 3 callers, in a.ts, b.ts and c.ts'),
    ('edit-call', 'model', 'MODEL', '`Edit("src/session.ts", ...)`'),
    ('edit', 'tool', 'TOOL', 'Done: src/session.ts changed'),
    ('answer', 'model', 'MODEL', 'Fixed: the timeout is now read in milliseconds.'),
]
KIND = {'always': ('blue', 1), 'you': ('green', None), 'think': ('orange', None), 'model': ('orange', None),
        'tool': ('purple', 2), 'sub': ('teal', 3)}

# (row key, icon, name, note, arrow label, colour, row key the arrow starts from when it points to the item)
ITEMS = [
    ('agents', 'file', '`AGENTS.md`', "your project's rules", 'full text', 'blue', None),
    ('memory', 'file', '`MEMORY.md`', "the agent's own notes", 'index', 'blue', None),
    ('skills', 'folder', '`skills/`', 'one folder per skill', 'descriptions', 'blue', None),
    ('tools', 'term', 'Tool programs', 'built in, or MCP servers', 'how to call them', 'blue', None),
    ('skill', 'file', '`debug/SKILL.md`', "a skill's full text", 'full text', 'purple', None),
    ('mcp', 'plug', 'MCP server', 'runs `get_issue`', 'its answer', 'purple', None),
    ('note', 'file', '`memory/ci-notes.md`', 'one saved note', 'full text', 'purple', None),
    ('summary', 'window', 'Subagent', 'works in its own window', 'summary only', 'teal', None),
    ('edit', 'file', '`src/session.ts`', 'your code', 'changes it', 'orange', 'edit-call'),
]

STEP1, H1 = 54, 44  # rows sent first
STEP2, H2 = 48, 38  # conversation rows


def draw_centre(out, top, extra=0):
    """Draw the centre; extra is added to the free space so the centre can match the side columns."""
    anchors = {}
    ox0, ox1 = CX0 + 20, CX0 + 235
    fx0, fx1 = CX0 + 355, CX0 + 845
    wx0, wx1 = fx0 + 14, fx1 - 14
    bx = fx1 + 13
    mx0 = bx + 30
    mx1 = mx0 + 200
    text(out, CX0 + 24, top + 42, 'What the model reads during one task', 27, bold=True)
    text(out, CX0 + 24, top + 70, 'Start here. Panels A to E show parts of it in more detail.', 15.5,
         'ink2')
    fy0 = top + 92
    wy0 = fy0 + 62
    n1 = sum(1 for r in ROWS if r[1] == 'always')
    r1y = wy0 + 92
    block_bottom = r1y + (n1 - 1) * STEP1 + H1 + 10
    r6y = block_bottom + 42
    index = {r[0]: i for i, r in enumerate(ROWS)}

    def row_y(i):
        return r1y + i * STEP1 if i < n1 else r6y + (i - n1) * STEP2

    def row_h(i):
        return H1 if i < n1 else H2

    last = len(ROWS) - 1
    slot_y = row_y(last) + H2 + 10
    free_y = slot_y + H2
    limit_y = free_y + 90 + extra
    win_h = limit_y + 32 - wy0
    frame_h = win_h + 76

    # harness frame and window
    rect(out, fx0, fy0, fx1 - fx0, frame_h, 'frame', rx=14)
    text(out, fx0 + 16, fy0 + 27, 'Harness', 17, bold=True)
    text(out, fx0 + 92, fy0 + 27, 'builds the window, runs tools', 14, 'muted')
    rect(out, wx0, wy0, wx1 - wx0, win_h, 'win', rx=12)
    text(out, wx0 + 16, wy0 + 28, 'Context window', 18, bold=True)
    text(out, wx0 + 16, wy0 + 49, 'what the model reads for every reply', 14, 'muted')
    rect(out, wx0 + 8, wy0 + 62, wx1 - wx0 - 16, block_bottom - wy0 - 62, 'k-blue', rx=10)
    text(out, wx0 + 20, wy0 + 82, 'SENT FIRST, EVERY TIME', 12.5, 't-blue', bold=True)
    text(out, wx0 + 20, block_bottom + 28, 'THE CONVERSATION, GROWING DOWNWARDS', 12.5, 'ink2', bold=True)
    for i, (key, kind, role, label) in enumerate(ROWS):
        color, t = KIND[kind]
        y, h = row_y(i), row_h(i)
        cls = {'always': 'win', 'think': 'k-think'}.get(kind, f'k-{color}')
        rect(out, wx0 + 16, y, wx1 - wx0 - 32, h, cls, rx=7)
        if t:
            tier(out, wx0 + 24, y + (h - 22) / 2, t)
        tx = wx0 + 56
        if role:
            text(out, tx, y + h / 2 + 4.5, role, 12, f't-{color}', bold=True)
            tx += 54
        size = 14.5
        if markup_width(label, size) > wx1 - 24 - tx:
            print(f'row {key} too wide: {label}', file=sys.stderr)
        tcls = '' if kind == 'always' else f't-{color}' + (' it' if kind == 'think' else '')
        text(out, tx, y + h / 2 + 5, label, size, tcls)
    rect(out, wx0 + 16, slot_y, wx1 - wx0 - 32, H2, 'slot', rx=7)
    text(out, (wx0 + wx1) / 2, slot_y + 24, "the model's next message is added here", 14, 't-orange',
         anchor='middle')
    text(out, (wx0 + wx1) / 2, (free_y + limit_y) / 2 - 4, 'free space', 15, 'muted', anchor='middle', bold=True)
    text(out, (wx0 + wx1) / 2, (free_y + limit_y) / 2 + 18, 'Every new message and tool result uses some of it.',
         14, 'muted', anchor='middle')
    out.append(f'<line x1="{wx0+10}" y1="{limit_y}" x2="{wx1-10}" y2="{limit_y}" class="limit"/>')
    text(out, wx1 - 16, limit_y + 22, 'limit, for example 1,000,000 tokens', 13.5, 't-red', anchor='end')
    anchors['E'] = zoom(out, wx0 + 4, free_y + 6, wx1 - wx0 - 8, limit_y + 30 - free_y - 6, 'E', 'right')
    b0, b1 = index['skill-call'], index['skill']
    anchors['B'] = zoom(out, wx0 + 8, row_y(b0) - 5, wx1 - wx0 - 16, row_y(b1) + H2 + 5 - row_y(b0) + 5, 'B',
                        'right')

    # files and programs, with arrows into the window
    text(out, ox0, fy0 + 27, 'Files and programs', 17, bold=True)
    para(out, ox0, fy0 + 40, ox1 - ox0, 'On your computer. The harness copies text from them into the window. '
         'Each arrow shows when the harness adds that text. [3, 4, 5]', 14, 'muted')
    for key, kind, name, sub, label, color, src_key in ITEMS:
        i = index[key]
        h, y = row_h(i), row_y(i)
        rect(out, ox0, y, ox1 - ox0, h, 'k-grey', rx=8)
        icon(out, kind, ox0 + 8, y + h / 2 - 12)
        text(out, ox0 + 42, y + h / 2 - 3, name, 14, bold=True)
        text(out, ox0 + 42, y + h / 2 + 13, sub, 12, 'muted')
        cy = y + h / 2
        if src_key:
            src = row_y(index[src_key]) + row_h(index[src_key]) / 2
            arrow(out, [(wx0 + 8, src), (ox1 + 4, cy)], color)
            text(out, (ox1 + fx0) / 2 + 8, (src + cy) / 2 - 10, label, 12.5, f't-{color}', anchor='middle',
                 bold=True)
        else:
            arrow(out, [(ox1 + 4, cy), (wx0 + 8, cy)], color)
            text(out, (ox1 + fx0) / 2, cy - 7, label, 12.5, f't-{color}', anchor='middle', bold=True)
        if key == 'mcp':
            anchors['C'] = zoom(out, ox0 - 6, y - 6, ox1 - ox0 + 12, h + 12, 'C', 'left')
        if key == 'summary':
            anchors['D'] = zoom(out, ox0 - 6, y - 6, ox1 - ox0 + 12, h + 12, 'D', 'left')
    para(out, ox0, row_y(index['edit']) + H2 + 30, ox1 - ox0, 'In Claude Code, AGENTS.md loads only when there is '
         'no CLAUDE.md. [4]', 13, 'muted')

    # effort: a setting in the harness, sent with each request
    py = fy0 + 10
    pw = 128
    px0 = fx1 - 14 - pw
    my0 = r1y + 36
    mh = 158
    ax = mx0 + 24
    rect(out, px0, py, pw, 28, 'k-grey', rx=14)
    text(out, px0 + pw / 2, py + 19, 'effort: high', 13.5, anchor='middle', bold=True)
    arrow(out, [(px0 + pw + 2, py + 14), (ax, py + 14), (ax, my0 - 3)])
    para(out, ax + 12, py + 26, CX1 - 20 - ax - 12, '**Effort**, sent with each request: how much the model '
         'thinks and checks before it answers. See [part 2](llm-reply.svg). [6]', 13, 'ink2')

    # the model and the loop
    path(out, f'M{bx-9},{r1y} H{bx} V{row_y(last)+H2} H{bx-9}', 'bracket')
    arrow(out, [(bx, my0 + 40), (mx0 - 4, my0 + 40)])
    rect(out, mx0, my0, mx1 - mx0, mh, 'dark', rx=12)
    text(out, mx0 + 14, my0 + 30, 'Model', 20, 'on-dark', bold=True)
    text(out, mx0 + 14, my0 + 50, 'at the provider', 12.5, 'on-dark')
    para(out, mx0 + 14, my0 + 62, mx1 - mx0 - 26, 'Reads all the text in the window, then writes the next '
         'token.', 14, 'on-dark')
    anchors['A'] = zoom(out, mx0 - 7, my0 - 7, mx1 - mx0 + 14, mh + 14, 'A', 'right')
    note(out, bx + 4, my0 + mh + 22, CX1 - 30 - bx - 4, '**Model or harness?** Claude Opus is a model and Claude '
         'Code is a harness. Pi and OpenCode are harnesses that can run Claude, GPT, Gemini or Qwen. The same model '
         'gives different results in two harnesses, because each builds a different window.', 'note-grey', 13)
    rx_line = CX1 - 12
    arrow(out, [(mx1, my0 + mh - 24), (rx_line, my0 + mh - 24), (rx_line, slot_y + H2 / 2),
                (wx1 + 4, slot_y + H2 / 2)], 'orange')
    text(out, rx_line - 12, slot_y + 9, 'next message', 13, 't-orange', anchor='end', bold=True)
    mid = (r1y + row_y(last) + H2) / 2 + 190
    out.append(f'<text x="{bx+18}" y="{mid:.1f}" class="ink2" style="font-size:13.5px" '
               f'transform="rotate(-90 {bx+18} {mid:.1f})">read in full for every token*</text>')

    # legend
    ly = fy0 + frame_h + 30
    text(out, ox0, ly + 4, 'Key', 16, bold=True)
    for i, (c, s) in enumerate([('green', 'You write it'), ('orange', 'The model writes it'),
                                ('think', "The model's thinking")]):
        rect(out, ox0, ly + 22 + i * 30, 22, 22, f'k-{c}', rx=5)
        text(out, ox0 + 32, ly + 38 + i * 30, s, 15)
    lx = fx0
    for i, (n, s) in enumerate([
        (1, '**Always:** sent with every request, from the first one.'),
        (2, '**On demand:** added when the model calls a tool, and kept until compaction.'),
        (3, '**Isolated:** done in another window. Only a summary comes back.'),
    ]):
        tier(out, lx, ly - 12 + i * 30, n)
        text(out, lx + 32, ly + 4 + i * 30, s, 15)
    foot = para(out, ox0, ly + 114, CX1 - 24 - ox0, '* The model uses every earlier token for each new one, '
                'but it does not process them again. During the reply it keeps that work, and between requests '
                "the provider's cache keeps it while the start of the window stays the same "
                '(see [part 2](llm-reply.svg)). [7]',
                13.5, 'muted')
    return anchors, foot + 4


def main():
    left = [Panel(None, 'Words used here', body_words),
            Panel('C', 'MCP: tools from other programs', body_mcp),
            Panel('D', 'Subagents: a separate window', body_sub)]
    right = [Panel('A', 'One token at a time', body_model),
             Panel('B', 'A tool call is just text', body_tool),
             Panel('E', 'Recall, and what carries over', body_recall)]
    build(GEO, OUT, 'How an AI agent works',
          'The model reads text and images and writes text. The harness, the program around the model, decides '
          'what the model reads, and acts on what the model writes.',
          'The context window of an AI agent: what is always loaded, what loads on demand '
          'through tool calls, and what runs in a separate window, with zoomed panels on token-by-token '
          'writing, tool calls, MCP, subagents, recall and what carries over between sessions.',
          left, right, draw_centre,
          'Sources, read in November 2026: ' + '; '.join(f'[{i}] {s}' for i, s in enumerate(SOURCES, start=1)) +
          '. Chart shapes are illustrative.')


if __name__ == '__main__':
    main()
