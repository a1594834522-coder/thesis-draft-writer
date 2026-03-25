#!/usr/bin/env python3
"""Build a lightweight review report for a generated thesis manuscript."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import check_format_profile


HEADING_TO_SECTION_ID = {
    "封面": "cover",
    "独创性声明": "originality_statement",
    "论文使用授权说明": "authorization_statement",
    "摘要": "abstract_zh",
    "ABSTRACT": "abstract_en",
    "关键词": "keywords",
    "目录": "table_of_contents",
    "结论与讨论": "conclusion_or_discussion",
    "参考文献": "references",
    "附录": "appendix",
    "个人简介": "profile_or_bio",
    "致谢": "acknowledgements",
}

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
WINDOWS_ABS_RE = re.compile(r"^[A-Za-z]:[\\/]")


def build_review_report(
    thesis_spec: dict,
    manifest: dict,
    citation_bank: dict,
    figure_plan: dict | None = None,
    result_summaries: list[dict] | None = None,
) -> dict:
    profile_name = thesis_spec.get("profile", "generic-stem")
    section_ids = extract_manifest_section_ids(manifest)
    format_report = check_format_profile.validate_manifest(
        {"sections": section_ids},
        profile_name=profile_name,
    )
    issues = list(format_report.get("issues", []))
    issues.extend(review_target_level(profile_name, manifest))
    issues.extend(review_placeholders(manifest))
    issues.extend(review_abstracts(manifest))
    issues.extend(review_research_questions(thesis_spec))
    issues.extend(review_citation_balance(thesis_spec, citation_bank))
    issues.extend(review_citation_topicality(thesis_spec, citation_bank, manifest))
    issues.extend(review_experiment_evidence(thesis_spec, manifest, figure_plan or {}, result_summaries or []))
    issues.extend(review_figure_plan(manifest, figure_plan or {}))
    issues.extend(review_dev_stage_markers(manifest))
    issues.extend(review_conclusion_alignment(thesis_spec, manifest))
    issues.extend(review_language_mechanics(manifest))
    issues.extend(review_proposal_tone(manifest))
    severity_counts = count_severities(issues)
    return {
        "profile": profile_name,
        "issues": issues,
        "summary": {
            "issue_count": len(issues),
            "severity_counts": severity_counts,
            "passes_blocker_gate": severity_counts["blocker"] == 0,
        },
    }


def extract_manifest_section_ids(manifest: dict) -> list[str]:
    section_ids: list[str] = []
    for section in manifest.get("sections", []):
        heading = str(section.get("heading", "")).strip()
        if heading.startswith("第") and "章" in heading and "main_body" not in section_ids:
            section_ids.append("main_body")
        section_id = HEADING_TO_SECTION_ID.get(heading)
        if section_id and section_id not in section_ids:
            section_ids.append(section_id)
    return section_ids


def review_abstracts(manifest: dict) -> list[dict]:
    issues: list[dict] = []
    english_abstract = get_section_body(manifest, "ABSTRACT")
    if not english_abstract:
        issues.append(
            {
                "severity": "blocker",
                "message": "English abstract is missing.",
            }
        )
    elif "placeholder" in english_abstract.lower():
        issues.append(
            {
                "severity": "major",
                "message": "English abstract still uses placeholder text.",
            }
        )
    elif contains_cjk(english_abstract):
        issues.append(
            {
                "severity": "major",
                "message": "English abstract still contains Chinese text and needs full English academic prose.",
            }
        )
    chinese_abstract = get_section_body(manifest, "摘要")
    if not chinese_abstract:
        issues.append(
            {
                "severity": "blocker",
                "message": "Chinese abstract is missing.",
            }
        )
    return issues


def review_target_level(profile_name: str, manifest: dict) -> list[dict]:
    if profile_name in {"generic-stem", "computing-thesis"}:
        expected_level = "undergraduate"
    elif "master" in profile_name:
        expected_level = "master"
    else:
        expected_level = ""
    cover_body = get_section_body(manifest, "封面")
    if not cover_body or not expected_level:
        return []
    if expected_level == "master" and "硕士" not in cover_body:
        return [{"severity": "blocker", "message": "Cover text does not match the active master-thesis profile."}]
    if expected_level == "master" and "本科" in cover_body:
        return [{"severity": "blocker", "message": "Cover text still claims undergraduate degree level under a master-thesis profile."}]
    if expected_level == "undergraduate" and "本科" not in cover_body:
        return [{"severity": "blocker", "message": "Cover text does not match the active undergraduate-thesis profile."}]
    if expected_level == "undergraduate" and "硕士" in cover_body:
        return [{"severity": "blocker", "message": "Cover text still claims master degree level under an undergraduate-thesis profile."}]
    return []


def review_placeholders(manifest: dict) -> list[dict]:
    issues: list[dict] = []
    for section in manifest.get("sections", []):
        body = str(section.get("body", ""))
        if any(token in body for token in ["待补充", "待核对", "placeholder"]):
            issues.append(
                {
                    "severity": "major",
                    "message": f"Section {section.get('heading', '')} still contains placeholder-style text.",
                }
            )
    return issues


def review_citation_balance(thesis_spec: dict, citation_bank: dict) -> list[dict]:
    stats = citation_bank.get("stats", {})
    total = int(stats.get("total") or 0)
    if total <= 0:
        return [{"severity": "blocker", "message": "Reference section is empty."}]
    counts = stats.get("counts_by_language", {})
    chinese_ratio = float(stats.get("chinese_ratio") or 0.0)
    foreign_ratio = float(counts.get("en", 0)) / total
    constraints = thesis_spec.get("reference_constraints", {})
    target_chinese_ratio = float(constraints.get("target_chinese_ratio") or 0.0)
    minimum_foreign_ratio = float(constraints.get("minimum_foreign_ratio") or 0.0)
    issues: list[dict] = []
    if chinese_ratio < target_chinese_ratio:
        issues.append(
            {
                "severity": "major",
                "message": (
                    f"Chinese citation ratio {chinese_ratio:.2f} is below target {target_chinese_ratio:.2f}."
                ),
            }
        )
    if foreign_ratio < minimum_foreign_ratio:
        issues.append(
            {
                "severity": "major",
                "message": (
                    f"Foreign citation ratio {foreign_ratio:.2f} is below minimum {minimum_foreign_ratio:.2f}."
                ),
            }
        )
    return issues


def review_citation_topicality(thesis_spec: dict, citation_bank: dict, manifest: dict) -> list[dict]:
    citations = citation_bank.get("citations", [])
    if not citations:
        return []
    keywords = [str(item).strip().lower() for item in thesis_spec.get("keywords", []) if str(item).strip()]
    total = len(citations)
    relevant = [item for item in citations if is_relevant_reference(item, keywords)]
    min_relevant = min(6, max(3, total // 3))
    issues: list[dict] = []
    if len(relevant) < min_relevant:
        issues.append(
            {
                "severity": "major",
                "message": (
                    f"Citation bank is numerically sufficient but thematically weak: only {len(relevant)}/{total} references appear tightly related to the thesis topic."
                ),
            }
        )
    zh_citations = [item for item in citations if item.get("language") == "zh"]
    zh_relevant = [item for item in zh_citations if is_relevant_reference(item, keywords)]
    if len(zh_citations) >= 3 and len(zh_relevant) < min(2, len(zh_citations)):
        issues.append(
            {
                "severity": "major",
                "message": "Chinese references meet the ratio target but are not specific enough to the thesis topic.",
            }
        )
    experiment_body = get_section_body(manifest, "第四章 实验设计与结果分析")
    if experiment_body:
        experiment_refs = [
            item
            for item in citations
            if has_any_term(item, ["implementation", "benchmark", "performance", "experiment", "evaluation", "实现", "优化", "实验", "评估"])
        ]
        if len(experiment_refs) < 2:
            issues.append(
                {
                    "severity": "minor",
                    "message": "Experiment chapter has too little citation support for implementation or benchmarking claims.",
                }
            )
    return issues


def review_experiment_evidence(
    thesis_spec: dict,
    manifest: dict,
    figure_plan: dict,
    result_summaries: list[dict],
) -> list[dict]:
    issues: list[dict] = []
    experiment_body = get_section_body(manifest, "第四章 实验设计与结果分析")
    domain = str((thesis_spec.get("domain") or {}).get("primary") or "").strip().lower()
    allow_simulated = bool(thesis_spec.get("allow_simulated_experiments"))
    requires_original = bool((thesis_spec.get("execution_requirements") or {}).get("requires_original_experiments")) or domain in {
        "computing",
        "engineering",
        "data-science",
        "life-science",
    }
    simulated_markers = ["模拟", "占位", "placeholder", "draft-only", "结构化 benchmark", "结构化benchmark", "synthetic", "simulated"]
    if experiment_body and not result_summaries:
        issues.append(
            {
                "severity": "blocker",
                "message": "Experiment chapter exists but no result summaries were provided.",
            }
        )
    if experiment_body and result_summaries and not any(marker in experiment_body for marker in simulated_markers) and "实测" not in experiment_body and "重复测量" not in experiment_body:
        issues.append(
            {
                "severity": "major",
                "message": "Experiment chapter does not explain whether the evidence is simulated or measured.",
            }
        )
    if (
        experiment_body
        and requires_original
        and not allow_simulated
        and any(marker in experiment_body for marker in simulated_markers)
        and "实测" not in experiment_body
    ):
        issues.append(
            {
                "severity": "blocker",
                "message": "Experiment-capable thesis still relies only on simulated evidence; AI-produced original experiments are required.",
            }
        )
    if experiment_body and domain in {"computing", "engineering", "data-science", "engineering"}:
        implementation_terms = ["实现", "代码", "编译", "运行", "模块", "命令", "工具链", "脚本", "benchmark", "实验程序", "仓库", "配置"]
        if not any(term in experiment_body for term in implementation_terms):
            issues.append(
                {
                    "severity": "blocker",
                    "message": "Computing thesis does not provide enough implementation evidence to show that thesis-critical code was actually written or executed.",
                }
            )
    if experiment_body and not re.search(r"\[[0-9,\s]+\]", experiment_body):
        issues.append(
            {
                "severity": "major",
                "message": "Experiment chapter lacks inline citations for implementation or benchmarking claims.",
            }
        )
    if experiment_body:
        required_signals = required_method_signals(domain)
        missing = [
            label
            for label, terms in required_signals.items()
            if not any(term in experiment_body for term in terms)
        ]
        if missing:
            issues.append(
                {
                    "severity": "major",
                    "message": f"Experiment chapter is missing methodological scaffolding for: {', '.join(missing)}.",
                }
            )
    if result_summaries and not figure_plan.get("figures"):
        issues.append(
            {
                "severity": "major",
                "message": "Result summaries exist but no figure plan was generated.",
            }
        )
    return issues


def review_dev_stage_markers(manifest: dict) -> list[dict]:
    issues: list[dict] = []
    forbidden_markers = [
        "thesis-draft-writer",
        "simulate_experiment_results.py",
        "summarize_results.py",
        "build_figure_plan.py",
        "prompt_placeholder",
        "提示词",
        "结果工件",
        "可验证工作流",
        "当前初稿阶段",
        "draft-stage",
    ]
    soft_markers = ["本论文草稿", "论文草稿", "工作流", "artifact", "results/", "待替换", "待后续补充"]
    for section in manifest.get("sections", []):
        heading = str(section.get("heading", "")).strip()
        body = str(section.get("body", ""))
        if any(marker in body for marker in forbidden_markers):
            issues.append(
                {
                    "severity": "major",
                    "message": f"Section {heading} still contains development-stage or workflow-only markers.",
                }
            )
            continue
        if heading in {"独创性声明", "论文使用授权说明", "附录", "结论与讨论", "致谢"} and any(
            marker in body for marker in soft_markers
        ):
            issues.append(
                {
                    "severity": "major",
                    "message": f"Section {heading} still reads like an internal draft artifact rather than thesis text.",
                }
            )
    return issues


def review_figure_plan(manifest: dict, figure_plan: dict) -> list[dict]:
    issues: list[dict] = []
    figures = figure_plan.get("figures", [])
    if not figures:
        return issues
    cover_body = get_section_body(manifest, "封面")
    target_level = "undergraduate" if "本科" in cover_body else "graduate" if "硕士" in cover_body else ""
    seen_titles: set[str] = set()
    duplicate_titles: set[str] = set()
    for figure in figures:
        title = str(figure.get("中文标题", "")).strip()
        if title in seen_titles:
            duplicate_titles.add(title)
        if title:
            seen_titles.add(title)
        metric = str(figure.get("metric", "")).strip().lower()
        if metric in {"accuracy", "quality_score"}:
            issues.append(
                {
                    "severity": "minor",
                    "message": f"Figure {title or figure.get('figure_number', '')} uses a generic metric that may be low-value for this thesis topic.",
                }
            )
        for key in ["source_data", "prompt_placeholder"]:
            value = str(figure.get(key, ""))
            if is_absolute_path_text(value):
                issues.append(
                    {
                        "severity": "major",
                        "message": f"Figure {title or figure.get('figure_number', '')} still leaks absolute local paths in {key}.",
                    }
                )
        prompt = str(figure.get("prompt_placeholder", ""))
        if target_level == "undergraduate" and "硕士论文" in prompt:
            issues.append(
                {
                    "severity": "minor",
                    "message": f"Figure {title or figure.get('figure_number', '')} uses graduate-level prompt text that conflicts with the undergraduate thesis context.",
                }
            )
        if target_level == "graduate" and "本科毕业论文" in prompt:
            issues.append(
                {
                    "severity": "minor",
                    "message": f"Figure {title or figure.get('figure_number', '')} uses undergraduate-level prompt text that conflicts with the graduate thesis context.",
                }
            )
    if duplicate_titles:
        issues.append(
            {
                "severity": "major",
                "message": f"Figure plan contains duplicated figure titles: {', '.join(sorted(duplicate_titles))}.",
            }
        )
    return issues


def review_proposal_tone(manifest: dict) -> list[dict]:
    issues: list[dict] = []
    for heading in ["第三章 系统设计与实现", "第四章 实验设计与结果分析", "结论与讨论"]:
        body = get_section_body(manifest, heading)
        if not body:
            continue
        if any(token in body for token in ["本研究旨在", "核心目标", "拟采用", "计划通过", "预期达到"]):
            issues.append(
                {
                    "severity": "major",
                    "message": f"Section {heading} still reads like a proposal instead of a final thesis section.",
                }
            )
    return issues


def review_research_questions(thesis_spec: dict) -> list[dict]:
    questions = [str(item).strip() for item in thesis_spec.get("research_questions", []) if str(item).strip()]
    if not questions:
        return [{"severity": "blocker", "message": "Thesis spec does not define concrete research questions."}]
    issues: list[dict] = []
    weak_markers = [
        "可复现且可验证的实现方案",
        "如何通过基线对比、消融和敏感性实验验证方案的有效性",
        "如何在性能、资源消耗和工程可维护性之间取得平衡",
        "可靠的研究论证链",
    ]
    if any(marker in question for question in questions for marker in weak_markers):
        issues.append(
            {
                "severity": "blocker",
                "message": "Research questions are still generic prompt templates instead of thesis-specific questions.",
            }
        )
    if any(len(question) < 12 for question in questions):
        issues.append(
            {
                "severity": "major",
                "message": "At least one research question is too short to be operational and thesis-specific.",
            }
        )
    return issues


def review_conclusion_alignment(thesis_spec: dict, manifest: dict) -> list[dict]:
    conclusion = get_section_body(manifest, "结论与讨论")
    questions = [str(item).strip("？?。 ") for item in thesis_spec.get("research_questions", []) if str(item).strip()]
    if not conclusion or not questions:
        return []
    issues: list[dict] = []
    for question in questions:
        question_terms = [term for term in re.split(r"[^\w\u4e00-\u9fff]+", question) if len(term) >= 2]
        if question_terms and not any(term in conclusion for term in question_terms[:3]):
            issues.append(
                {
                    "severity": "major",
                    "message": f"Conclusion does not clearly resolve research question: {question}",
                }
            )
            break
    return issues


def review_language_mechanics(manifest: dict) -> list[dict]:
    issues: list[dict] = []
    bodies = "\n".join(str(section.get("body", "")) for section in manifest.get("sections", []))
    mechanical_markers = [
        "综上所述，可以看出",
        "值得注意的是",
        "不难发现",
        "由此可见",
        "进一步而言",
    ]
    hits = [marker for marker in mechanical_markers if marker in bodies]
    if len(hits) >= 3:
        issues.append(
            {
                "severity": "major",
                "message": "Manuscript still shows repetitive AI-like transition phrasing and needs a de-mechanized language pass.",
            }
        )
    return issues


def required_method_signals(domain: str) -> dict[str, list[str]]:
    common = {
        "experiment environment": ["实验环境", "运行环境", "平台", "硬件", "软件环境", "数据来源"],
        "metrics": ["评价指标", "指标", "准确率", "时延", "吞吐量", "内存", "F1", "RMSE", "AUC"],
        "commands or protocol": ["命令", "工具链", "脚本", "配置", "参数", "训练流程", "实验步骤"],
        "limitations": ["局限", "限制", "威胁分析", "重复测量", "误差", "偏差"],
    }
    if domain == "data-science":
        common["data split or leakage control"] = ["训练集", "验证集", "测试集", "交叉验证", "数据泄漏", "分层抽样"]
    return common


def get_section_body(manifest: dict, heading: str) -> str:
    for section in manifest.get("sections", []):
        if section.get("heading") == heading:
            return str(section.get("body", "")).strip()
    return ""


def count_severities(issues: list[dict]) -> dict[str, int]:
    counts = {"blocker": 0, "major": 0, "minor": 0}
    for issue in issues:
        severity = str(issue.get("severity", "minor"))
        counts.setdefault(severity, 0)
        counts[severity] += 1
    return counts


def contains_cjk(text: str) -> bool:
    return bool(CJK_RE.search(text))


def has_any_term(citation: dict, terms: list[str]) -> bool:
    haystack = " ".join(
        [
            str(citation.get("title", "")),
            str(citation.get("source", "")),
            str(citation.get("raw", "")),
            " ".join(str(item) for item in citation.get("keywords", []) if str(item).strip()),
            str(citation.get("abstract", "")),
        ]
    ).lower()
    return any(term.lower() in haystack for term in terms)


def is_relevant_reference(citation: dict, keywords: list[str]) -> bool:
    generic_terms = ["implementation", "实现", "experiment", "实验", "evaluation", "评估", "optimization", "优化", "system", "模型"]
    keyword_hits = sum(1 for term in keywords if term and has_any_term(citation, [term]))
    generic_hits = sum(1 for term in generic_terms if term and has_any_term(citation, [term]))
    return keyword_hits >= 2 or (keyword_hits >= 1 and generic_hits >= 1)


def is_absolute_path_text(value: str) -> bool:
    return value.startswith("/") or bool(WINDOWS_ABS_RE.match(value))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("thesis_spec_json")
    parser.add_argument("manifest_json")
    parser.add_argument("citation_bank_json")
    parser.add_argument("--figure-plan-json")
    parser.add_argument("--result-summaries-json")
    args = parser.parse_args()
    thesis_spec = json.loads(Path(args.thesis_spec_json).read_text(encoding="utf-8"))
    manifest = json.loads(Path(args.manifest_json).read_text(encoding="utf-8"))
    citation_bank = json.loads(Path(args.citation_bank_json).read_text(encoding="utf-8"))
    figure_plan = {}
    result_summaries = []
    if args.figure_plan_json:
        figure_plan = json.loads(Path(args.figure_plan_json).read_text(encoding="utf-8"))
    if args.result_summaries_json:
        payload = json.loads(Path(args.result_summaries_json).read_text(encoding="utf-8"))
        result_summaries = payload.get("summaries", payload)
    report = build_review_report(
        thesis_spec,
        manifest,
        citation_bank,
        figure_plan=figure_plan,
        result_summaries=result_summaries,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
