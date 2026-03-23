---
name: backtest-analysis
description: |
  Deep, structured analysis for backtest ledgers, trade logs, daily PnL series,
  scorecards, and A/B comparison packs. Use when the user provides concrete
  parquet/csv/json backtest artifacts and wants a decision such as promote,
  watch, or reject based on the data itself. Covers return, risk, stability,
  and trade quality, prevents single-metric conclusions, and prevents total PnL
  from dominating the verdict. Do not use for open-ended root-cause diagnosis
  without a concrete dataset, or for implementation-vs-research consistency
  audits.
---

# Backtest Analysis

## Goal

Turn raw backtest artifacts into a disciplined decision memo. Use this skill to
analyze a strategy, candidate set, or comparison pack without falling into the
usual traps: cherry-picking one metric, ignoring risk, or confusing selection
artifacts with deployable evidence.

## Workflow

### 1. Fix The Decision Context

State the context explicitly before analyzing:

- `research`: decide whether to promote to the next validation stage
- `paper/sim`: decide whether to keep under observation or controlled forward testing
- `live`: decide whether something is eligible for live-readiness discussion

Do not collapse these contexts into one generic "go/no-go".

### 2. Fingerprint The Input First

Run the bundled profiler before interpreting the file:

```bash
python scripts/profile_input.py --input <path>
python scripts/profile_input.py --input <path_a> --input <path_b>
```

If the file shape is still unclear, read:

- `references/data_shapes.md`

### 3. Apply The Four Required Dimensions

Read:

- `references/framework.md`

Always cover:

1. return
2. risk
3. stability
4. trade quality

Never skip one of the four. If the data does not support a dimension, say so and
reduce confidence.

### 4. Enforce Hard Constraints

1. Never issue a verdict from one metric alone.
2. Never skip risk analysis.
3. Never let `total_pnl` dominate stronger quality metrics.
4. If long and short are mixed, split them before concluding on the combined set.
5. If the artifact is a selection or dedup output, say that clearly instead of treating it like a full portfolio audit.
6. If the user provides project-specific evaluation rules, those rules override the generic defaults in this skill.

### 5. Output Contract

Produce these sections:

1. `Input fingerprint`
2. `Decision context`
3. `Return`
4. `Risk`
5. `Stability`
6. `Trade quality`
7. `Verdict`
8. `Why not the other verdicts`
9. `Next action`
10. `Confidence and missing evidence`

## Default Verdict Vocabulary

- `promote`
- `watch`
- `reject`

If the user prefers other labels such as `上线 / 观察 / 弃用`, map to their vocabulary
but keep the same underlying decision semantics.

## Good Use Cases

- "Analyze this ledger and tell me whether to promote it."
- "Compare these two backtest result packs."
- "Review this trade log without letting total PnL dominate the conclusion."
- "Give me a structured watch/reject memo for this candidate set."

## Not For

- open-ended causal diagnosis with no concrete data artifact
- code review
- implementation-vs-research consistency checking
- deployment execution or broker-state verification
