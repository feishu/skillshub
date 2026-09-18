#!/usr/bin/env bash
set -euo pipefail

# Local Markdown -> PDF converter.
# Stable + controllable: relies on local tooling only.
# Preferred: pandoc -> HTML -> weasyprint.
#
# Usage:
#   bash scripts/md2pdf.sh input.md output.pdf

in="${1:-}"
out="${2:-}"

if [[ -z "$in" || -z "$out" ]]; then
  echo "Usage: bash scripts/md2pdf.sh <input.md> <output.pdf>" >&2
  exit 2
fi

if [[ ! -f "$in" ]]; then
  echo "Input not found: $in" >&2
  exit 2
fi

command -v pandoc >/dev/null 2>&1 || { echo "Missing pandoc. Install: apt-get install pandoc" >&2; exit 1; }
command -v weasyprint >/dev/null 2>&1 || { echo "Missing weasyprint. Install: apt-get install python3-weasyprint (or pip install weasyprint)" >&2; exit 1; }

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

html="$tmpdir/out.html"
css="$tmpdir/style.css"

cat >"$css" <<'CSS'
@page { size: A4; margin: 18mm 16mm; }
body { font-family: "Noto Sans CJK SC", "Noto Sans SC", "Microsoft YaHei", "PingFang SC", "Heiti SC", Arial, sans-serif; font-size: 10.5pt; line-height: 1.35; color: #111; }
h1 { font-size: 18pt; margin: 0 0 6pt 0; }
h2 { font-size: 12pt; margin: 14pt 0 6pt 0; border-bottom: 0.6pt solid #ddd; padding-bottom: 2pt; }
h3 { font-size: 11pt; margin: 10pt 0 4pt 0; }
ul { margin: 4pt 0 6pt 18pt; }
li { margin: 2pt 0; }
code, pre { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
pre { background: #f6f6f6; padding: 8pt; border-radius: 4pt; overflow-wrap: anywhere; }
hr { border: none; border-top: 0.6pt solid #ddd; margin: 10pt 0; }
CSS

pandoc "$in" -o "$html" --standalone --metadata title="Resume" --css "$css" --from markdown
weasyprint "$html" "$out"

echo "Wrote: $out" >&2
