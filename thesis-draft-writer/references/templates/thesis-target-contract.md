# Thesis Mission Contract

Use this before substantial writing. Fill it mentally or as scratch notes; do not treat it as a formality.

If the thesis starts from a proposal or task book, complete the proposal challenge stage first and carry its decisions into this contract.

## 1. Thesis Goal

- Research title:
- Final output type: `docx` thesis manuscript
- Target level: undergraduate / master / other
- Main discipline:
- Expected contribution type:
  - implementation
  - experiment
  - system design
  - literature synthesis
  - method improvement

## 1A. Proposal Challenge Outcome

- proposal challenge summary completed:
- obvious errors or confusions found:
- platform feasibility verdict:
- agreed substitute route if the original experiment path is infeasible:
- unresolved blockers:

## 2. Non-Negotiable End State

The final manuscript must satisfy all of the following:

- It reads like a thesis, not like a workflow log or tool demo.
- Core claims are supported by literature or experimental evidence.
- For computing theses, thesis-critical claims are supported by code the AI actually wrote or executed, not only by narrative description.
- The experiment chapter reports the study itself, not the helper scripts.
- For experiment-capable theses, a full manuscript is not considered deliverable until at least one real experiment artifact exists.
- Citations are topically aligned, not only numerically balanced.
- Figures, tables, and appendix material serve the thesis argument.
- Formatting and front matter meet the active profile.
- Format defects are not allowed, but they also do not define the thesis core.

## 3. Research Questions

- Primary question:
- Secondary question 1:
- Secondary question 2:

Every chapter should map back to these questions.

## 4. Core System

The system must stay ordered around the following priority:

- Experiment core:
  - what code must run
  - what measurements must exist
  - what comparisons must be made
- Conclusion core:
  - what the thesis is allowed to conclude from those measurements
  - what remains uncertain
- Manuscript integration core:
  - where each result and conclusion appears in the manuscript
  - which figure/table supports which claim
  - which representative Chinese theses are being used to calibrate language and chapter arrangement
- Delivery layer:
  - what formatting and docx work remains after the substance is ready

## 5. Evidence Plan

- What literature evidence is required?
- Which papers must be fully read before method selection, experiment design, or final claim-making?
- What implementation evidence is required?
- What experiment evidence is required?
- What figures/tables are required?
- What claims must remain cautious until stronger evidence exists?

For computing and experiment-capable STEM theses, this section should normally include:
- which papers are core enough that the main AI must read them in full rather than cite them from metadata or abstract-only impressions
- what code the AI itself must write or run
- what original measurements the AI itself must produce
- what conclusions depend on those measurements
- which chapters can be drafted before experiments finish, and which claims must stay provisional until experiment evidence is complete
- what would count as an unacceptable downgrade to draft-only or placeholder-only output

## 6. Current Work Plan

For long or multi-session work, maintain a lightweight rolling plan here or in `working-plan.md`.

- active literature objective:
- active experiment objective:
- active conclusion objective:
- active writing objective:
- active review objective:
- next evidence-producing action:
- currently blocked claim or section:

The plan should stay short and change often. It exists to preserve momentum, not to freeze the workflow.

## 7. AI Autonomy Rule

- Main AI decides the order of reading, coding, experimenting, and writing.
- Main AI must challenge the incoming proposal instead of inheriting it blindly.
- Tools are only used when they close a real evidence gap.
- Intermediate artifacts are expendable.
- The only thing that matters is whether the final thesis manuscript becomes more defensible and more complete.
- The AI must not let format work or presentation work outrank the experiment core unless the substance is already ready.

## 8. Trajectory Audit

At checkpoints, ask:

- Is the experiment core becoming stronger?
- Are the thesis conclusions becoming clearer and more defensible?
- Is the manuscript becoming a better carrier of those conclusions?
- Has delivery work started dominating too early?

If these answers are going in the wrong direction, redirect the system immediately.

## 9. Failure Conditions

If any of the following appears, the manuscript is not ready:

- proposal tone
- placeholder prose
- tool or script leakage into正文
- weak claim-reference fit
- experiment chapter without methodological detail
- computing thesis with no AI-written or AI-executed thesis-critical code path
- experiment-capable thesis with no AI-produced original experimental evidence
- experiment-capable thesis that outputs a complete draft or `docx` before any real experiment artifact exists
- the manuscript grows while the experiment core and conclusion core remain weak
- long-running work with no visible active plan, causing experiment and writing tracks to drift apart
- format work starts dominating while the thesis still lacks substantive experimental support
- conclusion that summarizes workflow instead of research findings
- delivery wording that treats passing hard checks as proof of submission readiness
