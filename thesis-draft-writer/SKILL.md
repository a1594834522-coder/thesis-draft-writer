---
name: thesis-draft-writer
description: Use when the user wants a Chinese STEM thesis manuscript, literature search, experiment planning or execution, chart planning, thesis review, or DOCX assembly, especially for computing, data, algorithms, systems, simulation, and public-dataset driven topics.
metadata:
  short-description: Research-driven final thesis delivery
---

# Thesis Draft Writer

<EXTREMELY-IMPORTANT>
For proposal-driven or experiment-capable theses, the following are non-negotiable:

1. If the thesis path comes from a proposal, you MUST run the Proposal Challenge Gate before normal execution.
2. If a paper will shape method choice, experiment design, or final claims, you MUST fully read that paper before treating it as understood evidence.
3. If the topic is experiment-capable, you MUST produce at least one real experiment artifact before outputting a full thesis draft or final `docx`.
4. If a review or investigation task is independent, sidecar, and not on the immediate critical path, use real fresh-context subagents instead of silent self-roleplay.

If any of these are skipped, the skill has not actually been used correctly.
</EXTREMELY-IMPORTANT>

## Quick Start

When this skill is loaded, do these first:

1. If the opening material is a proposal or task book, run the Proposal Challenge Gate.
2. Identify the platform and check whether the planned experiment can really run there.
3. Identify the core papers and read them in full before they shape method or claim decisions.
4. Push implementation and experiments until at least one real experiment artifact exists.
5. Dispatch real reviewer subagents for independent sidecar review work before claiming that panel-style review happened.

If you are about to write a full thesis draft before doing those steps, stop and redirect.

## Overview

This skill is a unified thesis production system, not a loose collection of writing helpers. Codex remains the author and decision-maker; the skill mainly supplies one mission contract, one control loop, one reviewer membrane, and a small amount of deterministic tooling so the work stays evidence-backed instead of turning into free-form text generation.

The primary entrypoint is not a Python runner. The primary entrypoint is Codex itself operating through prompt-driven academic work: reading source materials, deciding what evidence is missing, choosing which tool to call next, drafting text, dispatching reviewer agents, and iterating.

Default target:
- Chinese STEM thesis manuscript in `docx`
- Research workflow driven by proposal/task-book inputs
- Free literature sources first
- Goal-driven iteration instead of rigid pipeline execution
- Final-delivery quality by default, not draft-only quality
- For computing and experiment-capable STEM topics, AI-authored code and original experiments are mandatory by default
- Experiments and the conclusions they support are the thesis body; formatting is delivery work, not the system core

This skill must be runnable from a fresh context. Do not assume prior chat memory. The first turn should be able to reconstruct the task from the source files, the profile, and the companion skills listed here.

Core mental model:
- The skill defines one mission contract and keeps all work subordinate to it.
- The main AI decides how to reduce the gap between current state and mission completion.
- Experiments, conclusions, and manuscript integration are the real core of the system.
- Scripts only help with narrow deterministic tasks.
- Thesis review is primarily performed by AI reviewer subagents, not by scripts.
- Authenticity outranks speed or polish: do not fake understanding, fake citations, or fake results.

## The Rule

Use this skill as a control discipline, not as a loose reference.

Before normal thesis execution:
- challenge the proposal if the proposal is defining the path
- read the core literature deeply enough to justify decisions
- push real experiment work until real artifacts exist
- dispatch real reviewer subagents for independent sidecar review work instead of narrating imaginary review

If one of those did not happen, treat the workflow as incomplete rather than rationalizing past it.

## First Five Moves

For a fresh thesis task, the default opening sequence is:

1. Challenge the proposal.
2. Lock the feasible experiment route.
3. Read the core papers in full.
4. Start real implementation and experiments.
5. Only then expand toward full-manuscript integration.

This sequence may overlap in time, but it may not be silently skipped.

## Proposal Challenge Gate

Before normal thesis production begins, this skill must pass a hard entry stage driven by the user's proposal, task book, or equivalent source material.

This gate is mandatory when the thesis target is being inferred from an opening proposal-like document.

Purpose:
- challenge the proposal before the system silently accepts it
- identify obvious mistakes, ambiguous claims, overpromised goals, and missing operational detail
- surface better technical or experimental alternatives
- verify whether the current machine and platform can actually execute the planned experiments
- prevent the thesis from drifting into a false plan that later forces fake experiments or fake conclusions

