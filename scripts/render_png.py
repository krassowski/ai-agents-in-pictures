#!/usr/bin/env python3
"""Render SVG files to PNG files with Chrome or Chromium in headless mode.

Usage: python3 render_png.py [--scale N] [--dark] [--out-dir DIR] FILE.svg...

Each PNG is written next to its SVG, or into --out-dir. The browser is the CHROME
environment variable, else the first of google-chrome, chromium, chromium-browser
and chrome-headless-shell that is on the PATH.
"""

import argparse
import math
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

BROWSERS = ['google-chrome', 'chromium', 'chromium-browser', 'chrome-headless-shell']


def find_browser():
    found = os.environ.get('CHROME') or next(filter(None, map(shutil.which, BROWSERS)), None)
    if not found:
        sys.exit('render_png.py: no browser found, so set CHROME to the path of Chrome or Chromium')
    return found


def render(svg, png, scale=1, dark=False, browser=None):
    """Write the PNG of the SVG file svg to png, at scale pixels per SVG unit."""
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', svg.read_text(encoding='utf-8'))
    width, height = (math.ceil(float(v)) for v in m.groups())
    with tempfile.TemporaryDirectory() as profile:
        cmd = [browser or find_browser(), '--headless', '--hide-scrollbars', f'--user-data-dir={profile}',
               f'--force-device-scale-factor={scale}', f'--window-size={width},{height}',
               f'--screenshot={png.resolve()}', svg.resolve().as_uri()]
        if dark:
            cmd.insert(2, '--blink-settings=preferredColorScheme=0')
        subprocess.run(cmd, check=True, capture_output=True)
    got = struct.unpack('>II', png.read_bytes()[16:24])
    want = (round(width * scale), round(height * scale))
    if got != want:
        sys.exit(f'render_png.py: {png} is {got[0]}x{got[1]} pixels, not {want[0]}x{want[1]}')
    print(f'wrote {png} ({width}x{height} at {scale}x, {"dark" if dark else "light"})')


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    parser.add_argument('svgs', nargs='+', type=Path, metavar='FILE.svg')
    parser.add_argument('--scale', type=float, default=1, help='pixels per SVG unit (default 1)')
    parser.add_argument('--dark', action='store_true', help='draw the dark colours')
    parser.add_argument('--out-dir', type=Path, help='folder for the PNG files')
    args = parser.parse_args()
    browser = find_browser()
    for svg in args.svgs:
        name = svg.with_suffix('.png').name if not args.dark else svg.stem + '-dark.png'
        render(svg, (args.out_dir or svg.parent) / name, args.scale, args.dark, browser)


if __name__ == '__main__':
    main()
