#!/usr/bin/env python3
"""Build a thesis spec from parsed source materials."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from thesis_utils import contains_chinese


KEYWORD_CANDIDATES = [
    "格密码",
    "后量子",
    "零知识证明",
    "Rust",
    "算法",
    "模型",
    "系统",
    "数据",
    "数据集",
    "实验",
    "仿真",
    "优化",
    "平台",
    "实现",
    "控制",
    "检测",
    "预测",
    "调度",
    "网络",
    "安全",
    "仿真",
]

PROFILE_TARGET_LEVELS = {
    "generic-stem": "undergraduate",
    "computing-thesis": "undergraduate",
}

QUESTION_SECTION_HINTS = [
    "研究内容",
    "研究方案",
    "关键问题",
    "研究目标",
    "拟解决",
    "创新点",
    "目的与意义",
]


def build_thesis_spec(parsed_documents: list[dict], profile_name: str = "generic-stem") -> dict:
    primary = parsed_documents[0] if parsed_documents else {"metadata": {"title": ""}, "text": "", "sections": {}}
    title = primary["metadata"].get("title") or "未命名论文"
    combined_text = "\n".join(item.get("text", "") for item in parsed_documents)
    primary_domain = detect_domain(title=title, text=combined_text)
    keywords = extract_keywords(title=title, text=combined_text)
    research_questions = build_research_questions(parsed_documents, primary_domain)
    target_level = PROFILE_TARGET_LEVELS.get(profile_name, "undergraduate")
    experiment_required = primary_domain in {"computing", "engineering", "data-science", "life-science"}
    return {
        "title": title,
        "profile": profile_name,
        "target_level": target_level,
        "language": "zh-CN" if contains_chinese(combined_text) else "en-US",
        "document_type": "thesis-manuscript",
        "completion_target": "final-thesis",
        "domain": {
            "primary": primary_domain,
            "secondary": secondary_domain(primary_domain),
        },
        "keywords": keywords,
        "research_questions": research_questions,
        "allow_simulated_experiments": False,
        "execution_requirements": {
            "requires_original_experiments": experiment_required,
            "requires_ai_written_or_executed_code": primary_domain == "computing",
            "runner_may_use_simulation_only_with_explicit_permission": True,
        },
        "source_materials": [item["metadata"]["source_name"] for item in parsed_documents],
        "reference_constraints": {
            "target_chinese_ratio": 0.35,
            "minimum_foreign_ratio": 0.33,
            "free_sources_first": True,
        },
        "required_artifacts": [
            "thesis_spec",
            "citation_bank",
            "experiment_plan",
            "figure_plan",
            "review_report",
            "docx_manifest",
        ],
    }


def detect_domain(title: str, text: str) -> str:
    corpus = f"{title}\n{text}".lower()
    if any(token in corpus for token in ["rust", "python", "c++", "java", "算法", "软件", "系统", "代码", "编译", "benchmark"]):
        return "computing"
    if any(token in corpus for token in ["模型", "数据集", "分类", "回归", "预测", "训练", "推理", "特征", "机器学习"]):
        return "data-science"
    if any(token in corpus for token in ["控制", "机械", "传感", "电机", "硬件", "装置", "工艺"]):
        return "engineering"
    if any(token in corpus for token in ["植物", "基因", "生态", "农业", "生物"]):
        return "life-science"
    return "generic-stem"


def extract_keywords(title: str, text: str) -> list[str]:
    found: list[str] = []
    corpus = f"{title}\n{text}"
    title_terms = [
        item.strip()
        for item in re.split(r"[，,：:（）()、/\-\s]+", title)
        if 2 <= len(item.strip()) <= 12 and item.strip() not in {"研究", "设计", "实现", "分析", "基于", "面向"}
    ]
    for keyword in title_terms:
        if keyword not in found:
            found.append(keyword)
    for keyword in KEYWORD_CANDIDATES:
        if keyword in corpus and keyword not in found:
            found.append(keyword)
    if not found:
        parts = [item for item in re.split(r"[^\w\u4e00-\u9fff]+", title) if len(item) >= 2]
        found.extend(parts[:4])
    return found[:6]


def build_research_questions(parsed_documents: list[dict], domain: str) -> list[str]:
    sections = parsed_documents[0].get("sections", {}) if parsed_documents else {}
    title = parsed_documents[0].get("metadata", {}).get("title", "") if parsed_documents else ""
    prompts: list[str] = []
    topic = normalize_topic_phrase(title)
    problem_clauses = extract_problem_clauses(sections)
    if problem_clauses:
        for clause in problem_clauses[:3]:
            prompts.append(clause_to_question(clause))
    if not prompts:
        if domain == "computing":
            prompts = [
                f"围绕“{topic}”，需要实现或改进的核心对象是什么，评价口径应如何界定？",
                f"围绕“{topic}”，应采用怎样的实现、算法或系统路径，并如何与基线方案比较？",
                f"围绕“{topic}”，哪些实验能够支撑对性能、资源消耗与适用边界的结论？",
            ]
        elif domain == "data-science":
            prompts = [
                f"围绕“{topic}”，研究对象、数据范围与预测或判别目标应如何界定？",
                f"围绕“{topic}”，应采用怎样的特征、模型或训练策略，并如何与基线方法比较？",
                f"围绕“{topic}”，哪些评估设计能够避免数据泄漏并支撑最终结论？",
            ]
        else:
            prompts = [
                f"围绕“{topic}”，本文试图解决的核心问题是什么？",
                f"围绕“{topic}”，哪些方法或方案值得比较，比较标准是什么？",
                f"围绕“{topic}”，哪些证据足以支撑最终结论，哪些结论必须保持谨慎？",
            ]
    deduped: list[str] = []
    for prompt in prompts:
        if prompt not in deduped:
            deduped.append(prompt)
    return deduped[:4]


def secondary_domain(primary_domain: str) -> str:
    mapping = {
        "computing": "software-research",
        "data-science": "data-driven-research",
        "engineering": "engineering-research",
        "life-science": "life-science-research",
    }
    return mapping.get(primary_domain, "generic-stem")


def normalize_topic_phrase(title: str) -> str:
    cleaned = re.sub(r"[\s]+", "", str(title or ""))
    cleaned = re.sub(r"^(关于|面向|基于)", "", cleaned)
    cleaned = re.sub(r"(研究|设计|实现|分析|优化)$", "", cleaned)
    return cleaned or "当前研究主题"


def extract_problem_clauses(sections: dict[str, str]) -> list[str]:
    clauses: list[str] = []
    for heading, body in sections.items():
        if not any(hint in heading for hint in QUESTION_SECTION_HINTS):
            continue
        for chunk in re.split(r"[。；;\n]", body):
            sentence = chunk.strip("，、:： ")
            if len(sentence) < 10:
                continue
            if any(token in sentence for token in ["本文", "本课题", "本研究", "拟", "计划"]) and len(sentence) < 18:
                continue
            clauses.append(sentence)
    return clauses


def clause_to_question(clause: str) -> str:
    clause = clause.strip()
    clause = re.sub(r"^(本文|本研究|本课题)(围绕|拟|将|主要)?", "", clause).strip("，、:： ")
    if clause.startswith("如何"):
        return clause.rstrip("。；;") + "？"
    return f"如何{clause.rstrip('。；;') }？"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("parsed_json", nargs="+")
    parser.add_argument("--profile", default="generic-stem")
    args = parser.parse_args()
    parsed_documents = [
        json.loads(Path(path).read_text(encoding="utf-8"))
        for path in args.parsed_json
    ]
    print(json.dumps(build_thesis_spec(parsed_documents, args.profile), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
