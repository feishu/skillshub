#!/usr/bin/env bash
set -euo pipefail

mkdir -p ./examples/out

# demo: parse resume + jd
python3 ./scripts/parse_resume_cn.py ./examples/resume_text.txt > ./examples/out/resume.json
python3 ./scripts/parse_jd_cn.py ./examples/jd.txt > ./examples/out/jd.json

echo "Wrote: examples/out/resume.json"
echo "Wrote: examples/out/jd.json"
