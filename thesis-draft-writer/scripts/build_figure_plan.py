#!/usr/bin/env python3
"""Build a lightweight figure plan from experiment plans and result summaries."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import summarize_results


METRIC_LABELS_ZH = {
    "latency": "时延",
    "latency_ms": "时延",
    "throughput": "吞吐量",
    "memory_mb": "内存占用",
    "accuracy": "准确率",
    "quality_score": "质量得分",
}

METRIC_LABELS_EN = {
    "latency": "Latency",
    "latency_ms": "Latency",
    "throughput": "Throughput",
    "memory_mb": "Memory",
    "accuracy": "Accuracy",
    "quality_score": "Quality Score",
}

METRIC_CHART_TYPES = {
    "latency": "bar",
    "latency_ms": "bar",
    "throughput": "bar",
    "memory_mb": "bar",
    "accuracy": "line",
    "quality_score": "line",
}


def build_figure_plan(
    thesis_spec: dict,
    experiment_plan: dict,
    result_summaries: list[dict] | None = None,
) -> dict:
    figures = figures_from_result_summaries(result_summaries or [])
    if not figures:
        figures = figures_from_experiment_plan(experiment_plan)
    for index, figure in enumerate(figures, start=1):
        figure.setdefault("figure_number", f"图{index}")
    return {
        "title": thesis_spec.get("title", ""),
        "domain": thesis_spec.get("domain", {}).get("primary") or experiment_plan.get("domain", "generic-stem"),
        "figures": figures,
    }


def figures_from_experiment_plan(experiment_plan: dict) -> list[dict]:
    figures: list[dict] = []
    for experiment in experiment_plan.get("experiments", []):
        metric = pick_primary_metric(experiment.get("metrics", []))
        metric_zh = METRIC_LABELS_ZH.get(metric, metric)
        metric_en = METRIC_LABELS_EN.get(metric, metric.replace("_", " ").title())
        prompt_bundle = build_prompt_bundle(
            source_hint=f"{experiment.get('name', 'experiment')} 的实验结果表",
            metric_zh=metric_zh,
            chart_type=METRIC_CHART_TYPES.get(metric, "bar"),
            figure_title=f"{experiment.get('name', '实验')}的{metric_zh}对比图",
            figure_purpose=experiment.get("goal", "展示实验结果。"),
        )
        figures.append(
            {
                "中文标题": f"{experiment.get('name', '实验')}的{metric_zh}对比图",
                "英文标题": f"{metric_en} Analysis for {experiment.get('name', 'Experiment')}",
                "figure_purpose": experiment.get("goal", "展示实验结果。"),
                "source_data": f"{experiment.get('name', 'experiment')} 的实验结果表",
                "target_chapter": "第四章 实验设计与结果分析",
                "notes": "优先展示 proposed 与 baseline/ablation 的相对差异，并在图注中注明硬件与参数设置。",
                "chart_type": METRIC_CHART_TYPES.get(metric, "bar"),
                "metric": metric,
                "prompt_placeholder": prompt_bundle["image_prompt"],
                "image_prompt": prompt_bundle["image_prompt"],
                "negative_prompt": prompt_bundle["negative_prompt"],
                "render_spec": prompt_bundle["render_spec"],
            }
        )
    return figures


def figures_from_result_summaries(result_summaries: list[dict]) -> list[dict]:
    figures: list[dict] = []
    for summary in result_summaries:
        source_data = summary.get("source_file", "results.csv")
        source_name = Path(source_data).name
        stem = Path(source_data).stem
        for spec in figure_specs_for_source(stem):
            metric = spec["metric"]
            metric_zh = METRIC_LABELS_ZH.get(metric, metric)
            prompt_bundle = build_prompt_bundle(
                source_hint=source_name,
                metric_zh=metric_zh,
                chart_type=spec["chart_type"],
                figure_title=spec["title_zh"],
                figure_purpose=spec["purpose"],
            )
            figures.append(
                {
                    "中文标题": spec["title_zh"],
                    "英文标题": spec["title_en"],
                    "figure_purpose": spec["purpose"],
                    "source_data": source_name,
                    "target_chapter": "第四章 实验设计与结果分析",
                    "notes": spec["notes"],
                    "chart_type": spec["chart_type"],
                    "metric": metric,
                    "prompt_placeholder": prompt_bundle["image_prompt"],
                    "image_prompt": prompt_bundle["image_prompt"],
                    "negative_prompt": prompt_bundle["negative_prompt"],
                    "render_spec": prompt_bundle["render_spec"],
                }
            )
    return figures


def figure_specs_for_source(stem: str) -> list[dict]:
    if stem == "baseline_comparison":
        return [
            {
                "metric": "latency_ms",
                "title_zh": "核心指标总体对比图",
                "title_en": "Overall Core Metric Comparison",
                "purpose": "展示不同方案在核心性能指标上的总体差异。",
                "chart_type": "bar",
                "notes": "横轴为比较方案，纵轴为核心指标，图注中应说明实验对象、环境与统计口径。",
            }
        ]
    if stem == "ablation_study":
        return [
            {
                "metric": "latency_ms",
                "title_zh": "关键因素消融效果图",
                "title_en": "Ablation Impact on the Core Metric",
                "purpose": "展示关键因素移除后对核心指标的影响。",
                "chart_type": "bar",
                "notes": "应突出各因素的边际贡献，并在图注中明确消融设置和控制变量。",
            }
        ]
    if stem == "sensitivity_analysis":
        return [
            {
                "metric": "throughput",
                "title_zh": "关键参数敏感性趋势图",
                "title_en": "Sensitivity Trend under Different Parameter Settings",
                "purpose": "展示关键参数变化对主要结果指标的影响趋势。",
                "chart_type": "line",
                "notes": "横轴为关键参数，纵轴为核心指标，并在图注中说明伴随变化的代价或约束。",
            }
        ]
    return []


def build_prompt_bundle(
    source_hint: str,
    metric_zh: str,
    chart_type: str,
    figure_title: str,
    figure_purpose: str,
) -> dict:
    chart_type_zh = {
        "bar": "柱状图",
        "line": "折线图",
        "table": "表格式统计图",
    }.get(chart_type, "学术统计图")
    image_prompt = (
        f"请生成一张适用于中文 STEM 学位论文的{chart_type_zh}，图题为“{figure_title}”。"
        f"该图用于{figure_purpose}。数据来源提示：{source_hint}。"
        f"视觉风格要求：白色背景、二维平面、中文坐标轴与中文图例、黑灰主色配一组克制的学术蓝色点缀、排版紧凑、适合直接放入论文正文。"
        "请明确预留图题、误差线、显著性标记、单位标注和图注区域。"
        f"重点突出“{metric_zh}”这一指标在 baseline、optimized、ablation 等方案之间的差异。"
        "不要臆造不存在的数据点、类别、实验结论或夸张视觉元素；如果无法精确还原数值，就输出严格按占位结构组织的学术图形草图。"
    )
    negative_prompt = (
        "禁止三维效果、渐变炫光、卡通插画、照片质感、科幻背景、营销海报风、大面积高饱和配色、英文界面按钮、无关图标、人物、动物、随意添加的数据标签。"
    )
    render_spec = {
        "aspect_ratio": "4:3",
        "preferred_background": "white",
        "label_language": "zh-CN",
        "style_keywords": ["academic", "clean", "2d", "thesis-ready"],
        "data_policy": "Do not invent missing measurements; preserve placeholders if exact values are unavailable.",
    }
    return {
        "image_prompt": image_prompt,
        "negative_prompt": negative_prompt,
        "render_spec": render_spec,
    }


def pick_primary_metric(metrics: list[str]) -> str:
    for metric in ["latency_ms", "latency", "accuracy", "throughput", "memory_mb", "quality_score"]:
        if metric in metrics:
            return metric
    return metrics[0] if metrics else "value"


def discover_result_csvs(
    source_paths: list[str | Path],
    extra_dirs: list[str | Path] | None = None,
) -> list[Path]:
    candidates: list[Path] = []
    seen: set[Path] = set()
    search_dirs = [Path.cwd() / "results", Path.cwd() / "experiment_results"]
    for source_path in source_paths:
        base = Path(source_path).resolve().parent
        search_dirs.extend([base / "results", base / "experiment_results"])
    for extra_dir in extra_dirs or []:
        search_dirs.append(Path(extra_dir))
    for directory in search_dirs:
        if not directory.exists() or not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.csv")):
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            candidates.append(resolved)
    return candidates


def load_result_summaries(csv_paths: list[str | Path]) -> list[dict]:
    summaries = []
    for csv_path in csv_paths:
        summary = summarize_results.summarize_csv(csv_path)
        summary["source_file"] = str(Path(csv_path))
        summaries.append(summary)
    return summaries


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("thesis_spec_json")
    parser.add_argument("experiment_plan_json")
    parser.add_argument("--result-summary-json", action="append", default=[])
    args = parser.parse_args()
    thesis_spec = json.loads(Path(args.thesis_spec_json).read_text(encoding="utf-8"))
    experiment_plan = json.loads(Path(args.experiment_plan_json).read_text(encoding="utf-8"))
    result_summaries = [
        json.loads(Path(path).read_text(encoding="utf-8"))
        for path in args.result_summary_json
    ]
    print(json.dumps(build_figure_plan(thesis_spec, experiment_plan, result_summaries), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
