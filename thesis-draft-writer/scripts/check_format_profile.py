#!/usr/bin/env python3
"""Validate a draft manifest against a profile."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PROFILE_RULES = {
    "generic-stem": {
        "required_sections": [
            "cover",
            "originality_statement",
            "authorization_statement",
            "abstract_zh",
            "abstract_en",
            "keywords",
            "table_of_contents",
            "main_body",
            "conclusion_or_discussion",
            "references",
            "appendix",
            "profile_or_bio",
            "acknowledgements",
        ]
    },
    "computing-thesis": {
        "required_sections": [
            "cover",
            "originality_statement",
            "authorization_statement",
            "abstract_zh",
            "abstract_en",
            "keywords",
            "table_of_contents",
            "main_body",
            "conclusion_or_discussion",
            "references",
            "appendix",
            "profile_or_bio",
            "acknowledgements",
        ]
    }
}


def validate_manifest(manifest: dict, profile_name: str = "generic-stem") -> dict:
    rules = PROFILE_RULES[profile_name]
    current = set(manifest.get("sections", []))
    issues = []
    for section in rules["required_sections"]:
        if section not in current:
            issues.append(
                {
                    "severity": "blocker",
                    "message": f"Missing required section: {section}",
                }
            )
    return {
        "profile": profile_name,
        "issues": issues,
        "required_sections": rules["required_sections"],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest_json")
    parser.add_argument("--profile", default="generic-stem")
    args = parser.parse_args()
    manifest = json.loads(Path(args.manifest_json).read_text(encoding="utf-8"))
    print(json.dumps(validate_manifest(manifest, args.profile), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
