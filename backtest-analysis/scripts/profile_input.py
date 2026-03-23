#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import pandas as pd


SUMMARY_MARKERS = {
    "l4_sharpe",
    "l4_cost_to_gross",
    "l4_n_trades",
    "l4_net_pnl",
    "l4_max_drawdown",
    "l3_holdout_sharpe",
    "l2_oos_sharpe",
    "l3_sharpe_decay",
}

SIDE_CANDIDATES = ["trade_side", "strategy_trade_side", "side", "direction_side"]
HOLD_CANDIDATES = ["hold_bars", "bars_held", "holding_bars"]
TRADE_MARKERS = {"symbol", "entry_time", "exit_time", "pnl_net", "pnl_gross"}

CORE_METRIC_CANDIDATES = {
    "avg_pnl_per_trade": ["avg_pnl", "avg_pnl_per_trade", "trade_weighted_avg_pnl", "expectancy"],
    "win_rate": ["win_rate", "wr", "l4_win_rate", "trade_weighted_win_rate"],
    "sharpe": ["l4_sharpe", "sharpe", "aligned_sharpe", "median_sharpe"],
    "cost_to_gross": ["l4_cost_to_gross", "cost_to_gross", "cost_ratio", "median_cost_to_gross"],
}

PNL_CANDIDATES = ["pnl_net", "net_pnl", "pnl", "daily_pnl", "l4_net_pnl"]
GROSS_CANDIDATES = ["pnl_gross", "gross_pnl", "gross", "gross_pnl_usd"]
COST_CANDIDATES = ["cost", "fees", "commission", "slippage", "total_cost", "cost_total"]
DATE_CANDIDATES = ["exit_time", "date", "exit_date", "session_date", "entry_time", "entry_date"]


def find_first(columns: list[str], candidates: list[str]) -> str | None:
    for candidate in candidates:
        if candidate in columns:
            return candidate
    return None


