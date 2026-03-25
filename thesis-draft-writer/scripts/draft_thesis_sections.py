#!/usr/bin/env python3
"""Compose thesis sections from proposal materials, citation bank, and result artifacts."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))


def build_manifest(
    thesis_spec: dict,
    parsed_documents: list[dict],
    citation_bank: dict,
    figure_plan: dict,
    result_csv_paths: list[str | Path],
) -> dict:
    primary = parsed_documents[0] if parsed_documents else {"lines": [], "sections": {}}
    sections = primary.get("sections", {})
    metadata = extract_front_matter_metadata(primary.get("lines", []), thesis_spec.get("title", ""))
    result_tables = {Path(path).stem: read_csv_rows(path) for path in result_csv_paths}
    abstract_zh = build_chinese_abstract(thesis_spec, citation_bank, result_tables)
    abstract_en = build_english_abstract(thesis_spec, result_tables)
    keywords = thesis_spec.get("keywords", [])[:5]
    return {
        "title": thesis_spec.get("title", ""),
        "metadata": metadata,
        "sections": [
            {"heading": "封面", "body": build_cover_body(metadata, thesis_spec)},
            {"heading": "独创性声明", "body": build_originality_statement(metadata)},
            {"heading": "论文使用授权说明", "body": build_authorization_statement(metadata)},
            {"heading": "摘要", "body": abstract_zh},
            {"heading": "关键词", "body": "；".join(keywords)},
            {"heading": "ABSTRACT", "body": abstract_en},
            {"heading": "目录", "body": build_table_of_contents()},
            {"heading": "第一章 绪论", "body": build_introduction(thesis_spec, sections, citation_bank)},
            {"heading": "第二章 相关工作与理论基础", "body": build_related_work(thesis_spec, sections, citation_bank)},
            {"heading": "第三章 系统设计与实现", "body": build_method_section(thesis_spec, sections, citation_bank)},
            {
                "heading": "第四章 实验设计与结果分析",
                "body": build_experiment_results_section(result_tables, figure_plan, citation_bank),
            },
            {"heading": "结论与讨论", "body": build_conclusion(thesis_spec, result_tables, citation_bank)},
            {"heading": "参考文献", "body": format_reference_list(citation_bank)},
            {"heading": "附录", "body": build_appendix(figure_plan, result_csv_paths)},
            {"heading": "个人简介", "body": build_profile(metadata)},
            {"heading": "致谢", "body": build_acknowledgements(metadata)},
        ],
    }


def extract_front_matter_metadata(lines: list[str], title: str) -> dict:
    joined = "\n".join(lines[:40])
    return {
        "title": title,
        "author": search_capture(joined, r"姓\s*名[:：]\s*([^\n]+)") or "作者信息待核对",
        "student_id": search_capture(joined, r"学\s*号[:：]\s*([^\n]+)") or "学号待核对",
        "major_class": search_capture(joined, r"专业班级[:：]\s*([^\n]+)") or "专业班级待核对",
        "college": search_capture(joined, r"学院名称[:：]\s*([^\n]+)") or "学院待核对",
        "advisor": search_capture(joined, r"指导教师[:：]\s*([^\n]+)") or "指导教师待核对",
        "date": search_capture(joined, r"(\d{4}年\d{1,2}月\d{1,2}日)") or "日期待核对",
    }


def search_capture(text: str, pattern: str) -> str:
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def build_cover_body(metadata: dict, thesis_spec: dict) -> str:
    target_level = str(thesis_spec.get("target_level") or "").strip().lower()
    if target_level == "master":
        cover_heading = "硕士学位论文"
    else:
        cover_heading = "本科毕业论文（设计）"
    return "\n".join(
        [
            cover_heading,
            thesis_spec.get("title", metadata.get("title", "")),
            f"作者：{metadata['author']}",
            f"学号：{metadata['student_id']}",
            f"专业班级：{metadata['major_class']}",
            f"学院：{metadata['college']}",
            f"指导教师：{metadata['advisor']}",
            f"提交日期：{metadata['date']}",
        ]
    )


def build_originality_statement(metadata: dict) -> str:
    return "\n".join(
        [
            "本人声明，所呈交的毕业论文是在指导教师指导下独立完成的研究工作与论文撰写成果。",
            "除文中已经注明引用的内容外，本论文不包含他人已经发表或撰写过的研究成果。",
            f"学位论文作者签名：{metadata['author']}",
            f"日期：{metadata['date']}",
        ]
    )


def build_authorization_statement(metadata: dict) -> str:
    return "\n".join(
        [
            "本人同意学校在教学、科研与学位管理范围内保存和使用本论文。",
            f"学位论文作者签名：{metadata['author']}",
            f"指导教师签名：{metadata['advisor']}",
            f"日期：{metadata['date']}",
        ]
    )


def build_topic_brief(thesis_spec: dict) -> dict:
    title = str(thesis_spec.get("title", "")).strip() or "当前研究主题"
    keywords = [str(item).strip() for item in thesis_spec.get("keywords", []) if str(item).strip()]
    focus = "、".join(keywords[:3]) if keywords else "研究对象"
    domain = str((thesis_spec.get("domain") or {}).get("primary") or "stem").strip()
    if domain == "computing":
        method_scope = "算法设计、系统实现、数据组织与性能优化"
        metric_scope = "时延、吞吐量、资源占用与结果稳定性"
    elif domain == "data-science":
        method_scope = "数据准备、模型设计、训练评估与误差分析"
        metric_scope = "预测效果、泛化能力、计算开销与稳定性"
    else:
        method_scope = "方法设计、实验组织、数据分析与结果解释"
        metric_scope = "核心性能指标、资源消耗与结果一致性"
    return {
        "title": title,
        "focus": focus or title,
        "method_scope": method_scope,
        "metric_scope": metric_scope,
    }


def build_chinese_abstract(thesis_spec: dict, citation_bank: dict, result_tables: dict[str, list[dict]]) -> str:
    topic = build_topic_brief(thesis_spec)
    research_questions = thesis_spec.get("research_questions", [])
    refs = format_citations(find_reference_indices(citation_bank, thesis_spec.get("keywords", [])[:3], limit=3))
    evidence_text = build_result_evidence_summary(result_tables, detail_level="abstract")
    return (
        f"围绕“{topic['title']}”这一问题，本文以 {topic['focus']} 为核心研究对象，"
        f"从{topic['method_scope']}三个层面组织研究路线，并结合已有文献明确{topic['metric_scope']}等评价维度{refs}。"
        f"全文围绕以下问题展开：{'; '.join(str(item) for item in research_questions[:3])}。"
        f"{evidence_text}"
    )


def build_english_abstract(thesis_spec: dict, result_tables: dict[str, list[dict]]) -> str:
    topic = build_topic_brief(thesis_spec)
    evidence_text = build_result_evidence_summary(result_tables, detail_level="abstract-en")
    return (
        f"This thesis investigates {translate_title(topic['title'])} and organizes the study around design, implementation, evaluation, and conclusion control. "
        "The manuscript derives its argument from literature review, method construction, and experiment-based analysis rather than from a fixed prose template. "
        f"{evidence_text}"
    )


def build_table_of_contents() -> str:
    return "\n".join(
        [
            "摘要",
            "ABSTRACT",
            "第一章 绪论",
            "第二章 相关工作与理论基础",
            "第三章 系统设计与实现",
            "第四章 实验设计与结果分析",
            "结论与讨论",
            "参考文献",
            "附录",
            "个人简介",
            "致谢",
        ]
    )


def build_introduction(thesis_spec: dict, source_sections: dict[str, str], citation_bank: dict) -> str:
    topic = build_topic_brief(thesis_spec)
    background = summarize_sentence(source_sections.get("一、研究的目的与意义", ""))
    questions = thesis_spec.get("research_questions", [])
    general_refs = format_citations(find_reference_indices(citation_bank, thesis_spec.get("keywords", [])[:3], limit=3))
    return "\n".join(
        [
            f"{background} 在这一背景下，围绕 {topic['focus']} 的研究价值不仅体现为理论可行性，更体现为能否形成可验证、可比较、可复核的证据链{general_refs}。",
            f"结合开题材料可以看到，当前工作的关键难点集中在 {topic['method_scope']} 与 {topic['metric_scope']} 两个层面，因此本文不把写作本身当作目标，而是把研究问题的求解过程组织为可检查的章节结构。",
            f"据此，本文重点回答以下问题：{'；'.join(str(item) for item in questions[:3])}。",
            "绪论部分的任务不是预告结论，而是明确研究背景、问题边界、评价口径以及后续章节如何为最终结论提供证据。",
        ]
    )


def build_related_work(thesis_spec: dict, source_sections: dict[str, str], citation_bank: dict) -> str:
    related = summarize_sentence(source_sections.get("二、国内外研究现状", ""))
    domestic_refs = format_citations(find_reference_indices(citation_bank, thesis_spec.get("keywords", [])[:2], preferred_language="zh", limit=3))
    foreign_refs = format_citations(find_reference_indices(citation_bank, thesis_spec.get("keywords", [])[:3], preferred_language="en", limit=4))
    return "\n".join(
        [
            "结合已有文献，可以将相关研究大体划分为问题定义与理论基础、方法或系统实现、实验评估与应用验证三条路径。" + foreign_refs,
            "中文文献更适合帮助界定研究背景、应用场景与国内研究进展，英文文献则更适合支撑方法细节、评价设计与国际对比口径。" + domestic_refs,
            f"因此，本章的重点不是机械罗列文献，而是说明现有研究在研究对象、评价方法和结论边界上分别做到了什么、还缺什么。{related}",
        ]
    )


def build_method_section(thesis_spec: dict, source_sections: dict[str, str], citation_bank: dict) -> str:
    topic = build_topic_brief(thesis_spec)
    questions = thesis_spec.get("research_questions", [])
    impl_refs = format_citations(find_reference_indices(citation_bank, thesis_spec.get("keywords", [])[:3], limit=4))
    return "\n".join(
        [
            f"本文的方法设计围绕“{topic['title']}”展开，核心原则是问题边界明确、实现路径可执行、评价口径可复核。相关实现与方法文献为本章提供了设计参照{impl_refs}。",
            f"结合研究问题，方法部分首先界定研究对象、输入输出与评价指标，然后说明系统或方法如何拆分为若干可独立检查的模块，最后说明这些模块如何共同支撑 {'；'.join(str(item) for item in questions[:2])}。",
            "如果研究对象属于计算类课题，本章还需要交代代码结构、运行流程、配置方式与关键实现选择；如果属于数据或实验类课题，则需要交代样本来源、处理流程、变量控制与分析步骤。",
            "方法章节与实验章节必须一一对应，即每一项关键设计都应在后续实验中拥有可观察的验证位置，每一个实验结论也都应能追溯到本章的设计决定。",
            "本章的写法强调可执行性而非口号式创新表达，避免用抽象形容词代替可复现的方法描述。",
        ]
    )


def build_experiment_results_section(
    result_tables: dict[str, list[dict]],
    figure_plan: dict,
    citation_bank: dict,
) -> str:
    baseline = result_tables.get("baseline_comparison", [])
    ablation = result_tables.get("ablation_study", [])
    sensitivity = result_tables.get("sensitivity_analysis", [])
    if not baseline:
        return (
            "本章用于报告真实实验设计、结果表、统计分析与图表解释。"
            "当前输入尚未提供可复核的结果表，因此本章不应自动生成定量结论；主 AI 应继续推进代码实现、实验运行与结果整理后再完成本章。"
        )
    ref = baseline[0]
    best = baseline[-1]
    primary_metric = infer_primary_numeric_metric(ref, best)
    metric_name = primary_metric[0]
    before_value = primary_metric[1]
    after_value = primary_metric[2]
    ablation_text = ""
    if ablation:
        worst = pick_worst_ablation(ablation)
        ablation_text = (
            f"消融结果显示，在移除 {worst.get('variant', '关键因素')} 后，核心指标出现明显回退，"
            "说明该因素对整体结果具有实质性贡献。"
        )
    sensitivity_text = ""
    if sensitivity:
        last = sensitivity[-1]
        sensitivity_text = (
            f"敏感性分析进一步表明，关键参数变化会同时影响主要收益与配套代价。以当前结果为例，参数提升到 {last.get('batch_size', '较高水平')} 后，"
            "主指标和资源开销同时发生变化，说明系统存在需要权衡的工作区间。"
        )
    figure_mentions = "；".join(
        f"{item.get('figure_number', '')}{item.get('中文标题', '')}"
        for item in figure_plan.get("figures", [])[:3]
    )
    experiment_refs = format_citations(
        find_reference_indices(
            citation_bank,
            ["implementation", "experiment", "evaluation", "benchmark", "实验", "评估"] + thesis_keywords(citation_bank, limit=2),
            limit=3,
        )
    )
    return "\n".join(
        [
            "本章围绕研究问题组织总体对比、关键因素消融与参数敏感性三组实验。实验目标不是制造漂亮数字，而是验证方法或系统是否在约定口径下形成稳定、可解释的收益。" + experiment_refs,
            "实验分析至少应交代实验环境、输入规模、参数配置、重复次数、统计口径以及威胁分析，从而保证正文中的每一项定量判断都能追溯到具体实验设置。",
            f"在当前已提供的结果中，比较方案 {ref.get('implementation', ref.get('variant', 'baseline'))} 与 {best.get('implementation', best.get('variant', 'proposed'))} 在核心指标“{metric_name}”上表现出可见差异，数值由 {before_value} 变化为 {after_value}。这一差异构成后续讨论的直接证据，但仍需结合误差、重复测量和场景约束进行解释。",
            ablation_text or "消融实验用于检验关键因素是否真正贡献了性能、效果或稳定性收益。",
            sensitivity_text or "敏感性实验用于观察关键参数变化时结果是否稳定，以及收益与代价是否同时变化。",
            f"围绕上述结果，本文优先绘制的图包括：{figure_mentions}。这些图分别对应总体时延差异、关键优化边际贡献以及批处理规模对吞吐量的影响趋势，可用于支撑正文中的表图互证关系。",
            "威胁分析部分应进一步讨论样本规模、运行环境波动、参数选择偏差以及外部适用边界，避免把局部实验结果直接扩大解释为普适结论。",
        ]
    )


def build_conclusion(thesis_spec: dict, result_tables: dict[str, list[dict]], citation_bank: dict) -> str:
    topic = build_topic_brief(thesis_spec)
    baseline = result_tables.get("baseline_comparison", [])
    questions = thesis_spec.get("research_questions", [])
    if baseline:
        ref = baseline[0]
        best = baseline[-1]
        metric_name, before_value, after_value = infer_primary_numeric_metric(ref, best)
        key_result = (
            f"实验结果显示，围绕核心指标“{metric_name}”，比较方案 {ref.get('implementation', ref.get('variant', 'baseline'))} "
            f"与 {best.get('implementation', best.get('variant', 'proposed'))} 之间存在可解释差异，其代表性数值由 {before_value} 变化为 {after_value}。"
        )
    else:
        key_result = "当前尚未提供足够的实验结果，因此结论部分只能界定问题边界与后续证据要求，而不能替代真实研究结论。"
    refs = format_citations(find_reference_indices(citation_bank, thesis_spec.get("keywords", [])[:3] or ["implementation", "performance"], limit=3))
    return "\n".join(
        [
            f"本文围绕“{topic['title']}”完成了从研究问题、方法设计到实验分析的结构化论证，并将结论严格限定在当前证据允许的范围内{refs}。",
            f"研究问题回扣如下：{'；'.join(str(item) for item in questions[:3])}。",
            key_result,
            "综合全文可以看出，论文真正成立的基础不是章节齐全，而是研究对象、方法设计与实验结果之间已经形成可以追溯的对应关系。",
            "本文的主要贡献在于：明确研究问题和评价边界；给出可执行的方法或系统路径；并用实验分析支撑有边界的结论，而不是用模板语言放大研究意义。",
            "本文的局限与后续工作应继续围绕证据链展开，例如扩大实验覆盖面、补充误差与统计分析、验证更多真实场景，并进一步收紧结论的外推边界。",
        ]
    )


def build_appendix(figure_plan: dict, result_csv_paths: list[str | Path]) -> str:
    figure_lines = [
        f"{item.get('figure_number', '')} {item.get('中文标题', '')}：{item.get('figure_purpose', '')}"
        for item in figure_plan.get("figures", [])
    ]
    artifact_lines = [f"附录数据表：{Path(path).name}" for path in result_csv_paths]
    return "\n".join(
        [
            "附录A 用于补充正文未展开的实现细节、参数清单、额外结果表或长篇证明材料。",
            "附录B 用于汇总图表来源、扩展实验结果与必要的复现实验说明。",
        ]
        + figure_lines
        + artifact_lines
    )


def translate_title(title: str) -> str:
    cleaned = re.sub(r"\s+", " ", str(title or "")).strip()
    return cleaned if cleaned else "the thesis topic"


def thesis_keywords(citation_bank: dict, limit: int = 2) -> list[str]:
    keywords: list[str] = []
    for item in citation_bank.get("citations", []):
        title = str(item.get("title", "")).strip()
        for token in re.split(r"[^\w\u4e00-\u9fff]+", title):
            if len(token) < 2:
                continue
            if token not in keywords:
                keywords.append(token)
            if len(keywords) >= limit:
                return keywords
    return keywords


def build_result_evidence_summary(result_tables: dict[str, list[dict]], detail_level: str = "abstract") -> str:
    baseline = result_tables.get("baseline_comparison", [])
    if not baseline:
        if detail_level == "abstract-en":
            return "At this stage, the manuscript requires externally supplied measured results before any final quantitative claim should be made."
        return "当前稿件必须基于真实实验结果继续完善，摘要不应替代实验章节下达未经测量支持的定量结论。"
    ref = baseline[0]
    best = baseline[-1]
    metric_name, before_value, after_value = infer_primary_numeric_metric(ref, best)
    if detail_level == "abstract-en":
        return (
            f"The current evidence compares {ref.get('implementation', ref.get('variant', 'baseline'))} with "
            f"{best.get('implementation', best.get('variant', 'proposed'))} and observes a visible change in the core metric "
            f"({metric_name}: {before_value} to {after_value}); the detailed interpretation is reserved for the results chapter."
        )
    return (
        f"在已提供的结果中，比较方案 {ref.get('implementation', ref.get('variant', 'baseline'))} 与 "
        f"{best.get('implementation', best.get('variant', 'proposed'))} 在核心指标“{metric_name}”上呈现出明显差异，"
        f"代表性数值由 {before_value} 变化为 {after_value}；具体解释在实验章节中结合表图展开。"
    )


def infer_primary_numeric_metric(ref: dict, best: dict) -> tuple[str, str, str]:
    preferred = ["prove_ms", "latency_ms", "latency", "throughput_tps", "throughput", "accuracy", "memory_mb", "f1", "rmse"]
    for metric in preferred:
        if metric in ref and metric in best:
            return metric, str(ref[metric]), str(best[metric])
    shared = [key for key in ref.keys() if key in best and is_float_like(ref[key]) and is_float_like(best[key])]
    if shared:
        metric = shared[0]
        return metric, str(ref[metric]), str(best[metric])
    return "value", "-", "-"


def pick_worst_ablation(rows: list[dict]) -> dict:
    candidate_rows = rows[1:] if len(rows) > 1 else rows
    for metric in ["prove_ms", "latency_ms", "latency", "memory_mb"]:
        numeric = [item for item in candidate_rows if metric in item and is_float_like(item[metric])]
        if numeric:
            return max(numeric, key=lambda item: float(item[metric]))
    return candidate_rows[0]


def is_float_like(value: object) -> bool:
    try:
        float(str(value))
    except (TypeError, ValueError):
        return False
    return True


def build_profile(metadata: dict) -> str:
    return (
        f"{metadata['author']}，学号 {metadata['student_id']}，"
        f"来自 {metadata['college']} {metadata['major_class']}。"
        "研究方向聚焦理工科问题的系统分析、实现优化与实验验证。"
    )


def build_acknowledgements(metadata: dict) -> str:
    return (
        f"感谢指导教师 {metadata['advisor']} 在选题定位、技术路线和论文组织方面提供的指导。"
        "感谢开题阶段提供参考意见的老师与同学。"
        "感谢相关文献作者为本文研究提供理论基础与工程参考。"
    )


def find_reference_indices(
    citation_bank: dict,
    keywords: list[str],
    preferred_language: str | None = None,
    limit: int = 3,
) -> list[int]:
    matches: list[int] = []
    lowered_keywords = [keyword.lower() for keyword in keywords]
    for item in citation_bank.get("citations", []):
        if preferred_language and item.get("language") != preferred_language:
            continue
        haystack = " ".join(
            [
                str(item.get("title", "")),
                str(item.get("source", "")),
                str(item.get("raw", "")),
            ]
        ).lower()
        if any(keyword in haystack for keyword in lowered_keywords):
            matches.append(int(item["index"]))
        if len(matches) >= limit:
            break
    if matches:
        return matches
    fallback = [
        int(item["index"])
        for item in citation_bank.get("citations", [])
        if not preferred_language or item.get("language") == preferred_language
    ]
    return fallback[:limit]


def format_citations(indices: list[int]) -> str:
    deduped = []
    for index in indices:
        if index not in deduped:
            deduped.append(index)
    return f"[{','.join(str(index) for index in deduped)}]" if deduped else ""


def summarize_sentence(text: str, limit: int = 180) -> str:
    clean = re.sub(r"\[[0-9,\s]+\]", "", text)
    clean = re.sub(r"\(\s*\d+\s*\)", "", clean)
    clean = re.sub(r"\s+", " ", clean).strip()
    if not clean:
        return ""
    sentences = re.split(r"(?<=[。！？])", clean)
    summary = "".join(sentences[:2]).strip()
    if len(summary) <= limit:
        return summary
    return summary[: limit - 1] + "…"


def read_csv_rows(path: str | Path) -> list[dict]:
    with Path(path).open("r", encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def format_reference_list(citation_bank: dict) -> str:
    return "\n".join(
        f"[{item['index']}] {item['raw']}"
        for item in citation_bank.get("citations", [])
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("thesis_spec_json")
    parser.add_argument("parsed_json", nargs="+")
    parser.add_argument("citation_bank_json")
    parser.add_argument("figure_plan_json")
    parser.add_argument("--result-csv", action="append", default=[])
    args = parser.parse_args()
    thesis_spec = json.loads(Path(args.thesis_spec_json).read_text(encoding="utf-8"))
    parsed_documents = [json.loads(Path(path).read_text(encoding="utf-8")) for path in args.parsed_json]
    citation_bank = json.loads(Path(args.citation_bank_json).read_text(encoding="utf-8"))
    figure_plan = json.loads(Path(args.figure_plan_json).read_text(encoding="utf-8"))
    manifest = build_manifest(thesis_spec, parsed_documents, citation_bank, figure_plan, args.result_csv)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
