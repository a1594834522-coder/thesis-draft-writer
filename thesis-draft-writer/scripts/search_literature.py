#!/usr/bin/env python3
"""Free-first literature search helpers."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from thesis_utils import contains_chinese, normalize_doi
import normalize_citations


USER_AGENT = "thesis-draft-writer/0.1 (local skill)"


def normalize_openalex_work(record: dict) -> dict:
    source = record.get("primary_location", {}).get("source", {}) or {}
    return {
        "provider": "openalex",
        "id": record.get("id", ""),
        "doi": normalize_doi(record.get("doi", "")),
        "title": (record.get("title") or "").strip(),
        "year": record.get("publication_year"),
        "language": (record.get("language") or "").strip() or infer_language(record.get("title", "")),
        "source": source.get("display_name", ""),
        "authors": [
            authorship.get("author", {}).get("display_name", "")
            for authorship in record.get("authorships", [])
            if authorship.get("author", {}).get("display_name")
        ],
        "url": record.get("id", ""),
    }


def normalize_crossref_work(record: dict) -> dict:
    titles = record.get("title") or [""]
    source_titles = record.get("container-title") or [""]
    authors = []
    for author in record.get("author", []):
        family = (author.get("family") or "").strip()
        given = (author.get("given") or "").strip()
        full_name = " ".join(part for part in [family, given] if part)
        if full_name:
            authors.append(full_name)
    date_parts = record.get("issued", {}).get("date-parts", [[None]])
    year = date_parts[0][0] if date_parts and date_parts[0] else None
    return {
        "provider": "crossref",
        "id": record.get("URL", ""),
        "doi": normalize_doi(record.get("DOI", "")),
        "title": (titles[0] or "").strip(),
        "year": year,
        "language": normalize_language_code(record.get("language", "")) or infer_language(titles[0] if titles else ""),
        "source": source_titles[0] if source_titles else "",
        "authors": authors,
        "url": record.get("URL", ""),
    }


def normalize_arxiv_work(record: dict) -> dict:
    published = (record.get("published") or "")[:4]
    year = int(published) if published.isdigit() else None
    return {
        "provider": "arxiv",
        "id": record.get("id", ""),
        "doi": "",
        "title": (record.get("title") or "").strip(),
        "year": year,
        "language": infer_language(record.get("title", "")),
        "source": "arXiv",
        "authors": [item.get("name", "") for item in record.get("authors", []) if item.get("name")],
        "url": record.get("id", ""),
    }


def infer_language(title: str) -> str:
    return "zh" if any("\u4e00" <= ch <= "\u9fff" for ch in title) else "en"


def normalize_language_code(value: str) -> str:
    value = (value or "").lower()
    if value.startswith("zh"):
        return "zh"
    if value.startswith("en"):
        return "en"
    return ""


def search_openalex(query: str, per_page: int = 10) -> list[dict]:
    params = urllib.parse.urlencode({"search": query, "per-page": per_page})
    request = urllib.request.Request(
        f"https://api.openalex.org/works?{params}",
        headers={"User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return [normalize_openalex_work(item) for item in payload.get("results", [])]


def search_crossref(query: str, rows: int = 10) -> list[dict]:
    params = urllib.parse.urlencode({"query": query, "rows": rows})
    request = urllib.request.Request(
        f"https://api.crossref.org/works?{params}",
        headers={"User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    items = payload.get("message", {}).get("items", [])
    return [normalize_crossref_work(item) for item in items]


def rank_results(results: list[dict], prefer_chinese: bool = False) -> list[dict]:
    def score(item: dict) -> tuple[int, int, int]:
        language = item.get("language", "")
        chinese_bonus = 1 if prefer_chinese and language == "zh" else 0
        year = int(item.get("year") or 0)
        provider_bonus = 1 if item.get("provider") in {"crossref", "openalex", "arxiv"} else 0
        return (chinese_bonus, provider_bonus, year)

    return sorted(results, key=score, reverse=True)


def aggregate_search_results(
    query: str,
    limit: int = 10,
    providers: dict[str, callable] | None = None,
    prefer_chinese: bool = False,
) -> dict:
    providers = providers or {
        "openalex": search_openalex,
        "crossref": search_crossref,
    }
    merged_results = []
    providers_used = []
    for name, fn in providers.items():
        try:
            provider_results = fn(query, limit)
        except Exception:
            provider_results = []
        if provider_results:
            providers_used.append(name)
            merged_results.extend(provider_results)
    normalized = normalize_citations.normalize_citations(merged_results)
    ranked = rank_results(normalized["citations"], prefer_chinese=prefer_chinese)
    return {
        "query": query,
        "results": ranked,
        "providers_used": providers_used,
        "stats": normalized["stats"],
    }


def default_free_providers() -> dict[str, callable]:
    return {
        "openalex": search_openalex,
        "crossref": search_crossref,
    }


def import_local_literature_candidates(paths: list[str | Path]) -> dict:
    records: list[dict] = []
    source_files: list[str] = []
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists() or not path.is_file():
            continue
        imported = import_local_literature_file(path)
        if imported:
            source_files.append(str(path))
            records.extend(imported)
    normalized = normalize_citations.normalize_citations(records)
    citations = []
    for index, citation in enumerate(normalized["citations"], start=1):
        item = dict(citation)
        item["index"] = index
        citations.append(item)
    return {
        "citations": citations,
        "stats": normalized["stats"],
        "source_files": source_files,
    }


def import_local_literature_file(path: str | Path) -> list[dict]:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".json":
        return import_local_literature_json(path)
    if suffix in {".txt", ".md"}:
        return import_local_literature_text(path)
    return []


def import_local_literature_json(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        records = payload.get("citations") or payload.get("results") or payload.get("items") or []
    elif isinstance(payload, list):
        records = payload
    else:
        records = []
    normalized_records = []
    for record in records:
        normalized = normalize_local_candidate_record(record, source_hint=path.stem)
        if normalized:
            normalized_records.append(normalized)
    return normalized_records


def import_local_literature_text(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    blocks = split_local_text_blocks(text)
    records = []
    for block in blocks:
        parsed = parse_local_text_block(block, source_hint=path.stem)
        if parsed:
            records.append(parsed)
    return records


def split_local_text_blocks(text: str) -> list[str]:
    chunks = [chunk.strip() for chunk in re.split(r"\n\s*\n", text) if chunk.strip()]
    if len(chunks) > 1:
        return chunks
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in lines:
        if current and re.match(r"^(题名|标题|Title)\s*[:：]", line):
            blocks.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append(current)
    return ["\n".join(block) for block in blocks]


def parse_local_text_block(block: str, source_hint: str = "") -> dict | None:
    fields = {
        "title": "",
        "authors": [],
        "source": "",
        "year": None,
        "doi": "",
        "url": "",
        "language": "zh",
        "provider": "local-import",
    }
    label_map = {
        "题名": "title",
        "标题": "title",
        "title": "title",
        "作者": "authors",
        "authors": "authors",
        "来源": "source",
        "刊名": "source",
        "source": "source",
        "年份": "year",
        "年": "year",
        "year": "year",
        "doi": "doi",
        "链接": "url",
        "网址": "url",
        "url": "url",
    }
    for line in block.splitlines():
        match = re.match(r"^\s*([^:：]+)\s*[:：]\s*(.+?)\s*$", line)
        if not match:
            continue
        label = match.group(1).strip().lower()
        value = match.group(2).strip()
        field_name = label_map.get(label)
        if not field_name or not value:
            continue
        if field_name == "authors":
            fields["authors"] = [item.strip() for item in re.split(r"[；;,，、]\s*", value) if item.strip()]
        elif field_name == "year":
            year_match = re.search(r"\d{4}", value)
            fields["year"] = int(year_match.group(0)) if year_match else None
        else:
            fields[field_name] = value
    if not fields["title"]:
        return None
    if not fields["source"]:
        fields["source"] = source_hint
    return normalize_local_candidate_record(fields, source_hint=source_hint)


def normalize_local_candidate_record(record: dict, source_hint: str = "") -> dict | None:
    title = str(record.get("title") or record.get("题名") or record.get("标题") or "").strip()
    if not title:
        return None
    authors = record.get("authors") or record.get("作者") or []
    if isinstance(authors, str):
        authors = [item.strip() for item in re.split(r"[；;,，、]\s*", authors) if item.strip()]
    year = record.get("year") or record.get("年份")
    if isinstance(year, str):
        year_match = re.search(r"\d{4}", year)
        year = int(year_match.group(0)) if year_match else None
    return {
        "provider": str(record.get("provider") or "local-import").strip() or "local-import",
        "id": str(record.get("id") or record.get("url") or title),
        "doi": normalize_doi(str(record.get("doi") or "")),
        "title": title,
        "year": year if isinstance(year, int) else None,
        "language": normalize_language_code(str(record.get("language") or "")) or infer_language(title),
        "source": str(record.get("source") or record.get("刊名") or source_hint or "").strip(),
        "authors": authors,
        "url": str(record.get("url") or record.get("链接") or ""),
        "keywords": record.get("keywords") or record.get("关键词") or [],
        "abstract": str(record.get("abstract") or record.get("摘要") or "").strip(),
    }


def build_candidate_chinese_refs(
    thesis_spec: dict,
    local_paths: list[str | Path] | None = None,
    citation_bank: dict | None = None,
    imported_candidates: dict | list[dict] | None = None,
    providers: dict[str, callable] | None = None,
    max_queries: int = 5,
    per_query_limit: int = 5,
) -> dict:
    queries = local_chinese_query_candidates(thesis_spec)
    imported = import_local_literature_candidates(local_paths or [])
    imported_records = [canonicalize_chinese_citation(citation) for citation in imported["citations"] if is_chinese_citation(citation)]
    imported_records.extend(
        canonicalize_chinese_citation(citation)
        for citation in extract_citation_records(imported_candidates)
        if is_chinese_citation(citation)
    )
    seed_records = [
        canonicalize_chinese_citation(citation)
        for citation in (citation_bank or {}).get("citations", [])
        if is_chinese_citation(citation)
    ]
    retrieved_records: list[dict] = []
    providers_used: list[str] = []
    active_providers = providers or {}
    for query in queries[:max_queries]:
        if not active_providers:
            break
        aggregated = aggregate_search_results(
            query=query,
            limit=per_query_limit,
            providers=active_providers,
            prefer_chinese=True,
        )
        for provider in aggregated.get("providers_used", []):
            if provider not in providers_used:
                providers_used.append(provider)
        retrieved_records.extend(
            canonicalize_chinese_citation(citation)
            for citation in aggregated.get("results", [])
            if is_chinese_citation(citation) and passes_relevance_gate(citation, thesis_spec, query)
        )
    normalized = normalize_citations.normalize_citations(seed_records + imported_records + retrieved_records)
    citations = []
    for index, citation in enumerate(rank_results(normalized["citations"], prefer_chinese=True), start=1):
        item = dict(citation)
        item["index"] = index
        citations.append(item)
    stats = dict(normalized["stats"])
    stats.update(
        {
            "seed_count": len(seed_records),
            "imported_count": len(imported_records),
            "retrieved_count": len(retrieved_records),
        }
    )
    return {
        "profile": thesis_spec.get("profile", ""),
        "queries": queries,
        "citations": citations,
        "stats": stats,
        "source_files": imported["source_files"],
        "providers_used": providers_used,
    }


def discover_local_literature_files(source_paths: list[str | Path], extra_dirs: list[str | Path] | None = None) -> list[Path]:
    candidates: list[Path] = []
    seen: set[Path] = set()
    search_dirs = [Path.cwd() / "literature_inputs"]
    for source_path in source_paths:
        search_dirs.append(Path(source_path).resolve().parent / "literature_inputs")
    for extra_dir in extra_dirs or []:
        search_dirs.append(Path(extra_dir))
    for directory in search_dirs:
        if not directory.exists() or not directory.is_dir():
            continue
        for path in sorted(directory.iterdir()):
            if path.suffix.lower() not in {".json", ".txt", ".md"} or not path.is_file():
                continue
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            candidates.append(resolved)
    return candidates


def extract_citation_records(payload: dict | list[dict] | None) -> list[dict]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return [dict(item) for item in payload]
    return [dict(item) for item in payload.get("citations", [])]


def is_chinese_citation(citation: dict) -> bool:
    language = normalize_language_code(str(citation.get("language", "")))
    if language == "zh":
        return True
    title = str(citation.get("title") or "")
    source = str(citation.get("source") or "")
    return contains_chinese(title) or contains_chinese(source)


def canonicalize_chinese_citation(citation: dict) -> dict:
    item = dict(citation)
    if is_chinese_citation(item):
        item["language"] = "zh"
    return item


def passes_relevance_gate(citation: dict, thesis_spec: dict, query: str) -> bool:
    text = " ".join(
        [
            str(citation.get("title") or ""),
            str(citation.get("source") or ""),
            " ".join(citation.get("authors") or []),
        ]
    ).lower()
    query_terms = [term.strip().lower() for term in query.split() if term.strip()]
    keyword_terms = [str(term).strip().lower() for term in thesis_spec.get("keywords", []) if str(term).strip()]
    query_matches = [term for term in query_terms if term in text]
    keyword_matches = [term for term in keyword_terms if term in text]
    generic_research_terms = [
        "实现",
        "implementation",
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
    research_term_hits = [term for term in generic_research_terms if term in text]
    if len(keyword_matches) >= 2:
        return True
    if len(keyword_matches) >= 1 and len(research_term_hits) >= 1:
        return True
    if len(query_matches) >= 2:
        return True
    if len(query_matches) >= 1 and len(research_term_hits) >= 1:
        return True
    return False


def local_chinese_query_candidates(thesis_spec: dict) -> list[str]:
    keywords = thesis_spec.get("keywords", [])
    candidates: list[str] = []
    title = str(thesis_spec.get("title") or "").strip()
    chinese_keywords = [term for term in keywords if any("\u4e00" <= ch <= "\u9fff" for ch in str(term))]
    for size in (2, 3):
        if len(chinese_keywords) >= size:
            candidates.append(" ".join(chinese_keywords[:size]))
    if chinese_keywords:
        candidates.append(" ".join(chinese_keywords[:2] + ["研究"]))
        candidates.append(" ".join(chinese_keywords[:2] + ["实验"]))
        candidates.append(" ".join(chinese_keywords[:2] + ["实现"]))
    if title:
        title_terms = [term for term in chinese_keywords[:3] if term]
        if title_terms:
            candidates.append(" ".join(title_terms))
    if thesis_spec.get("title"):
        noun_phrase = re.sub(r"[^\w\u4e00-\u9fff]+", " ", thesis_spec["title"]).strip()
        if noun_phrase:
            candidates.append(noun_phrase[:24].strip())
    deduped = []
    for candidate in candidates:
        candidate = re.sub(r"\s+", " ", candidate).strip()
        if candidate and candidate not in deduped:
            deduped.append(candidate)
    return deduped


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("--provider", default="openalex", choices=["openalex", "crossref", "all"])
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--prefer-chinese", action="store_true")
    args = parser.parse_args()
    if args.provider == "openalex":
        results = search_openalex(args.query, args.limit)
        payload = {"query": args.query, "results": results, "providers_used": ["openalex"]}
    elif args.provider == "crossref":
        results = search_crossref(args.query, args.limit)
        payload = {"query": args.query, "results": results, "providers_used": ["crossref"]}
    else:
        payload = aggregate_search_results(
            args.query,
            args.limit,
            prefer_chinese=args.prefer_chinese,
        )
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
