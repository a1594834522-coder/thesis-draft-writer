#!/usr/bin/env python3
"""Shared helpers for thesis-draft-writer scripts."""

from __future__ import annotations

import html
import json
import re
import subprocess
import zipfile
from pathlib import Path


SECTION_PATTERNS = [
    re.compile(r"^[一二三四五六七八九十百]+、"),
    re.compile(r"^（[一二三四五六七八九十百]+）"),
    re.compile(r"^第[一二三四五六七八九十百]+章"),
    re.compile(r"^\d+(?:\.\d+)*\s+"),
]


def read_text(path: Path) -> str:
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix in {".doc", ".docx", ".rtf", ".html", ".htm"}:
        text = _read_with_textutil(path)
        if text.strip():
            return clean_text(text)
        if suffix == ".docx":
            return clean_text(_read_docx_xml(path))
    return clean_text(path.read_text(encoding="utf-8"))


def _read_with_textutil(path: Path) -> str:
    command = ["textutil", "-convert", "txt", "-stdout", str(path)]
    result = subprocess.run(command, check=False, capture_output=True)
    if result.returncode != 0:
        return ""
    return result.stdout.decode("utf-8", errors="ignore")


def _read_docx_xml(path: Path) -> str:
    with zipfile.ZipFile(path) as archive:
        raw = archive.read("word/document.xml").decode("utf-8", errors="ignore")
    raw = raw.replace("</w:p>", "\n")
    raw = re.sub(r"<[^>]+>", "", raw)
    return html.unescape(raw)


def clean_text(text: str) -> str:
    text = text.replace("\r", "\n").replace("\f", "\n")
    text = html.unescape(text)
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def split_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip()]


def detect_title(lines: list[str], fallback: str = "") -> str:
    title_pattern = re.compile(r"题\s*目[:：]\s*(.+)")
    for line in lines[:80]:
        match = title_pattern.search(line)
        if match:
            return match.group(1).strip()
    for idx, line in enumerate(lines[:20]):
        if "毕业论文" in line or "开题报告" in line or "学位论文" in line:
            for candidate in lines[idx + 1 : idx + 8]:
                if len(candidate) >= 8 and not candidate.startswith("姓") and not candidate.startswith("学"):
                    return candidate.strip()
    return fallback


def split_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current_heading = "全文"
    sections[current_heading] = []
    for line in split_lines(text):
        if is_heading(line):
            current_heading = line
            sections.setdefault(current_heading, [])
        else:
            sections.setdefault(current_heading, []).append(line)
    return {key: "\n".join(value).strip() for key, value in sections.items() if value or key != "全文"}


def is_heading(line: str) -> bool:
    stripped = line.strip()
    if stripped in {"摘要", "ABSTRACT", "目 录", "目录", "参考文献", "附录", "致谢"}:
        return True
    if any(pattern.match(stripped) for pattern in SECTION_PATTERNS[:3]):
        return True
    if SECTION_PATTERNS[3].match(stripped):
        if not contains_chinese(stripped):
            return False
        if re.fullmatch(r"\d+(?:\.\d+)*\s*[A-Za-z%/().-]+", stripped):
            return False
        if re.search(r"\b(?:KB|MB|GB|ms|cycles|x)\b", stripped, flags=re.IGNORECASE):
            return False
        return len(stripped) <= 40
    return False


def normalize_doi(value: str) -> str:
    value = (value or "").strip()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value, flags=re.IGNORECASE)
    return value.lower()


def contains_chinese(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text or ""))


def write_json(path: Path, payload: dict) -> None:
    path = Path(path)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
