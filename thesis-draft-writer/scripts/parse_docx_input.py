#!/usr/bin/env python3
"""Parse proposal, task-book, and requirement documents into structured text."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from thesis_utils import detect_title, read_text, split_lines, split_sections


def parse_document(path: str | Path) -> dict:
    path = Path(path)
    text = read_text(path)
    lines = split_lines(text)
    title = detect_title(lines, fallback=path.stem)
    return {
        "path": str(path),
        "text": text,
        "lines": lines,
        "sections": split_sections(text),
        "metadata": {
            "source_name": path.name,
            "file_type": path.suffix.lower(),
            "title": title,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    print(json.dumps(parse_document(args.path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