Minimum discussion topics:
- whether the proposal's research question is coherent and specific enough
- whether key concepts, metrics, baselines, datasets, or claimed contributions are confused
- whether there is a better or safer alternative route worth adopting
- whether the current platform such as macOS, Windows, or Linux can actually run the required experiments
- if the current platform cannot support the experiment plan, what real substitute route will be used instead

Execution rule:
- The main AI must lead this discussion.
- The main AI should dispatch fresh-context subagents for bounded sidecar challenge roles such as route-alternative challenge and platform-feasibility challenge when those checks can proceed independently.
- The proposal challenge gate is not complete until the main AI has resolved the core proposal judgment and incorporated any useful sidecar challenge findings.
- The output of this gate should be consolidated into a short `proposal_challenge_summary` using `references/templates/proposal-challenge-summary.md` or an equivalent scratch artifact.
- Normal literature deep-reading, coding, experimentation, and thesis drafting may begin only after this gate has identified the blocking risks and the main AI has either resolved them or recorded a real fallback path.
- If this gate discovers a blocker with no credible workaround, the system must not pretend that the thesis path is settled.

## Red Flags

These thoughts mean the agent is drifting and should self-correct immediately:

| Thought | Reality |
|---------|---------|
| "I can refine the proposal while I draft the thesis" | Proposal challenge is a hard pre-execution gate. |
| "I skimmed enough papers to start writing conclusions" | Core papers must be fully read before they anchor claims. |
| "I can finish the draft now and add experiments later" | No real experiment artifact means no full draft or final `docx` for experiment-capable topics. |
| "I reviewed it mentally from multiple angles" | If the review is an independent sidecar task, use actual subagents; if it is immediate critical-path judgment, do it locally and do not pretend a panel ran. |
| "The scripts are enough to say review passed" | Scripts only catch rigid failures, not academic judgment. |
| "This is just an internal draft" | If it looks like a full thesis draft, the experiment and review bars still apply. |

## Unified System

This skill should behave like one integrated system with four layers:

1. `Experiment Core`
   The main AI writes or adapts thesis-critical code, runs experiments, collects measurements, and tests whether the research question is actually being answered.
2. `Conclusion Core`
   The main AI turns raw results into bounded claims, compares alternatives, explains limitations, and decides what the thesis is actually allowed to conclude.
3. `Manuscript Integration Core`
   The main AI organizes experiments and conclusions into thesis chapters, figures, tables, and argumentative structure, and calibrates language and chapter arrangement against a few representative Chinese theses of the same level.
4. `Delivery Layer`
   Formatting, docx assembly, Word MCP repair, and final polish happen only after the manuscript already has research substance.

Priority rule:
- If experiment evidence is weak, work on experiments.
- If results exist but claims are weak, work on conclusions.
- If claims are clear but chapters are weak, work on manuscript integration.
- Only when the manuscript is substantively ready should delivery-format work dominate.
- During manuscript integration, prefer extracting language patterns and chapter moves from a few representative Chinese theses rather than inventing an abstract generic style.
- For experiment-capable theses, do not synthesize a full thesis draft or final `docx` before at least one real experiment artifact exists.

## Primary Entry Mode

Use this skill as an AI-led work loop:

1. Read the user's source materials and identify whether a proposal-like input is defining the thesis path.
2. If so, run the mandatory `Proposal Challenge Gate` before normal execution.
3. Form a final thesis target: what question will be answered, what evidence must exist, what code and experiments must be completed, and what the finished manuscript must contain.
4. Use `references/templates/thesis-target-contract.md` to keep the end state explicit.
5. If the task is long, multi-session, or multi-agent, establish a lightweight rolling plan using `references/templates/working-plan.md` or equivalent scratch notes.
6. Read and organize literature before substantial正文 writing, but do not lock yourself into a fixed order after that.
   For core literature and any paper used to support key claims, read the full paper rather than skimming title/abstract only.
