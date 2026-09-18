#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Extract text from a PDF locally.

Design goals (stable + controllable):
- Local-first: no network calls.
- Prefer native text layer; OCR is intentionally NOT bundled to avoid heavy deps.
- Keep a JSON/MD-friendly output for downstream resume parsing.

Usage:
  python3 scripts/extract_pdf_text.py input.pdf > output/resume/raw_text.txt

If PyMuPDF is missing:
  pip install PyMuPDF
"""

from __future__ import annotations

import sys
from pathlib import Path


def extract_text_pymupdf(pdf_path: Path) -> str:
    try:
        import fitz  # PyMuPDF
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "Missing dependency: PyMuPDF (import fitz). Install with: pip install PyMuPDF"
        ) from e

    doc = fitz.open(str(pdf_path))
    chunks: list[str] = []
    try:
        for page in doc:
            # sort=True helps some multi-column layouts read more naturally
            text = page.get_text(sort=True)
            chunks.append(text)
    finally:
        doc.close()

    # Add simple page breaks to keep a hint of structure
    out: list[str] = []
    for i, t in enumerate(chunks, start=1):
        out.append(f"\n\n===== Page {i} =====\n\n")
        out.append(t.rstrip())
    return "".join(out).strip() + "\n"


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in {"-h", "--help"}:
        sys.stderr.write(
            "Usage: python3 scripts/extract_pdf_text.py <input.pdf>\n"
        )
        return 2

    pdf_path = Path(argv[1]).expanduser().resolve()
    if not pdf_path.exists() or pdf_path.suffix.lower() != ".pdf":
        sys.stderr.write(f"Invalid PDF path: {pdf_path}\n")
        return 2

    try:
        text = extract_text_pymupdf(pdf_path)
    except Exception as e:
        sys.stderr.write(f"PDF extract failed: {e}\n")
        return 1

    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
