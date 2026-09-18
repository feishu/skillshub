#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Heuristic extractor for Chinese Job Descriptions (JD).

Input: plain text (paste/export).
Output: JSON with responsibilities/requirements/keywords.

Usage:
  python3 scripts/parse_jd_cn.py jd.txt > output/resume/jd.json

Design principles:
- Deterministic + local-first.
- Optimized for China tech roles (开发/前端/后端/算法/测试/运维/产品技术侧协作).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


RESP_HEADINGS = [
    "岗位职责", "工作职责", "职责描述", "职位描述", "你将", "工作内容", "Responsibilities",
]
REQ_HEADINGS = [
    "任职要求", "岗位要求", "任职资格", "任职条件", "我们希望", "你需要", "Requirements",
]

TECH_TERMS = [
    "Java", "Kotlin", "Go", "Golang", "Python", "JavaScript", "TypeScript", "C++", "C#", "Rust",
    "React", "Vue", "Angular", "Next.js", "Node.js",
    "Spring", "Spring Boot", "SpringCloud", "MySQL", "PostgreSQL", "Redis", "Kafka", "RocketMQ",
    "Docker", "Kubernetes", "Linux", "Nginx", "Elasticsearch", "Prometheus", "Grafana", "Git",
    "微服务", "分布式", "高并发", "高可用", "性能优化", "系统设计", "数据库", "缓存", "消息队列",
]


def norm(s: str) -> str:
    s = s.replace("\u3000", " ").strip()
    s = re.sub(r"\s+", " ", s)
    return s


def split_blocks(text: str) -> dict[str, list[str]]:
    lines = [norm(x) for x in text.splitlines()]
    lines = [x for x in lines if x]

    blocks: dict[str, list[str]] = {"_all": lines}

    def is_heading(line: str, headings: list[str]) -> bool:
        clean = line.strip(":：")
        clean = re.sub(r"^[一二三四五六七八九十0-9]+[、.\)]\s*", "", clean)
        return any(clean.lower() == h.lower() for h in headings)

    current = "_other"
    blocks[current] = []
    for line in lines:
        if is_heading(line, RESP_HEADINGS):
            current = "responsibilities"
            blocks.setdefault(current, [])
            continue
        if is_heading(line, REQ_HEADINGS):
            current = "requirements"
            blocks.setdefault(current, [])
            continue
        blocks.setdefault(current, []).append(line)

    return blocks


def extract_bullets(lines: list[str]) -> list[str]:
    out: list[str] = []
    for l in lines:
        # bullet-like
        m = re.match(r"^(?:[-*•]|\d+[.、\)]|[一二三四五六七八九十]+[、.\)])\s*(.+)$", l)
        if m:
            item = m.group(1).strip()
            if item:
                out.append(item)
        else:
            # keep short imperative lines
            if len(l) <= 60:
                out.append(l)
    # dedupe
    seen = set()
    dedup = []
    for x in out:
        if x not in seen:
            seen.add(x)
            dedup.append(x)
    return dedup


def extract_keywords(text: str) -> list[str]:
    found: list[str] = []
    # tech terms
    for t in TECH_TERMS:
        if t.lower() in text.lower():
            found.append(t)
    # uppercase tokens
    caps = re.findall(r"\b[A-Z][A-Z0-9+./-]{1,12}\b", text)
    for c in caps:
        if c not in found:
            found.append(c)
    # Chinese keywords from common patterns (very lightweight)
    cn = re.findall(r"([\u4e00-\u9fff]{2,6})", text)
    # keep only those that look like requirement nouns
    stop = {"我们", "负责", "以及", "相关", "以上", "能力", "工作", "经验", "熟悉", "掌握", "具备", "优先", "岗位", "职责", "要求"}
    freq: dict[str, int] = {}
    for w in cn:
        if w in stop:
            continue
        if any(ch in w for ch in "：。、（）()"):
            continue
        freq[w] = freq.get(w, 0) + 1
    for w, _ in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[:25]:
        if w not in found:
            found.append(w)
    return found


def infer_title(text: str) -> str | None:
    # Try patterns like "职位：XX" or first line short
    m = re.search(r"(职位|岗位|职务)\s*[:：]\s*(.{2,30})", text)
    if m:
        return m.group(2).strip()
    first = next((norm(x) for x in text.splitlines() if norm(x)), "")
    if 2 <= len(first) <= 30:
        return first
    return None


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in {"-h", "--help"}:
        sys.stderr.write("Usage: python3 scripts/parse_jd_cn.py <jd.txt>\n")
        return 2

    p = Path(argv[1]).expanduser().resolve()
    text = p.read_text(encoding="utf-8", errors="ignore")

    blocks = split_blocks(text)
    resps = extract_bullets(blocks.get("responsibilities", []))
    reqs = extract_bullets(blocks.get("requirements", []))

    title = infer_title(text)
    keywords = extract_keywords(text)

    result: dict[str, Any] = {
        "title": title,
        "responsibilities": resps,
        "requirements": reqs,
        "keywords": keywords,
        "raw": text.strip(),
        "meta": {
            "extractor": "cn-resume-optimizer/scripts/parse_jd_cn.py",
            "version": "0.1.0",
        },
    }

    sys.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