7. Identify the current highest-priority blocker inside the unified system: experiment weakness, conclusion weakness, manuscript-integration weakness, or delivery weakness.
8. Call only the minimum supporting tools needed to remove that blocker.
9. Write code, run experiments, derive conclusions, and author thesis content yourself instead of delegating core research labor or authorship to scripts.
10. Use `references/templates/reviewer-panel.md` to dispatch fresh-context reviewer subagents and challenge whether the work is converging on the mission contract rather than merely accumulating artifacts.
11. Run deterministic hard checks only where needed, inspect failures, and revise again.
12. Assemble or refresh the `docx` only after the content is defensible enough.
13. Run a trajectory audit: verify that the latest round reduced mission risk rather than merely producing more surface output.

In other words:
- AI is the workflow engine.
- Prompting and judgment are the default control plane.
- The system cares much more about the final thesis quality than about preserving any fixed intermediate state.
- Scripts are optional tools under the AI, not the owner of the process.
- For long tasks, maintain a rolling plan, not a heavyweight frozen pipeline document.
- A `0 issue` review report only means no deterministic hard check fired; it does not by itself prove submission readiness or high academic quality.
- The default completion target is a presentable final thesis manuscript, not merely a defensible first draft.
- For computing and other experiment-capable STEM topics, the default completion bar includes AI-written code, AI-run experiments, and AI-produced experimental evidence, not only literature synthesis or simulated placeholders.
- Original experiments are a completion requirement, not a universal sequencing requirement; the main AI may draft chapters before experiments are fully finished, but must keep pushing experiment work in parallel and treat it as core thesis labor.
- For experiment-capable topics, "may draft chapters before experiments are fully finished" does not authorize zero-experiment full-manuscript delivery. Before real experiment artifacts exist, limit writing to planning-critical sections such as problem framing, literature review, method design, experiment plan, and implementation setup notes.
- Draft-only, placeholder-only, or outline-only behavior is fallback mode and must be treated as an explicit downgrade that requires user permission.
- Do not let formatting, docx assembly, or review theater outrank experiment and conclusion work.

Rolling-plan rule:
- Use a lightweight plan for non-trivial thesis runs.
- The plan should track only active objectives, blocked items, and the next evidence-producing actions.
- Do not force a heavyweight static `plan.md` for every run.
- If work spans multiple sessions, persist a `working_plan.md` or an equivalent section inside the thesis contract.
- The plan must keep experiment, conclusion, and manuscript-integration tracks visible when the topic requires experiments.
- Keep a short progress ledger inside the same working artifact so the system remembers what concrete evidence, code, and conclusions were added in the last rounds without splitting into many separate planning files.

## Companion Skills

This skill is intentionally not self-sufficient. Codex should actively combine it with other relevant skills when the task demands it.

Default companion stack for a real thesis run:
- `academic-writing`: refine research questions, section logic, academic tone, and discussion structure.
- `citation-management`: verify citation metadata, deduplicate records, and improve reference accuracy.
- `literature-review`: broaden or deepen literature coverage when the proposal literature is too thin or too narrow.
- `verification-before-completion`: verify tests, artifact generation, and review outputs before claiming the workflow is ready.

Optional companion stack:
- `research-paper-writer`: help with formal paper-style prose when a section needs stronger academic expression.
- `dispatching-parallel-agents` or `subagent-driven-development`: when literature search, experiment verification, and formatting checks can proceed in parallel.

## Multi-Agent Pattern

This skill should normally run in a multi-agent mode when the thesis task becomes non-trivial.

Role split:
- **Main Codex agent**: the sole author, decision-maker, and integrator. Owns mission control, thesis logic, final claims, experiment interpretation, and final prose.
- **Main Codex agent**: the sole code owner for thesis-critical implementation work unless the work is explicitly split across subagents.
- **Literature scout agents**: high-capability subagents that search, filter, and summarize bounded literature slices.
- **Citation verification agents**: high-capability subagents that check metadata consistency, duplicates, and citation quality.
- **Experiment sanity-check agents**: high-capability subagents that review benchmark assumptions, result consistency, and figure/table narratives.
- **Fresh-context reviewer agents**: bounded thesis reviewers instantiated from `references/templates/reviewer-panel.md`, given the mission contract and current artifacts but not the full chat history.
- **Format review agents**: bounded reviewers that inspect profile compliance and front-matter/docx issues only after substantive research work exists.

