#!/usr/bin/env python3
"""Create a domain-aware experiment plan skeleton."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def build_experiment_plan(thesis_spec: dict) -> dict:
    domain = thesis_spec.get("domain", {}).get("primary", "generic-stem")
    if domain == "computing":
        experiments = [
            {
                "name": "baseline-comparison",
                "goal": "Compare the proposed method with at least one baseline implementation.",
                "metrics": ["latency", "latency_ms", "throughput", "memory_mb"],
            },
            {
                "name": "ablation-study",
                "goal": "Measure the effect of removing or simplifying major method components.",
                "metrics": ["latency", "latency_ms", "memory_mb", "quality_score"],
            },
            {
                "name": "sensitivity-analysis",
                "goal": "Check parameter stability and identify robust operating ranges.",
                "metrics": ["latency", "latency_ms", "accuracy", "memory_mb"],
            },
        ]
    else:
        experiments = [
            {
                "name": "evidence-mapping",
                "goal": "Map research questions to available evidence and analytical procedures.",
                "metrics": ["coverage_ratio", "evidence_count"],
            }
        ]
    return {
        "title": thesis_spec.get("title", ""),
        "domain": domain,
        "research_questions": thesis_spec.get("research_questions", []),
        "experiments": experiments,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("thesis_spec_json")
    args = parser.parse_args()
    thesis_spec = json.loads(Path(args.thesis_spec_json).read_text(encoding="utf-8"))
    print(json.dumps(build_experiment_plan(thesis_spec), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
