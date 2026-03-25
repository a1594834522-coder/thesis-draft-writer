# Figure Image Prompts

Use these only as prompt templates or placeholders for external image models. The thesis author is still responsible for checking whether the resulting figure matches the actual data and argument.

## Core Rule

- Prefer data-faithful charts over decorative images.
- Do not ask the model to invent measurements, categories, or conclusions.
- If exact plotting is not possible, ask for a thesis-ready layout mockup that preserves placeholders clearly.

## 1. Data Chart Prompt

```text
请生成一张适用于中文 STEM 学位论文的二维学术图表，图题为“{figure_title}”。
该图用于{figure_purpose}。
数据来源提示：{source_hint}。
图表类型：{chart_type_zh}。
视觉要求：白色背景、中文坐标轴与中文图例、字体清晰、线条克制、适合论文排版、不要海报化设计。
内容要求：突出 {metric_zh} 指标在 baseline、proposed、ablation 或不同参数组之间的差异，预留误差线、显著性标记、单位标注和图注区域。
约束：不要臆造不存在的数据点、类别、方法名或实验结论；如果无法精确还原数值，就输出结构准确的论文图表草图而不是伪造精确统计图。
```

## 2. System Diagram Prompt

```text
请生成一张适用于中文 STEM 学位论文的系统结构图，主题为“{figure_title}”。
目的：{figure_purpose}。
内容要求：仅展示论文中已经出现的模块、数据流和交互关系，结构层次清楚，箭头方向明确，中文标注统一。
视觉要求：白底、二维扁平、低饱和配色、线框与色块克制、适合论文黑白打印后仍能辨识。
约束：不要加入正文未定义的新模块、不要使用产品海报风、不要出现人物、照片、设备写实纹理。
```

## 3. Negative Prompt

```text
禁止三维效果、夸张透视、霓虹渐变、海报风、UI 截图风、卡通图标堆砌、人物或动物、英文界面元素、与论文无关的装饰纹理、随意捏造的数据标签。
```

## 4. Review Checklist

- 图题、坐标轴、图例语言是否与论文一致
- 图中类别、方法名、指标名是否与正文和实验数据一致
- 是否存在模型臆造的新数据、新模块或过强结论
- 黑白打印后是否仍可辨识