Rules:
- Prefer the latest high-capability model class for non-trivial subagent work.
- Use smaller/faster models only for clearly narrow and low-risk tasks.
- Main Codex agent must never delegate final authorship or final judgment.
- Main Codex agent must ensure thesis-critical code and experiments actually get executed; literature review alone is never enough for a computing thesis.
- Parallelize only independent tasks; keep tightly coupled chapter writing local to the main agent.
- Treat subagent output as evidence to review, not as final truth to trust blindly.
- Use fresh-context reviewers to detect drift from the mission contract, not to generate replacement prose.
- Use reviewer or investigator subagents when the task is independent, bounded, and can advance in parallel without blocking the immediate next local step.
- Use scripts only for dead checks such as section presence, placeholder leakage, profile compliance, metadata residue, or similar deterministic failures.
- Do not confuse script output with reviewer judgment.
- For literature work, scout agents may help screen candidates, but the main AI must still fully read the core papers it relies on for thesis logic, method choice, and final claims.
- Treat proposal challenge as a real pre-execution discussion stage, not as a cosmetic recap of the opening document.
- Do not silently self-simulate a subagent review that never happened.
- Do not offload urgent blocking judgment just to satisfy a workflow ritual.

## Tool Layer

Use scripts as supporting tools, not as the conceptual workflow entrypoint:

1. `scripts/parse_docx_input.py`: parse proposal/task-book inputs into text and sections.
2. `scripts/extract_thesis_spec.py`: build a thesis contract and reference constraints.
3. `scripts/search_literature.py` and `scripts/normalize_citations.py`: retrieve and clean literature candidates.
4. `scripts/build_citation_bank.py`: merge proposal references and external candidates.
5. `scripts/plan_experiments.py`: scaffold computing-oriented experiments.
6. `scripts/build_figure_plan.py`: build chart plans or prompt placeholders from experiment/result evidence.
7. `scripts/summarize_results.py`: summarize CSV results into reusable evidence.
8. `scripts/check_format_profile.py` and `scripts/review_draft.py`: run deterministic hard checks only; they do not replace reviewer subagents.
9. `scripts/assemble_docx.py`: package the draft into `docx`.
10. `scripts/run_thesis_workflow.py`: optional smoke-test or batch artifact runner, not the primary user-facing entry.

Runner rule:
- `run_thesis_workflow.py` must not fabricate thesis evidence in default mode.
- If placeholder simulation is ever used for exploratory drafting, it must be an explicit downgrade mode and must not be mistaken for final evidence.
- A thesis artifact bundle created without real experiment results should be treated as incomplete, not as a hidden shortcut to final delivery.

If a Word-focused MCP is available in the current environment:
- Use it after `docx` assembly to inspect paragraph alignment, caption styling, page breaks, table layout, and figure placement.
- Prefer it for deterministic post-processing of an already-authored draft, not for replacing thesis authorship.
- In this workspace, `safe_docx` is the preferred local MCP name when available.

Use as little code as necessary:
- Prefer `.md` guidance, rubrics, prompts, and reviewer roles over automating the whole writing process.
- Keep framework code light, but do not underinvest in thesis-critical implementation work. For computing theses, the main AI must still write and run substantive research code.
- Do not encode subjective writing choices, literature judgments, or research direction as hard pipeline rules.
- Do not encode reviewer judgment itself as a script unless the failure mode is genuinely rigid and deterministic.

## Working Style

