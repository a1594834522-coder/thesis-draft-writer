#!/usr/bin/env python3
"""Summarize CSV result tables for thesis charts and tables."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def summarize_csv(csv_path: str | Path) -> dict:
    csv_path = Path(csv_path)
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    numeric_columns: dict[str, list[float]] = {}
    for row in rows:
        for key, value in row.items():
            try:
                numeric_columns.setdefault(key, []).append(float(value))
            except (TypeError, ValueError):
                continue
    summary = {
        key: {
            "min": min(values),
            "max": max(values),
            "mean": sum(values) / len(values),
        }
        for key, values in numeric_columns.items()
        if values
    }
    return {
        "row_count": len(rows),
        "numeric_columns": summary,
        "recommended_plots": sorted(summary.keys()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    args = parser.parse_args()
    print(json.dumps(summarize_csv(args.csv_path), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
