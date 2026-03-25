#!/usr/bin/env python3
"""Generate deterministic experiment result artifacts for computing-oriented thesis drafts."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def generate_experiment_results(
    thesis_spec: dict,
    experiment_plan: dict,
    output_dir: str | Path,
    explicit_placeholder_mode: bool = False,
) -> dict:
    if not explicit_placeholder_mode:
        raise ValueError(
            "Simulated thesis results are downgrade-only. Pass explicit_placeholder_mode=True to opt in."
        )
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    domain = experiment_plan.get("domain", thesis_spec.get("domain", {}).get("primary", "generic-stem"))
    generated_files: list[str] = []
    if domain != "computing":
        notes = {
            "mode": "evidence-mapping-only",
            "message": "No computing benchmark simulation was generated for this domain.",
        }
        notes_path = output_dir / "experiment_notes.json"
        notes_path.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"mode": "evidence-mapping-only", "files": [str(notes_path)]}

    benchmark_path = output_dir / "baseline_comparison.csv"
    ablation_path = output_dir / "ablation_study.csv"
    sensitivity_path = output_dir / "sensitivity_analysis.csv"

    write_csv(
        benchmark_path,
        fieldnames=["implementation", "prove_ms", "verify_ms", "throughput_tps", "memory_mb", "proof_kb"],
        rows=[
            {"implementation": "reference-cpp", "prove_ms": 48.6, "verify_ms": 12.1, "throughput_tps": 20.4, "memory_mb": 11.8, "proof_kb": 13.4},
            {"implementation": "rust-scalar", "prove_ms": 37.2, "verify_ms": 8.7, "throughput_tps": 28.9, "memory_mb": 8.9, "proof_kb": 13.4},
            {"implementation": "rust-avx2", "prove_ms": 22.4, "verify_ms": 5.3, "throughput_tps": 47.6, "memory_mb": 5.6, "proof_kb": 13.4},
            {"implementation": "rust-avx512", "prove_ms": 11.6, "verify_ms": 2.8, "throughput_tps": 82.7, "memory_mb": 3.1, "proof_kb": 13.4},
        ],
    )
    generated_files.append(str(benchmark_path))

    write_csv(
        ablation_path,
        fieldnames=["variant", "prove_ms", "verify_ms", "throughput_tps", "memory_mb", "quality_score"],
        rows=[
            {"variant": "full-system", "prove_ms": 11.6, "verify_ms": 2.8, "throughput_tps": 82.7, "memory_mb": 3.1, "quality_score": 1.00},
            {"variant": "without-avx512", "prove_ms": 19.8, "verify_ms": 4.9, "throughput_tps": 50.8, "memory_mb": 4.9, "quality_score": 0.99},
            {"variant": "without-sparse-multiplier", "prove_ms": 17.9, "verify_ms": 4.1, "throughput_tps": 58.2, "memory_mb": 4.2, "quality_score": 0.99},
            {"variant": "without-zero-copy", "prove_ms": 15.4, "verify_ms": 3.6, "throughput_tps": 64.3, "memory_mb": 6.5, "quality_score": 1.00},
        ],
    )
    generated_files.append(str(ablation_path))

    write_csv(
        sensitivity_path,
        fieldnames=["batch_size", "prove_ms", "verify_ms", "throughput_tps", "memory_mb"],
        rows=[
            {"batch_size": 1, "prove_ms": 11.6, "verify_ms": 2.8, "throughput_tps": 82.7, "memory_mb": 3.1},
            {"batch_size": 2, "prove_ms": 18.4, "verify_ms": 4.1, "throughput_tps": 103.2, "memory_mb": 4.3},
            {"batch_size": 4, "prove_ms": 31.9, "verify_ms": 7.2, "throughput_tps": 125.4, "memory_mb": 6.9},
            {"batch_size": 8, "prove_ms": 63.7, "verify_ms": 14.8, "throughput_tps": 125.7, "memory_mb": 11.7},
        ],
    )
    generated_files.append(str(sensitivity_path))

    notes = {
        "mode": "placeholder-simulation",
        "message": (
            "These result tables are deterministic placeholder benchmark simulations for exploratory drafting only. "
            "They must not be treated as final thesis evidence."
        ),
        "files": generated_files,
    }
    notes_path = output_dir / "experiment_notes.json"
    notes_path.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")
    generated_files.append(str(notes_path))
    return {"mode": "placeholder-simulation", "files": generated_files}


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("thesis_spec_json")
    parser.add_argument("experiment_plan_json")
    parser.add_argument("output_dir")
    args = parser.parse_args()
    thesis_spec = json.loads(Path(args.thesis_spec_json).read_text(encoding="utf-8"))
    experiment_plan = json.loads(Path(args.experiment_plan_json).read_text(encoding="utf-8"))
    payload = generate_experiment_results(thesis_spec, experiment_plan, args.output_dir)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
