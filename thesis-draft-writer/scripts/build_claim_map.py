#!/usr/bin/env python3
"""Build a lightweight claim-to-citation map from draft text."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


def build_claim_map(text: str) -> dict:
    claims = []
    for paragraph in [item.strip() for item in text.split("\n") if item.strip()]:
        if len(paragraph) < 20:
            continue
        citations = re.findall(r"\[[0-9,\-\s]+\]|\([^)]+,\s*\d{4}[a-z]?\)", paragraph)
        claims.append(
            {
                "claim": paragraph,
                "citations": citations,
                "supported": bool(citations),
            }
        )
    return {"claims": claims}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("text_file")
    args = parser.parse_args()
    text = Path(args.text_file).read_text(encoding="utf-8")
    print(json.dumps(build_claim_map(text), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
