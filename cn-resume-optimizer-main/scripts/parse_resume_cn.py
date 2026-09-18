#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Heuristic parser for Chinese resumes (tech-oriented by default).

Goal: stable, local-first structure extraction from plain text.

Input: a .txt produced by extract_pdf_text.py (or any text).
Output: JSON to stdout.

Usage:
  python3 scripts/parse_resume_cn.py input.txt > output/resume/resume.json

Notes:
- This is not an NLP model. It's a deterministic parser built for controllability.
- It keeps raw blocks even when field extraction is partial.
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SECTION_ALIASES = {
    "basics": ["基本信息", "个人信息", "联系方式", "信息"],
    "summary": ["个人亮点", "个人总结", "自我评价", "简介", "概述", "summary"],
    "skills": ["专业技能", "技能", "技术栈", "技能栈", "技能特长"],
    "experience": ["工作经历", "工作经验", "职业经历", "实习经历", "经历"],
    "projects": ["项目经历", "项目经验", "项目", "项目介绍"],
    "education": ["教育经历", "教育背景", "教育"],
    "awards": ["奖项", "获奖", "荣誉", "竞赛"],
    "certs": ["证书", "认证"],
    "opensource": ["开源", "作品", "作品集", "GitHub"],
}

# Common tech keywords for extraction (China tech resume focus)
TECH_TERMS = [
    # languages
    "Java", "Kotlin", "Go", "Golang", "Python", "JavaScript", "TypeScript", "C++", "C#", "Rust", "PHP", "Ruby",
    # frontend
    "React", "Vue", "Angular", "Next.js", "Nuxt", "Webpack", "Vite", "Tailwind",
    # backend
    "Spring", "SpringBoot", "Spring Cloud", "Node.js", "Express", "NestJS", "Django", "Flask", "FastAPI",
    # db/cache/mq
    "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch", "Kafka", "RocketMQ", "RabbitMQ",
    # infra
    "Linux", "Docker", "Kubernetes", "K8s", "Nginx", "Prometheus", "Grafana", "CI/CD", "Git",
]

DATE_RANGE_RE = re.compile(
    r"(?P<start>(?:19|20)\d{2}[./-](?:0?[1-9]|1[0-2])|(?:19|20)\d{2})\s*[-—~～至]+\s*(?P<end>(?:19|20)\d{2}[./-](?:0?[1-9]|1[0-2])|(?:19|20)\d{2}|至今|现在|Present)",
    re.I,
)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?<!\d)(1[3-9]\d{9})(?!\d)")


def normalize_line(s: str) -> str:
    s = s.replace("\u3000", " ").strip()
    s = re.sub(r"\s+", " ", s)
    return s


def looks_like_heading(line: str) -> str | None:
    """Return section key if line is a recognized heading."""
    clean = re.sub(r"^[#*\-\s]+", "", line).strip()
    clean = clean.strip(":：")
    if not clean:
        return None
    for key, aliases in SECTION_ALIASES.items():
        for a in aliases:
            if clean.lower() == a.lower():
                return key
    # headings like "一、工作经历" / "（二）项目经历"
    clean2 = re.sub(r"^[一二三四五六七八九十0-9]+[、.\)]\s*", "", clean)
    for key, aliases in SECTION_ALIASES.items():
        for a in aliases:
            if clean2.lower() == a.lower():
                return key
    return None


def split_sections(lines: list[str]) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {"_prelude": []}
    current = "_prelude"
    for raw in lines:
        line = normalize_line(raw)
        if not line:
            continue
        key = looks_like_heading(line)
        if key:
            current = key
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return sections


def extract_basics(text: str) -> dict[str, Any]:
    emails = list(dict.fromkeys(EMAIL_RE.findall(text)))
    phones = list(dict.fromkeys(PHONE_RE.findall(text)))

    # Intent heuristics
    intent = None
    m = re.search(r"求职意向\s*[:：]?\s*(.{2,30})", text)
    if m:
        intent = m.group(1).strip()

    # City heuristics: prefer explicit patterns
    city = None
    m = re.search(r"现居城市\s*[:：]?\s*([\u4e00-\u9fff]{2,10})", text)
    if m:
        city = m.group(1)
    if not city:
        m = re.search(r"(城市|现居|所在地)\s*[:：]\s*([\u4e00-\u9fff]{2,10})", text)
        if m:
            city = m.group(2)

    # Name heuristics: find first standalone Chinese name-like line
    name = None
    for raw in text.splitlines():
        line = normalize_line(raw)
        if not line:
            continue
        if line.startswith("=====") and "Page" in line:
            continue
        if EMAIL_RE.search(line) or PHONE_RE.search(line):
            continue
        # a single name line is usually 2-4 Chinese chars
        if re.fullmatch(r"[\u4e00-\u9fff]{2,4}", line):
            name = line
            break
        # tolerate "姓名：张三"
        m = re.match(r"姓名\s*[:：]\s*([\u4e00-\u9fff]{2,4})", line)
        if m:
            name = m.group(1)
            break

    return {
        "name": name,
        "city": city,
        "emails": emails,
        "phones": phones,
        "intent": intent,
    }


def extract_tech_keywords(text: str) -> list[str]:
    found: list[str] = []
    for t in TECH_TERMS:
        if re.search(r"\b" + re.escape(t) + r"\b", text):
            found.append(t)
    # also capture common tokens like "RPC", "HTTP", "SQL", "JWT"
    caps = re.findall(r"\b[A-Z][A-Z0-9+./-]{1,10}\b", text)
    for c in caps:
        if c not in found and len(c) <= 10:
            found.append(c)
    return found


def parse_entries_by_date(block_lines: list[str]) -> list[dict[str, Any]]:
    """Split a section into entries using date ranges as anchors."""
    entries: list[list[str]] = []
    current: list[str] = []
    for line in block_lines:
        if DATE_RANGE_RE.search(line) and current:
            entries.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        entries.append(current)

    out: list[dict[str, Any]] = []
    for e in entries:
        raw = "\n".join(e).strip()
        dr = DATE_RANGE_RE.search(raw)
        dates = None
        if dr:
            dates = {"start": dr.group("start"), "end": dr.group("end")}
        out.append({"raw": raw, "dates": dates})
    return out


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in {"-h", "--help"}:
        sys.stderr.write("Usage: python3 scripts/parse_resume_cn.py <input.txt>\n")
        return 2

    p = Path(argv[1]).expanduser().resolve()
    text = p.read_text(encoding="utf-8", errors="ignore")

    lines = text.splitlines()
    sections = split_sections(lines)

    basics = extract_basics(text)
    tech = extract_tech_keywords(text)

    experience = parse_entries_by_date(sections.get("experience", []))
    projects = parse_entries_by_date(sections.get("projects", []))
    education = parse_entries_by_date(sections.get("education", []))

    result: dict[str, Any] = {
        "basics": basics,
        "sections": {k: "\n".join(v).strip() for k, v in sections.items() if k != "_prelude"},
        "prelude": "\n".join(sections.get("_prelude", [])).strip(),
        "tech_keywords": tech,
        "experience": experience,
        "projects": projects,
        "education": education,
        "meta": {
            "parser": "cn-resume-optimizer/scripts/parse_resume_cn.py",
            "version": "0.1.0",
        },
    }

    sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
