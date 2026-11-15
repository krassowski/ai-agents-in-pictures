#!/usr/bin/env python3
"""Build the website: one HTML page for each README.md, with the figures and a PNG of each.

Usage: python3 build-site.py [--out _site] [--base-url URL] [--repo-url URL] [--no-png]

--base-url is the address the site is published at, for the link preview image.
--repo-url is the GitHub repository; links to code then open there instead of in the site.
"""

import argparse
import html
import re
import shutil
from pathlib import Path
from urllib.parse import urljoin

from markdown_it import MarkdownIt

import render_png

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['README.md', 'simple-harness/README.md']

CSS = """
:root { color-scheme: light dark; --bg: #fbfaf7; --ink: #1c1b19; --ink2: #4a4945; --line: #dddbd3;
  --code: #f1f0eb; --link: #1f5fae; }
@media (prefers-color-scheme: dark) {
  :root { --bg: #151514; --ink: #f3f2ee; --ink2: #c9c7c0; --line: #3a3934; --code: #262623; --link: #86b6f0; }
}
* { box-sizing: border-box; }
body { margin: 0; background: var(--bg); color: var(--ink);
  font: 17px/1.6 system-ui, -apple-system, 'Segoe UI', Roboto, 'Noto Sans', sans-serif; }
main { padding: 32px 16px 24px; }
main > * { max-width: 46rem; margin-left: auto; margin-right: auto; }
main > figure { max-width: 2360px; margin: 24px auto 40px; }
h1 { font-size: 2.3rem; line-height: 1.15; margin-bottom: 0.6em; }
h2 { font-size: 1.5rem; line-height: 1.25; margin-top: 2.6em; padding-top: 1.2em; border-top: 1px solid var(--line); }
a { color: var(--link); }
code { font: 0.88em/1.5 'DejaVu Sans Mono', Menlo, Consolas, monospace; background: var(--code);
  padding: 0.1em 0.3em; border-radius: 4px; }
pre { background: var(--code); padding: 12px 16px; border-radius: 8px; overflow-x: auto; }
pre code { padding: 0; background: none; }
figure img { display: block; width: 100%; height: auto; border: 1px solid var(--line); border-radius: 12px; }
figcaption { margin-top: 8px; text-align: center; color: var(--ink2); font-size: 0.95rem; }
footer { max-width: 46rem; margin: 0 auto; padding: 16px 16px 48px; border-top: 1px solid var(--line);
  color: var(--ink2); font-size: 0.95rem; }
"""

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>{title}</title>
<meta name="description" content="{description}">
{preview}<style>{css}</style>
</head>
<body>
<main>
{body}</main>
{footer}</body>
</html>
"""


def slug(heading, seen):
    """The anchor GitHub gives a heading: lower case, punctuation removed, spaces as hyphens."""
    base = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
    n = seen.get(base, 0)
    seen[base] = n + 1
    return base if n == 0 else f'{base}-{n}'


def plain(fragment):
    return html.unescape(re.sub(r'<[^>]+>', '', fragment)).strip()


def svg_size(path):
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', path.read_text(encoding='utf-8'))
    return round(float(m.group(1))), round(float(m.group(2)))


rendered = set()


def build_page(md_path, out, args, browser):
    """Write the HTML page of one README.md and copy or render what it shows."""
    page_dir = md_path.parent
    rel_dir = page_dir.relative_to(ROOT)
    body = MarkdownIt('commonmark', {'html': True}).enable('table').render(md_path.read_text(encoding='utf-8'))

    seen = {}
    body = re.sub(r'<h([1-6])>(.*?)</h\1>',
                  lambda m: f'<h{m.group(1)} id="{slug(plain(m.group(2)), seen)}">{m.group(2)}</h{m.group(1)}>',
                  body)

    def figure(m):
        src, alt = html.unescape(m.group(1)), m.group(2)
        svg = (page_dir / src).resolve()
        dest = out / svg.relative_to(ROOT)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(svg, dest)
        width, height = svg_size(svg)
        links = f'<a href="{m.group(1)}">Open at full size</a>'
        if browser:
            if dest not in rendered:
                render_png.render(svg, dest.with_suffix('.png'), browser=browser)
                rendered.add(dest)
            png = m.group(1)[:-4] + '.png'
            links += f' · <a href="{png}" download>Download as PNG</a>'
        return (f'<figure><a href="{m.group(1)}"><img src="{m.group(1)}" alt="{alt}" width="{width}" '
                f'height="{height}"></a>\n<figcaption>{links}</figcaption></figure>')

    body = re.sub(r'<p><img src="([^"]+\.svg)" alt="([^"]*)" /></p>', figure, body)

    def link(m):
        href = html.unescape(m.group(1))
        if re.match(r'[a-z]+:|#', href):
            return m.group(0)
        path, _, anchor = href.partition('#')
        target = (page_dir / path).resolve()
        if target.is_dir() and (target / 'README.md').is_file():
            target = target / 'README.md'
        if target.name == 'README.md' and str(target.relative_to(ROOT)) in PAGES:
            new = Path(path).parent / 'index.html' if path.endswith('README.md') else Path(path) / 'index.html'
            new = new.as_posix() + (f'#{anchor}' if anchor else '')
        elif target.suffix in ('.svg', '.png'):
            return m.group(0)
        elif args.repo_url:
            kind = 'tree' if target.is_dir() else 'blob'
            new = f'{args.repo_url}/{kind}/HEAD/{target.relative_to(ROOT).as_posix()}'
        else:
            dest = out / target.relative_to(ROOT)
            dest.parent.mkdir(parents=True, exist_ok=True)
            if target.is_file():
                shutil.copyfile(target, dest)
            return m.group(0)
        return f'<a href="{html.escape(new)}"'

    body = re.sub(r'<a href="([^"]*)"', link, body)

    title = plain(re.search(r'<h1[^>]*>(.*?)</h1>', body).group(1))
    description = plain(re.search(r'<p>(.*?)</p>', body, re.S).group(1))
    preview = ''
    if args.base_url:
        url = args.base_url.rstrip('/') + '/' + (rel_dir.as_posix() + '/' if rel_dir.parts else '')
        image = re.search(r'<img src="([^"]+)\.svg"', body)
        preview = ('<meta property="og:type" content="website">\n'
                   f'<meta property="og:title" content="{html.escape(title)}">\n'
                   f'<meta property="og:description" content="{html.escape(description)}">\n'
                   f'<meta property="og:url" content="{url}">\n')
        if image and browser:
            preview += (f'<meta property="og:image" content="{urljoin(url, image.group(1) + ".png")}">\n'
                        '<meta name="twitter:card" content="summary_large_image">\n')
    footer = ''
    if args.repo_url:
        footer = f'<footer>The scripts that draw these pages are on <a href="{args.repo_url}">GitHub</a>.</footer>\n'
    page = PAGE.format(title=html.escape(title), description=html.escape(description), preview=preview, css=CSS,
                       body=body, footer=footer)
    dest = out / rel_dir / 'index.html'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page, encoding='utf-8')
    print(f'wrote {dest}')


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('--out', type=Path, default=ROOT / '_site')
    parser.add_argument('--base-url', help='where the site is published, such as https://example.github.io/repo/')
    parser.add_argument('--repo-url', help='the GitHub repository, such as https://github.com/example/repo')
    parser.add_argument('--no-png', action='store_true', help='leave out the PNG files')
    args = parser.parse_args()
    browser = None if args.no_png else render_png.find_browser()
    for page in PAGES:
        build_page(ROOT / page, args.out, args, browser)
    print(f'the website is in {args.out}')


if __name__ == '__main__':
    main()