- Prefer target-driven execution even if the user asks for a full draft in one go.
- Start long runs with a short working plan, then keep rewriting it as the real blockers change.
- Ground the thesis in real literature reading before major experiment decisions or large-scale正文 drafting.
- If a chapter lacks evidence, go back and strengthen experiments or conclusions before polishing prose.
- For experiment-capable topics, writing and experiments should normally advance in parallel rather than waiting for one track to be fully complete before starting the other.
- Literature reading and experimentation should usually overlap after the initial grounding step: read first, then keep reading whenever experiments expose uncertainty, contradictions, or new ideas.
- Before real experiment artifacts exist, do not finalize abstract, results, conclusion, or full-manuscript delivery for experiment-capable theses.
- For computing theses, treat code implementation and executable experiments as core thesis work, not as optional support tasks.
- Treat experiment substance and claim quality as the primary gates.
- Treat manuscript organization as the next gate.
- Treat format, citation support, and section completeness as delivery gates that matter later.
- Treat language, framing, and chart quality as revisable review layers.
- Before major prose integration, calibrate against a few representative Chinese theses at the same level and study how they write abstracts, chapter openings, method transitions, result narration, and conclusion sections.
- Apply explicit de-AI writing discipline: avoid mechanical transition chains, empty emphasis sentences, unsupported intensifiers, and list-heavy正文.
- Use concept-image prompts as placeholders unless the user explicitly asks to connect an image model.
- When figures are to be rendered by an external image model, reuse `references/templates/figure-image-prompts.md` and prefer data-faithful prompts over decorative illustration prompts.
- For Chinese literature, prefer free sources first: local pasted/exported snippets in `literature_inputs/`, then optional `--online-search` retrieval via OpenAlex/Crossref.
- Candidate screening may start from metadata or abstracts, but any paper that will shape method design, experiment decisions, or thesis claims must be read in full before being treated as understood evidence.
- Keep project-specific seed materials out of the core skill logic. If a workspace has topic-specific literature seeds or notes, place them under `literature_inputs/` as optional local inputs rather than hard-coding them into the skill itself.
- When using the optional runner or individual scripts, expect artifacts such as `candidate_chinese_refs.json`, `figure_plan.json`, and `review_report.json`.
- Do not mistake artifact generation for authorship. The scripts help produce evidence and scaffolding; Codex is still responsible for thesis quality.
- The most important review layer is still AI reviewer subagents; coded checks exist only to catch rigid failures that should never consume reviewer attention.
- After assembling a real manuscript `docx`, check whether a Word-oriented MCP is available and use it for a final formatting pass before concluding that the document is presentable.
- In final reporting, explicitly separate: `hard checks passed`, `current thesis-manuscript quality`, and `residual research risks`.
- Do not treat simulated benchmark artifacts as sufficient final evidence for a computing thesis unless the user explicitly asked for outline-only or placeholder-mode output.
- When reporting statistical results, prefer explicit test choice, assumption status, effect size, and confidence interval rather than significance-only narration.
- When generating Python figures for thesis use, prefer color-safe palettes, thesis-ready dimensions, 450 DPI raster export, and SVG companion export.

## Trajectory Audit

At regular checkpoints, ask all four questions:

- Did the latest work strengthen experiment evidence?
- Did it clarify or constrain the thesis conclusions?
- Did it improve how those conclusions are integrated into the manuscript?
- If it mostly changed formatting or surface polish, was that really the current top blocker?

If the answer to the first three questions is repeatedly no, the system is drifting and must be redirected.

## Profiles

Read only the profile you need:
- `references/profiles/generic-stem.md`: generic fallback for Chinese STEM theses
- `references/profiles/computing-thesis.md`: computing-oriented drafting heuristics

For this repository, default to `generic-stem`.

## Review Rubrics

Load only the rubrics relevant to the current step:
- `references/rubrics/structure.md`
- `references/rubrics/citation.md`
- `references/rubrics/citation-balance.md`
- `references/rubrics/language.md`
- `references/rubrics/method.md`
- `references/rubrics/visualization.md`
- `references/rubrics/format.md`

## Templates

Use when generating structured intermediate artifacts:
- `references/templates/thesis-start-gate.md`
- `references/templates/chapter-contract.md`
- `references/templates/figure-plan.md`
- `references/templates/figure-image-prompts.md`
- `references/templates/ai-author-workloop.md`
- `references/templates/proposal-challenge-summary.md`
- `references/templates/thesis-target-contract.md`
- `references/templates/working-plan.md`
- `references/templates/reviewer-panel.md`

## Notes

- This skill supports strong agent autonomy. Do not stay inside a fixed linear script if the evidence points elsewhere.
- A working plan is only a navigation aid. If reality changes, update or discard the stale plan instead of obeying it mechanically.
- If the current implementation starts to feel like a rigid pipeline, treat that as a design smell and move control back into prompt-driven reasoning.
- Treat literature reading, code implementation, experimentation, and正文写作 as intertwined work chosen by the main AI, not mandatory pipeline stages enforced by code.
- First version is optimized for computing, data, algorithms, software, systems, simulation, and public-dataset based STEM theses.
- For physical wet-lab or fieldwork topics, downgrade gracefully: use literature synthesis, public data reanalysis, or simulation and state the limitation explicitly.
