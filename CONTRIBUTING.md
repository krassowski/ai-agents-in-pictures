# Contributing

Every claim in a figure cites a source.

## Drawing the pictures

The scripts need the fonts Noto Sans and DejaVu Sans Mono.

```sh
pip install -r requirements.txt
for f in figures/llm-*.py; do python3 "$f"; done
python3 scripts/build-site.py  # writes the website to _site
```
