# Backtest Analysis Skill

Structured backtest analysis for ledgers, trade logs, daily PnL series, scorecards,
and A/B comparison packs.

This repository contains a portable `SKILL.md`-compatible skill for agents such as
Codex or other skill-aware coding assistants.

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

## Decision Vocabulary

By default the skill uses:

- `promote`
- `watch`
- `reject`

You can map those to your own language, such as:

- `上线`
- `观察`
- `弃用`

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

Then ask your agent to use the skill on that artifact.

Example:

> Use `$backtest-analysis` to analyze this ledger and return a structured promote/watch/reject verdict.

## Best Use Cases

- strategy candidate ledgers
- trade-level ledgers
- daily PnL or return series
- A/B result packs
- scorecard exports

## Not For

- open-ended root-cause diagnosis with no concrete dataset
- code review
- implementation-vs-research consistency audits
- direct broker-state verification

## License

MIT

