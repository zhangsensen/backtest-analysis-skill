# Backtest Analysis Skill

[![validate](https://github.com/zhangsensen/backtest-analysis-skill/actions/workflows/validate.yml/badge.svg)](https://github.com/zhangsensen/backtest-analysis-skill/actions/workflows/validate.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Structured analysis for backtest ledgers, trade logs, daily PnL series, scorecards,
and A/B comparison packs.

This repository contains a portable `SKILL.md`-compatible skill for agents such as
Codex or other skill-aware coding assistants.

It also includes a small input profiler that recognizes common backtest artifact
shapes before analysis starts.

## Why This Exists

Most backtest reviews fail in one of four ways:

- they over-weight `total_pnl`
- they ignore left-tail risk
- they skip stability checks
- they confuse selection outputs with deployable evidence

This skill exists to force a more disciplined review path.

Instead of asking an agent to "look at this backtest" and hoping it chooses the
right framework, you give it a concrete artifact and a fixed analysis contract.

## What It Does

The skill turns concrete backtest artifacts into a disciplined decision memo.

It forces every analysis to cover:

- return
- risk
- stability
- trade quality

And it prevents common mistakes:

- deciding from one metric alone
- ignoring risk
- letting `total_pnl` dominate the verdict
- treating selection outputs as if they were full portfolio audits

## What Makes It Different

This is not just a prompt that says "analyze the data carefully."

It explicitly:

- fingerprints the input before analysis
- distinguishes summary ledgers from trade ledgers and daily series
- requires return, risk, stability, and trade-quality coverage
- pushes the agent toward a final decision memo
- keeps verdict language separate from root-cause diagnosis

Use this when you want a repeatable decision process, not a one-off opinion.

## Decision Vocabulary

By default the skill uses:

- `promote`
- `watch`
- `reject`

You can map those to your own language, such as:

- `上线`
- `观察`
- `弃用`

## Typical Flow

1. Profile the artifact.
2. Identify whether it is a summary ledger, trade ledger, daily PnL series, or A/B pack.
3. Analyze the artifact across the four required dimensions.
4. Produce a verdict:
   - `promote`
   - `watch`
   - `reject`

## Repository Layout

```text
backtest-analysis/
  SKILL.md
  agents/openai.yaml
  references/
    framework.md
    data_shapes.md
  scripts/
    profile_input.py
examples/
  summary_ledger.csv
  trade_ledger.csv
  daily_pnl.csv
```

## Install

### Repo-local install for Codex-style agents

Copy the `backtest-analysis/` directory into your repo-local skills directory:

```bash
mkdir -p .agents/skills
cp -R backtest-analysis .agents/skills/
```

### User-global install

Copy the skill directory into your global skills location:

```bash
mkdir -p ~/.codex/skills
cp -R backtest-analysis ~/.codex/skills/
```

## Dependencies

The bundled profiler script requires:

- `pandas`
- `pyarrow` for parquet inputs

Install with:

```bash
pip install -r requirements.txt
```

## Quick Start

Profile a file first:

```bash
python backtest-analysis/scripts/profile_input.py --input path/to/results.parquet
```

Try the bundled examples:

```bash
python backtest-analysis/scripts/profile_input.py --input examples/summary_ledger.csv
python backtest-analysis/scripts/profile_input.py --input examples/trade_ledger.csv
python backtest-analysis/scripts/profile_input.py --input examples/daily_pnl.csv
```

Then ask your agent to use the skill on that artifact.

Example:

> Use `$backtest-analysis` to analyze this ledger and return a structured promote/watch/reject verdict.

## Example Output Shape

The skill is designed to produce a report with sections like:

```text
Input fingerprint
Decision context
Return
Risk
Stability
Trade quality
Verdict
Why not the other verdicts
Next action
Confidence and missing evidence
```

That structure is the point. It prevents the analysis from collapsing into
"Sharpe looks fine" or "PnL looks good, ship it."

## Best Use Cases

- strategy candidate ledgers
- trade-level ledgers
- daily PnL or return series
- A/B result packs
- scorecard exports

## Who It Is For

- quantitative researchers comparing candidate sets
- solo traders reviewing strategy ledgers
- teams using agents to standardize backtest review
- anyone with parquet/csv/json backtest artifacts who wants a stricter decision rubric

## Validation

The repository ships with a GitHub Actions workflow that:

- profiles the example datasets
- checks the skill frontmatter

You can also run the same checks locally:

```bash
python backtest-analysis/scripts/profile_input.py --input examples/summary_ledger.csv
python backtest-analysis/scripts/profile_input.py --input examples/trade_ledger.csv
python backtest-analysis/scripts/profile_input.py --input examples/daily_pnl.csv
```

## Not For

- open-ended root-cause diagnosis with no concrete dataset
- code review
- implementation-vs-research consistency audits
- direct broker-state verification

## Roadmap

Likely future additions:

- richer comparison helpers for multi-file A/B analysis
- optional markdown report generation
- more example datasets
- additional data-shape recognizers for common backtest frameworks

## License

MIT
