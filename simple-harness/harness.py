#!/usr/bin/env python3
"""A simple agent harness: a small local model, AGENTS.md, a list of skills and one tool.

Run it in a project folder, for example in the example folder next to this file:

    cd example
    python3 ../harness.py

Type a task at the > prompt. /raw prints all the text that the model has read and written
so far, /temp 0.8 sets the temperature, and Ctrl-D quits.
"""

import argparse
import re
from pathlib import Path

from llama_cpp import Llama

MODEL = ('ggml-org/gemma-4-E4B-it-GGUF', 'gemma-4-E4B-it-Q4_0.gguf')
CALL = re.compile(r'CALL read\("([^"]+)"\)')
MAX_CALLS = 5
DIM, PLAIN = '\x1b[2m', '\x1b[0m'

INSTRUCTIONS = """\
You are a coding agent. You help with one task at a time in a project folder.
Reply in plain, short sentences, and give only what the task asks for."""

SKILLS = """\
# Skills

A skill is a file with steps for one kind of task. When a task matches a skill, first read the skill's file \
with the read tool, then follow its steps.

"""

TOOLS = """\
# Tools

You have one tool, read, which returns the text of a file in the project folder.
To use it, reply with one line like this and nothing else:
CALL read("{example}")
The program then replies with RESULT: and the text of the file."""


def skill_list(root):
    """One line per skill: its name, its description and the path of its file."""
    lines = []
    for path in sorted(root.glob('skills/*/SKILL.md')):
        meta = dict(re.findall(r'^(name|description): *(.+)$', path.read_text(encoding='utf-8'), re.M))
        lines.append(f'- {meta.get("name", path.parent.name)}: {meta.get("description", "")} '
                     f'File: {path.relative_to(root).as_posix()}')
    return lines


def system_prompt(root):
    """The text that the harness sends first, every time."""
    parts = [INSTRUCTIONS]
    agents = root / 'AGENTS.md'
    if agents.is_file():
        parts.append('# AGENTS.md\n\n' + agents.read_text(encoding='utf-8').strip())
    skills = skill_list(root)
    if skills:
        parts.append(SKILLS + '\n'.join(skills))
    # an example with a path from this project helps small models copy the format
    example = skills[-1].rsplit('File: ', 1)[1] if skills else 'AGENTS.md'
    parts.append(TOOLS.format(example=example))
    return '\n\n'.join(parts)


def read(root, name):
    """The read tool: the text of a file in the project folder, or an error for the model."""
    path = (root / name).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        return f'error: {name} is not a file in the project folder'
    return path.read_text(encoding='utf-8', errors='replace')[:20_000]


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--model', help='a GGUF model file (default: download Gemma 4 E4B, 4.6 GB)')
    args = parser.parse_args()
    if args.model:
        path = args.model
    else:
        from huggingface_hub import hf_hub_download
        path = hf_hub_download(*MODEL)
    model = Llama(model_path=path, n_ctx=8192, seed=0, verbose=False)
    root = Path.cwd().resolve()
    chat = [{'role': 'system', 'content': system_prompt(root)}]
    temperature = 0.2

    def reply():
        text = ''
        # stop if the model starts to write a result itself
        for chunk in model.create_chat_completion(chat, temperature=temperature, stop=['RESULT:'], stream=True):
            piece = chunk['choices'][0]['delta'].get('content') or ''
            text += piece
            print(piece, end='', flush=True)
        print()
        return text

    while True:
        try:
            line = input('> ').strip()
        except EOFError:
            print()
            break
        if line == '/raw':
            tokens = model.input_ids[:model.n_tokens].tolist()
            print(model.detokenize(tokens, special=True).decode(errors='replace'))
            print(f'{DIM}[{len(tokens)} tokens]{PLAIN}')
        elif line.startswith('/temp '):
            try:
                temperature = float(line.split()[1])
            except ValueError:
                print('usage: /temp 0.8')
        elif line:
            chat.append({'role': 'user', 'content': line})
            text = reply()
            for _ in range(MAX_CALLS):
                call = CALL.search(text)
                if not call:
                    break
                result = read(root, call.group(1))
                print(f'{DIM}[harness: ran read("{call.group(1)}"), sending {len(result)} characters back]{PLAIN}')
                chat.append({'role': 'assistant', 'content': text[:call.end()]})
                chat.append({'role': 'user', 'content': 'RESULT: ' + result})
                text = reply()
            chat.append({'role': 'assistant', 'content': text})


if __name__ == '__main__':
    main()
