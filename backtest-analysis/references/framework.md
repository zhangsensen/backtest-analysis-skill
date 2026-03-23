# Backtest Analysis Framework

This reference defines the default module-by-module workflow and verdict rubric.

## Evidence Priority

1. explicit project-specific rules or evaluation gates, if provided
2. code and emitted artifacts
3. ledger-level evidence
4. single-day observations

Single-day observations can support a warning. They cannot carry the final thesis.

## Module A: 快速体检

### Goal

Establish whether the artifact has enough quality information to justify a strong
conclusion, and surface immediate red flags.

### Mandatory core metrics

Use these four if present:

1. `avg_pnl/trade`
2. `WR`
3. `Sharpe`
4. `cost/gross`

Add these when available:

5. `n_trades`
6. `max_drawdown`
7. `holdout_sharpe`
8. `sharpe_decay`
9. `profit_factor`

### Quick triage output

Produce a small table:

| metric | value | interpretation |

If one or more of the core four are missing:

- say which are missing
- say whether they can be safely derived
- reduce confidence

### Immediate red flags

Flag these immediately if visible:

- `Sharpe < 0.3` in an M2-style or weak-candidate context
- `cost/gross > 60%`
- sample size too thin to support the claimed verdict
- mixed long/short with clearly asymmetric quality but only combined reporting
- decisions built mainly on `total_pnl`

## Module B: 风险深度分析

### Must cover

1. maximum drawdown or best available left-tail proxy
2. worst day / worst cluster if daily data exists
3. concentration risk
4. side asymmetry
5. execution or cost fragility

### Questions to answer

- Is the left tail acceptable for the current track?
- Are losses broad and random, or concentrated in specific symbols, sides, or windows?
- Does the artifact hide tail risk behind good averages?

### Time-Series Constraints

- If Sharpe or daily risk is derived from a time series, state whether all periods
  were included or only active periods.
- If the user asks about live behavior, distinguish local backtest or paper ledgers
  from actual broker truth.

## Module C: 稳定性验证

### Must cover

1. period stability
2. side stability
3. market/regime stability if available
4. parameter sensitivity if relevant
5. train/holdout/full-period consistency

### Rules

- If holdout looks far better than full-period L4, anchor on the more conservative full-period view
- If the task compares altered logic against an old freeze, old pool, or stale candidate set,
  call out the mismatch instead of treating it as apples-to-apples evidence.
- If the evidence comes from one narrow window, do not call it stable

### Typical negative patterns

- good headline Sharpe but poor holdout retention
- no stable candidate across nearby parameter settings
- verdict depends on one slice, one symbol, or one date bucket

## Module D: 交易质量分析

### Must cover

1. `avg_pnl/trade`
2. win rate / loss ratio / profit factor
3. holding-time distribution if available
4. expensive-and-sparse behavior
5. long/short split

### Default Ordering

Use this default quality-first order unless the user's system defines a stricter one:

1. `avg_pnl/trade`
2. `WR`
3. `Sharpe`
4. `cost/gross`
5. `max_drawdown`
6. `total_pnl`

### Strong-quality defaults

These are defaults, not universal laws. Override them when the source artifact or
the user's project defines explicit gates.

- `l4_sharpe >= 1.0` is a strong-quality floor for main-system-style candidates
- `cost/gross <= 25%` is a good default live-quality guardrail
- `cost/gross > 20%` plus `n_trades <= 30` is an expensive-sparse warning
- mixed books should report long and short separately

## Module E: 结论输出

## Verdict meanings

### `上线`

Use only when:

- the artifact passes the relevant hard gates
- quality-first ordering is supportive
- no structural rule conflict is present
- missing evidence is not material

Track-aware meaning:

- `research`: promote to next validation stage or freeze discussion
- `sim`: eligible for audit-only / forward observation
- `live`: eligible for live-readiness discussion, not direct deployment

### `观察`

Use when:

- the edge looks real but incomplete
- evidence is directionally positive but still fragile
- forward validation, side split, or risk confirmation is still missing
- the data supports continued monitoring but not a strong promotion

### `弃用`

Use when:

- hard gates fail
- risk dominates quality
- stability is absent
- the thesis relies on one metric or one narrow sample
- the artifact conflicts with canonical rules in a way that invalidates the claimed result

## Why-not section

Always explain:

- why it is not `上线`
- why it is not `观察`
- why it is not `弃用`

At least two of the three should be explicitly discussed.

## Recommended report close

End with:

1. exact verdict
2. one-line action
3. one-line blocker

Example:

- `Verdict: 观察`
- `Action: keep this in audit-only and gather 10-15 more trading days or a same-caliber rerun`
- `Blocker: current evidence is too concentrated in one slice and does not yet clear stability requirements`