def load_dataframe(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".parquet":
        return pd.read_parquet(path)
    if suffix in {".csv", ".txt"}:
        return pd.read_csv(path)
    if suffix == ".tsv":
        return pd.read_csv(path, sep="\t")
    if suffix == ".jsonl":
        return pd.read_json(path, lines=True)
    if suffix == ".json":
        raw = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(raw, list):
            return pd.DataFrame(raw)
        if isinstance(raw, dict):
            for key in ("rows", "records", "data", "items"):
                value = raw.get(key)
                if isinstance(value, list):
                    return pd.DataFrame(value)
            return pd.DataFrame([raw])
    raise ValueError(f"Unsupported file type: {path}")


def infer_kind(columns: list[str]) -> str:
    colset = set(columns)
    if len(SUMMARY_MARKERS & colset) >= 3:
        return "summary_ledger"
    if len(TRADE_MARKERS & colset) >= 4 and (
        find_first(columns, SIDE_CANDIDATES) or find_first(columns, HOLD_CANDIDATES)
    ):
        return "trade_ledger"
    if find_first(columns, DATE_CANDIDATES) and find_first(columns, PNL_CANDIDATES):
        return "daily_series_or_trade_like"
    return "unknown_dataframe"


def series_stats(series: pd.Series) -> dict[str, Any]:
    clean = pd.to_numeric(series, errors="coerce").dropna()
    if clean.empty:
        return {}
    return {
        "count": int(clean.shape[0]),
        "min": float(clean.min()),
        "median": float(clean.median()),
        "mean": float(clean.mean()),
        "max": float(clean.max()),
    }


def compute_trade_profile(df: pd.DataFrame) -> dict[str, Any]:
    columns = list(df.columns)
    pnl_col = find_first(columns, PNL_CANDIDATES)
    gross_col = find_first(columns, GROSS_CANDIDATES)
    cost_col = find_first(columns, COST_CANDIDATES)
    date_col = find_first(columns, DATE_CANDIDATES)
    side_col = find_first(columns, SIDE_CANDIDATES)
    hold_col = find_first(columns, HOLD_CANDIDATES)

    profile: dict[str, Any] = {
        "symbols": int(df["symbol"].nunique()) if "symbol" in df.columns else None,
        "rows": int(len(df)),
        "sides": df[side_col].value_counts(dropna=False).to_dict() if side_col else {},
        "pnl_col": pnl_col,
        "gross_col": gross_col,
        "cost_col": cost_col,
        "date_basis": date_col,
        "side_col": side_col,
        "hold_col": hold_col,
    }

    if pnl_col:
        pnl = pd.to_numeric(df[pnl_col], errors="coerce").dropna()
        if not pnl.empty:
            wins = pnl[pnl > 0]
            losses = pnl[pnl < 0]
            profit_factor = None
            if losses.sum() < 0:
                profit_factor = float(wins.sum() / abs(losses.sum())) if wins.sum() > 0 else 0.0
            profile["trade_pnl"] = {
                "total": float(pnl.sum()),
                "mean": float(pnl.mean()),
                "median": float(pnl.median()),
                "win_rate": float((pnl > 0).mean()),
                "profit_factor": profit_factor,
                "best_trade": float(pnl.max()),
                "worst_trade": float(pnl.min()),
            }

    if hold_col:
        profile["hold_bars"] = series_stats(df[hold_col])

    if "symbol" in df.columns and pnl_col:
        by_symbol = (
            df.assign(_pnl=pd.to_numeric(df[pnl_col], errors="coerce"))
            .groupby("symbol", dropna=False)["_pnl"]
            .agg(["count", "sum", "mean"])
            .sort_values("sum", ascending=False)
        )
        profile["top_symbols_by_pnl"] = by_symbol.head(10).reset_index().to_dict(orient="records")
        profile["bottom_symbols_by_pnl"] = by_symbol.tail(10).sort_values("sum").reset_index().to_dict(orient="records")

    if date_col:
        dt = pd.to_datetime(df[date_col], errors="coerce")
        valid = dt.notna()
        if valid.any():
            profile["date_range"] = {
                "start": dt[valid].min().isoformat(),
                "end": dt[valid].max().isoformat(),
            }
            if pnl_col:
                temp = pd.DataFrame(
                    {
                        "_date": dt.dt.date,
                        "_pnl": pd.to_numeric(df[pnl_col], errors="coerce"),
                    }
                ).dropna()
                if not temp.empty:
                    daily = temp.groupby("_date")["_pnl"].sum().sort_index()
                    profile["daily_realized"] = {
                        "days": int(daily.shape[0]),
                        "positive_days": int((daily > 0).sum()),
                        "negative_days": int((daily < 0).sum()),
                        "mean": float(daily.mean()),
                        "median": float(daily.median()),
                        "best_day": float(daily.max()),
                        "worst_day": float(daily.min()),
                    }

    if gross_col and cost_col:
        gross = pd.to_numeric(df[gross_col], errors="coerce").fillna(0.0)
        cost = pd.to_numeric(df[cost_col], errors="coerce").fillna(0.0)
        gross_sum = float(gross.sum())
        cost_sum = float(cost.sum())
        ratio = None
        if abs(gross_sum) > 1e-12:
            ratio = float(cost_sum / abs(gross_sum))
        profile["cost_summary"] = {
            "gross_sum": gross_sum,
            "cost_sum": cost_sum,
            "cost_to_gross": ratio,
        }

    return profile


def compute_summary_profile(df: pd.DataFrame) -> dict[str, Any]:
    profile: dict[str, Any] = {
        "rows": int(len(df)),
        "symbols": int(df["symbol"].nunique()) if "symbol" in df.columns else None,
        "sides": df["trade_side"].value_counts(dropna=False).to_dict() if "trade_side" in df.columns else {},
    }

    available_core: dict[str, str] = {}
    missing_core: list[str] = []
    for key, candidates in CORE_METRIC_CANDIDATES.items():
        matched = find_first(list(df.columns), candidates)
        if matched:
            available_core[key] = matched
        else:
            missing_core.append(key)
    profile["available_core_metrics"] = available_core
    profile["missing_core_metrics"] = missing_core

    for col in [
        "l4_sharpe",
        "l4_cost_to_gross",
        "l4_n_trades",
        "l4_net_pnl",
        "l4_max_drawdown",
        "l3_holdout_sharpe",
        "l2_oos_sharpe",
        "l3_sharpe_decay",
        "avg_pnl",
        "win_rate",
        "profit_factor",
    ]:
        if col in df.columns:
            profile[col] = series_stats(df[col])

    if {"l4_net_pnl", "l4_n_trades"}.issubset(df.columns):
        net = pd.to_numeric(df["l4_net_pnl"], errors="coerce")
        trades = pd.to_numeric(df["l4_n_trades"], errors="coerce")
        derived = net / trades.replace(0, pd.NA)
        profile["derived_avg_pnl_per_trade"] = series_stats(derived)

    required = {"l4_sharpe", "l4_cost_to_gross", "l4_n_trades"}
    if required.issubset(df.columns):
        sharpe = pd.to_numeric(df["l4_sharpe"], errors="coerce")
        cg = pd.to_numeric(df["l4_cost_to_gross"], errors="coerce")
        trades = pd.to_numeric(df["l4_n_trades"], errors="coerce")
        profile["quality_floors"] = {
            "sharpe_ge_1_0": int((sharpe >= 1.0).sum()),
            "cost_le_25pct": int((cg <= 0.25).sum()),
            "trades_ge_30": int((trades >= 30).sum()),
            "expensive_sparse": int(((cg > 0.20) & (trades <= 30)).sum()),
        }

    return profile


def profile_path(path: Path) -> dict[str, Any]:
    df = load_dataframe(path)
    columns = list(df.columns)
    kind = infer_kind(columns)
    payload: dict[str, Any] = {
        "input_path": str(path),
        "kind": kind,
        "rows": int(len(df)),
        "columns": columns,
        "column_count": int(len(columns)),
    }

    if kind == "trade_ledger":
        payload["profile"] = compute_trade_profile(df)
    elif kind == "summary_ledger":
        payload["profile"] = compute_summary_profile(df)
    else:
        payload["profile"] = {
            "date_col": find_first(columns, DATE_CANDIDATES),
            "pnl_col": find_first(columns, PNL_CANDIDATES),
            "summary_guess": compute_summary_profile(df),
            "trade_guess": compute_trade_profile(df),
        }
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile backtest input files for the backtest-analysis skill.")
    parser.add_argument("--input", action="append", required=True, help="Input file path. Repeat for multiple inputs.")
    args = parser.parse_args()

    results: list[dict[str, Any]] = []
    for raw_path in args.input:
        path = Path(raw_path).expanduser().resolve()
        if not path.exists():
            raise FileNotFoundError(f"Input not found: {path}")
        results.append(profile_path(path))

    print(json.dumps({"inputs": results}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
