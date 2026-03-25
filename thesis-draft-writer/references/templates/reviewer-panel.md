# Reviewer Panel

Use this when the main AI wants thesis-style "tests". The main AI remains the author; reviewers only challenge the manuscript's convergence toward the mission contract. These reviewers are AI subagents, not scripts.

## Main Rule

- Each reviewer inspects the thesis from one angle only.
- Reviewers return findings, not rewritten chapters.
- The main AI decides which findings are valid and how to revise.
- Reviewers should judge whether the system is drifting away from experiment-and-conclusion-centered progress.
- fresh-context reviewers should be given the mission contract and current artifacts, but not the whole chat history.
- Deterministic scripts may run alongside this panel, but only for rigid checks and never as substitutes for reviewer judgment.
- This panel refers to actual subagent dispatch, not the main AI pretending to have asked reviewers.
- Use this panel when the review work is a genuine sidecar task. If the next critical move depends on immediate thesis judgment, the main AI should decide locally instead of blocking on ceremony.

At proposal stage, the same panel idea can be used in a smaller form to challenge the opening plan before execution begins.

## Proposal-Stage Challenge Roles

### Proposal Reviewer A: Question Challenge

Focus:
- whether the proposal defines a real research question
- whether key concepts are confused or too vague
- whether the promised contribution exceeds the available evidence path

Reject when:
- the proposal sounds impressive but is not operational
- key metrics, baselines, or datasets are undefined
- the stated contribution cannot be tested in a thesis-scale workflow

### Proposal Reviewer B: Alternative Route Challenge

Focus:
- whether there is a better or safer route than the proposal's current path
- whether a narrower but more defensible scope would produce a stronger thesis

Reject when:
- the current route is unnecessarily risky
- a simpler route would produce stronger real evidence
- the proposal locks onto one implementation path too early without comparison

### Proposal Reviewer C: Platform Feasibility Challenge

Focus:
- whether the planned experiment can actually run on the current machine and platform
- whether macOS, Windows, Linux, local hardware, or remote environments change feasibility
- whether a real substitute path exists if the original platform is infeasible

Reject when:
- the proposal assumes unavailable hardware, unsupported instruction sets, or unavailable toolchains
- the current machine cannot run the core experiment and no honest workaround is defined
- the thesis plan quietly depends on a platform the user does not actually have

## Reviewer 0: Trajectory Reviewer

Focus:
- whether current work is reducing the real top blocker
- whether experiments and conclusions remain the system core
- whether delivery work has started dominating too early

Reject when:
- the manuscript keeps growing but the experiment core is still weak
- results exist but conclusions are still vague or overclaimed
- formatting, docx repair, or visual polish are taking over before the substance is ready

## Reviewer 1: Structure Reviewer

Focus:
- chapter logic
- question-chapter alignment
- whether the text is still a proposal
- whether the conclusion actually concludes

Reject when:
- the chapter order is incoherent
- the method chapter does not support the experiment chapter
- the conclusion mostly summarizes process instead of findings

## Reviewer 2: Citation Reviewer

Focus:
- claim-reference fit
- topicality of references
- Chinese/English balance
- duplicate or low-value references

Reject when:
- references are numerically fine but thematically weak
- important claims have no direct support
- Chinese references are generic filler

## Reviewer 3: Experiment Reviewer

Focus:
- experiment purpose
- whether thesis-critical code was actually written or executed
- implementation details
- environment and parameter clarity
- metric choice
- threats and limitations
- whether experiment work is being seriously advanced rather than indefinitely deferred
- whether the conclusion layer is actually emerging from the experiments

Reject when:
- the experiment chapter reads like a tooling note
- a computing thesis describes an intended implementation path but does not show evidence that the AI actually wrote or executed thesis-critical code
- environment, repetitions, or measurement method are missing
- results are reported without enough methodological context
- a computing/STEM thesis relies only on simulated or placeholder evidence even though original experiments were feasible
- a full draft, polished abstract, finished conclusion, or `docx` is produced before any real experiment artifact exists for an experiment-capable thesis
- the draft keeps expanding while experiment work remains stagnant without a defensible reason
- a long-running thesis effort has no visible active plan and the experiment track has effectively disappeared from execution
- the chapter presents metrics but does not turn them into bounded research conclusions

## Reviewer 4: Language Reviewer

Focus:
- academic tone
- Chinese thesis style
- English abstract quality
- local awkwardness and overclaiming
- whether the prose actually resembles Chinese undergraduate/master thesis rhetoric rather than generic model-written academic text

Reject when:
- wording sounds like prompts, artifacts, or dev logs
- English abstract contains Chinese leakage or unnatural phrasing
- claims are stronger than the evidence warrants
- chapter openings, result narration, and conclusion phrasing do not read like representative Chinese theses of the target degree level
- prose overuses mechanical transitions, empty emphasis shells, or unsupported intensifiers in a way that exposes generic model writing

## Reviewer 5: Format Reviewer

Focus:
- front matter completeness
- profile compliance
- appendix appropriateness
- figure/table naming
- whether a Word-focused MCP post-pass is needed for layout defects

Reject when:
- front matter still contains dev-stage wording
- appendix is just internal production residue
- figures/tables are not ready for thesis reading
- the `docx` still shows obvious alignment, caption, table, or figure-placement defects that should have triggered a Word-focused MCP repair pass
- format work is being treated as if it could compensate for weak experiments or weak conclusions
- Python-generated final figures are still missing reusable high-quality exports such as thesis-ready PNG/SVG outputs when such figures are part of the deliverable

## Reviewer 6: Delivery Reviewer

Focus:
- whether the final status report overclaims
- whether hard checks are being confused with academic quality
- whether residual risks are stated plainly

Reject when:
- `0 issues` is described as equivalent to submission readiness
- simulated evidence is reported as if it were final measured evidence
- auxiliary artifacts still have inconsistencies but the delivery report sounds complete

## Escalation Rule

If two or more reviewers independently object to the same section, the main AI should treat that section as a blocking revision target.

## Minimum Dispatch Rule

- Proposal stage: dispatch reviewer subagents only for bounded sidecar challenge angles such as platform feasibility or alternative-route checks. The main AI keeps the core proposal judgment.
- Draft-review stage: when review can run as an independent sidecar task, dispatch at least two fresh-context reviewer subagents, one of which must cover experiments or conclusions.
- If no reviewer subagent was actually dispatched, the skill must not describe the work as having passed reviewer-panel review.

## Boundary With Scripts

- Scripts may check things like required sections, placeholder residue, obvious degree/profile mismatch, file-path leakage, or similar hard failures.
- Scripts should not be treated as reviewers for language quality, academic validity, novelty, evidential sufficiency, chapter logic, or conclusion strength.
- If a judgment requires interpretation, comparison, caution, or academic taste, dispatch a reviewer subagent instead of trying to automate it away.
