#!/usr/bin/env python3
"""Build a lightweight citation bank from parsed documents."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import normalize_citations


def build_citation_bank(parsed_documents: list[dict], candidate_citations: list[dict] | None = None) -> dict:
    section_text = ""
    for document in parsed_documents:
        sections = document.get("sections", {})
        section_text = sections.get("六、参考文献", "") or section_text
    raw_lines = split_reference_lines(section_text)
    citations: list[dict] = []
    for index, line in enumerate(raw_lines, start=1):
        cleaned = normalize_reference_line(line)
        if not cleaned:
            continue
        title = cleaned
        title_match = re.search(r"\.\s*([^.\[]+?)\s*\[[A-Z/]+\]", cleaned)
        if title_match:
            title = title_match.group(1).strip()
        language = "zh" if re.search(r"[\u4e00-\u9fff]", cleaned) else "en"
        citations.append(
            {
                "index": index,
                "raw": cleaned,
                "title": title,
                "language": language,
                "provider": "source-document",
            }
        )
    citations.extend(candidate_citations or [])
    normalized = normalize_citations.normalize_citations(citations)
    normalized_citations = []
    for index, citation in enumerate(normalized["citations"], start=1):
        item = dict(citation)
        item["index"] = index
        item["raw"] = item.get("raw") or build_reference_entry(item)
        normalized_citations.append(item)
    return {
        "citations": normalized_citations,
        "stats": normalized["stats"],
    }


def curate_citation_bank(
    citation_bank: dict,
    target_chinese_ratio: float = 0.35,
    minimum_foreign_ratio: float = 0.33,
    max_total: int = 18,
    thesis_keywords: list[str] | None = None,
) -> dict:
    citations = [dict(item) for item in citation_bank.get("citations", [])]
    zh = sorted(
        [item for item in citations if item.get("language") == "zh"],
        key=lambda item: reference_relevance_score(item, thesis_keywords),
        reverse=True,
    )
    foreign = sorted(
        [item for item in citations if item.get("language") != "zh"],
        key=lambda item: reference_relevance_score(item, thesis_keywords),
        reverse=True,
    )
    if not zh:
        curated = []
        counts = {"zh": 0, "en": 0, "other": 0}
        for index, citation in enumerate(citations[:max_total], start=1):
            item = dict(citation)
            language = item.get("language", "other")
            if language not in counts:
                language = "other"
            counts[language] += 1
            item["index"] = index
            item["raw"] = item.get("raw") or build_reference_entry(item)
            curated.append(item)
        total = len(curated) or 1
        return {
            "citations": curated,
            "stats": {
                "total": len(curated),
                "counts_by_language": counts,
                "chinese_ratio": counts["zh"] / total,
            },
        }
    selected = list(zh)
    target_total_cap = max_total
    if target_chinese_ratio > 0:
        target_total_cap = min(max_total, max(len(selected), int(len(selected) / target_chinese_ratio)))
    foreign_budget = max(target_total_cap - len(selected), 0)
    selected.extend(foreign[:foreign_budget])
    while len(selected) > 1:
        total = len(selected)
        zh_count = sum(1 for item in selected if item.get("language") == "zh")
        foreign_count = total - zh_count
        chinese_ratio = zh_count / total if total else 0.0
        foreign_ratio = foreign_count / total if total else 0.0
        if chinese_ratio >= target_chinese_ratio or foreign_count <= 1:
            break
        candidate = selected[-1]
        if candidate.get("language") == "zh":
            break
        next_total = total - 1
        next_foreign_ratio = (foreign_count - 1) / next_total if next_total else 0.0
        if next_foreign_ratio < minimum_foreign_ratio:
            break
        selected.pop()
    counts = {"zh": 0, "en": 0, "other": 0}
    curated = []
    for index, citation in enumerate(selected, start=1):
        item = dict(citation)
        language = item.get("language", "other")
        if language not in counts:
            language = "other"
        counts[language] += 1
        item["index"] = index
        item["raw"] = item.get("raw") or build_reference_entry(item)
        curated.append(item)
    total = len(curated) or 1
    return {
        "citations": curated,
        "stats": {
            "total": len(curated),
            "counts_by_language": counts,
            "chinese_ratio": counts["zh"] / total,
        },
    }


def normalize_reference_line(line: str) -> str:
    cleaned = line.replace("\u200f", "").replace("\u200e", "").strip()
    cleaned = re.sub(r"^[\[\(]?\d+[\]\)]\s*", "", cleaned).strip()
    return cleaned


def split_reference_lines(section_text: str) -> list[str]:
    lines: list[str] = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        chunks = re.split(r"(?=\[\d+\]\s*)", stripped)
        for chunk in chunks:
            cleaned = chunk.strip()
            if cleaned:
                lines.append(cleaned)
    return lines


def format_reference_list(citation_bank: dict) -> str:
    return "\n".join(
        f"[{item['index']}] {item.get('raw') or build_reference_entry(item)}"
        for item in citation_bank.get("citations", [])
    )


def build_reference_entry(citation: dict) -> str:
    authors = citation.get("authors") or []
    if isinstance(authors, str):
        authors = [authors]
    author_text = ", ".join(item.strip() for item in authors if item and str(item).strip())
    year = citation.get("year")
    source = str(citation.get("source") or "").strip()
    title = str(citation.get("title") or "题名待补充").strip()
    doi = str(citation.get("doi") or "").strip()
    pieces = [piece for piece in [author_text, title] if piece]
    if source:
        pieces.append(source)
    if year:
        pieces.append(str(year))
    entry = ". ".join(pieces).strip(". ")
    if doi:
        entry = f"{entry}. DOI: {doi}" if entry else f"DOI: {doi}"
    return entry or title


def reference_relevance_score(citation: dict, thesis_keywords: list[str] | None = None) -> tuple[int, int]:
    thesis_keywords = thesis_keywords or []
    haystack = " ".join(
        [
            str(citation.get("title", "")),
            str(citation.get("source", "")),
            str(citation.get("raw", "")),
            " ".join(str(item) for item in citation.get("keywords", []) if str(item).strip()),
            str(citation.get("abstract", "")),
        ]
    ).lower()
    keyword_hits = sum(1 for keyword in thesis_keywords if keyword and str(keyword).lower() in haystack)
    method_terms = [
        "implementation",
        "实现",
        "experiment",
        "实验",
        "evaluation",
        "评估",
        "optimization",
        "优化",
        "system",
        "系统",
        "model",
        "模型",
        "analysis",
        "分析",
    ]
    method_hits = sum(1 for term in method_terms if term in haystack)
    year = int(citation.get("year") or 0)
    return (keyword_hits * 5 + method_hits * 2, year)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("parsed_json", nargs="+")
    args = parser.parse_args()
    parsed_documents = [
        json.loads(Path(path).read_text(encoding="utf-8"))
        for path in args.parsed_json
    ]
    print(json.dumps(build_citation_bank(parsed_documents), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
