#!/usr/bin/env python3
"""Normalize and deduplicate literature records."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from thesis_utils import normalize_doi


def normalize_citations(citations: list[dict]) -> dict:
    merged: dict[str, dict] = {}
    for citation in citations:
        key = citation_key(citation)
        if key in merged:
            merged[key] = merge_citation(merged[key], citation)
        else:
            merged[key] = dict(citation)
            merged[key]["doi"] = normalize_doi(merged[key].get("doi", ""))
    items = list(merged.values())
    counts = {"zh": 0, "en": 0, "other": 0}
    for item in items:
        lang = normalize_language(item.get("language", ""))
        item["language"] = lang
        counts[lang] += 1
    total = len(items) or 1
    return {
        "citations": items,
        "stats": {
            "total": len(items),
            "counts_by_language": counts,
            "chinese_ratio": counts["zh"] / total,
        },
    }


def citation_key(citation: dict) -> str:
    doi = normalize_doi(citation.get("doi", ""))
    if doi:
        return f"doi:{doi}"
    title = re.sub(r"\s+", "", (citation.get("title") or "").lower())
    title = re.sub(r"[^0-9a-z\u4e00-\u9fff]+", "", title)
    return f"title:{title}"


def merge_citation(left: dict, right: dict) -> dict:
    result = dict(left)
    for key, value in right.items():
        if not result.get(key) and value:
            result[key] = value
        elif key == "source" and value and value not in str(result.get(key, "")):
            result[key] = f"{result.get(key, '')};{value}".strip(";")
    result["doi"] = normalize_doi(result.get("doi", "") or right.get("doi", ""))
    return result


def normalize_language(value: str) -> str:
    value = (value or "").lower()
    if value.startswith("zh"):
        return "zh"
    if value.startswith("en"):
        return "en"
    if any(ch in value for ch in ["中", "汉"]):
        return "zh"
    return "other"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("citations_json")
    args = parser.parse_args()
    payload = json.loads(Path(args.citations_json).read_text(encoding="utf-8"))
    print(json.dumps(normalize_citations(payload), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
