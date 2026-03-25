#!/usr/bin/env python3
"""Thin staged runner for thesis-draft-writer artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import assemble_docx
import build_figure_plan
import build_citation_bank
import draft_thesis_sections
import extract_thesis_spec
import parse_docx_input
import plan_experiments
import review_draft
import search_literature
import simulate_experiment_results
from thesis_utils import write_json


def run_workflow(
    source_paths: list[str | Path],
    artifact_dir: str | Path,
    profile: str = "generic-stem",
    literature_providers: dict[str, callable] | None = None,
    literature_input_dirs: list[str | Path] | None = None,
    allow_simulated_results: bool = False,
) -> dict:
    artifact_dir = Path(artifact_dir)
    parsed_dir = artifact_dir / "parsed_inputs"
    parsed_dir.mkdir(parents=True, exist_ok=True)

    parsed_documents = []
    for source_path in source_paths:
        source_path = Path(source_path)
        parsed = parse_docx_input.parse_document(source_path)
        parsed_documents.append(parsed)
        write_json(parsed_dir / f"{source_path.stem}.json", parsed)

    thesis_spec = extract_thesis_spec.build_thesis_spec(parsed_documents, profile_name=profile)
    write_json(artifact_dir / "thesis_spec.json", thesis_spec)

    proposal_citation_bank = build_citation_bank.build_citation_bank(parsed_documents)

    candidate_literature_files = search_literature.discover_local_literature_files(
        source_paths,
        extra_dirs=literature_input_dirs,
    )
    candidate_chinese_refs = search_literature.build_candidate_chinese_refs(
        thesis_spec,
        local_paths=candidate_literature_files,
        citation_bank=proposal_citation_bank,
        providers=literature_providers,
    )
    write_json(artifact_dir / "candidate_chinese_refs.json", candidate_chinese_refs)

    literature_queries = {
        "queries": candidate_chinese_refs["queries"],
        "profile": profile,
        "source_files": candidate_chinese_refs["source_files"],
        "providers_used": candidate_chinese_refs.get("providers_used", []),
    }
    write_json(artifact_dir / "literature_queries.json", literature_queries)

    citation_bank = build_citation_bank.build_citation_bank(
        parsed_documents,
        candidate_citations=candidate_chinese_refs["citations"],
    )
    citation_bank = build_citation_bank.curate_citation_bank(
        citation_bank,
        target_chinese_ratio=float(thesis_spec["reference_constraints"]["target_chinese_ratio"]),
        minimum_foreign_ratio=float(thesis_spec["reference_constraints"]["minimum_foreign_ratio"]),
        thesis_keywords=thesis_spec.get("keywords", []),
    )
    write_json(artifact_dir / "citation_bank.json", citation_bank)

    experiment_plan = plan_experiments.build_experiment_plan(thesis_spec)
    write_json(artifact_dir / "experiment_plan.json", experiment_plan)

    results_dir = artifact_dir / "results"
    result_csv_paths = build_figure_plan.discover_result_csvs(source_paths, extra_dirs=[results_dir])
    experiment_artifacts = {
        "mode": "external-or-missing-results",
        "message": (
            "No simulated results were generated. The main AI must supply or produce real experiment results, "
            "or explicitly opt into placeholder simulation mode for non-final exploratory work."
        ),
        "files": [str(path) for path in result_csv_paths],
    }
    if allow_simulated_results:
        experiment_artifacts = simulate_experiment_results.generate_experiment_results(
            thesis_spec,
            experiment_plan,
            results_dir,
            explicit_placeholder_mode=True,
        )
        result_csv_paths = build_figure_plan.discover_result_csvs(source_paths, extra_dirs=[results_dir])
    write_json(artifact_dir / "experiment_artifacts.json", experiment_artifacts)

    result_summaries = build_figure_plan.load_result_summaries(result_csv_paths)
    if result_summaries:
        write_json(artifact_dir / "result_summaries.json", {"summaries": result_summaries})

    figure_plan = build_figure_plan.build_figure_plan(
        thesis_spec,
        experiment_plan,
        result_summaries=result_summaries,
    )
    write_json(artifact_dir / "figure_plan.json", figure_plan)

    manifest = draft_thesis_sections.build_manifest(
        thesis_spec,
        parsed_documents,
        citation_bank,
        figure_plan,
        result_csv_paths,
    )
    write_json(artifact_dir / "docx_manifest.json", manifest)

    review_report = review_draft.build_review_report(
        thesis_spec,
        manifest,
        citation_bank,
        figure_plan=figure_plan,
        result_summaries=result_summaries,
    )
    write_json(artifact_dir / "review_report.json", review_report)

    draft_path = artifact_dir / "draft.docx"
    assemble_docx.assemble_docx(artifact_dir / "docx_manifest.json", draft_path)

    return {
        "artifact_dir": str(artifact_dir),
        "draft_path": str(draft_path),
        "title": thesis_spec["title"],
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("sources", nargs="+")
    parser.add_argument("--artifacts", default="artifacts")
    parser.add_argument("--profile", default="generic-stem")
    parser.add_argument("--literature-input-dir", action="append", default=[])
    parser.add_argument("--online-search", action="store_true")
    parser.add_argument(
        "--allow-simulated-results",
        action="store_true",
        help="Explicit downgrade mode: generate placeholder benchmark data for exploratory drafting only.",
    )
    args = parser.parse_args()
    result = run_workflow(
        args.sources,
        args.artifacts,
        args.profile,
        literature_providers=search_literature.default_free_providers() if args.online_search else None,
        literature_input_dirs=args.literature_input_dir,
        allow_simulated_results=args.allow_simulated_results,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
