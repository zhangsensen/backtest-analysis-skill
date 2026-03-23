# Common Data Shapes

Use this reference when the input file shape is unclear.

## 1. Summary Ledger

Typical columns:

- `symbol`
- `factor`
- `trade_side`
- `l4_sharpe`
- `l4_cost_to_gross`
- `l4_n_trades`
- `l4_net_pnl`
- `l4_max_drawdown`
- `l3_holdout_sharpe`
- `l2_oos_sharpe`
- `l3_sharpe_decay`
- `avg_pnl`
- `win_rate`
- `profit_factor`

Safe to trust directly if the file is emitted by the pipeline or freeze tooling:

- `l4_sharpe`
- `l4_cost_to_gross`
- `l4_n_trades`
- `l4_net_pnl`
- `l4_max_drawdown`
- `l3_holdout_sharpe`
- `l2_oos_sharpe`
- `l3_sharpe_decay`

## 2. Trade Ledger

Typical columns:

- `symbol`
- `factor`
- `trade_side`
- `entry_time`
- `exit_time`
- `pnl_net`
- `pnl_gross`
- `cost`
- `fees`
- `hold_bars`
- `shares`

Safe to derive directly:

- total net PnL
- average / median PnL per trade
- win rate
- profit factor
- hold-bar distribution
- side mix
- symbol concentration
- best / worst days using exit-date grouping

Use caution when deriving:

- `Sharpe`
- `Sortino`
- `Calmar`

Only derive those confidently if the input is already a canonical daily/equity series.
Otherwise label them as proxies or leave them missing.

## 3. Daily PnL / Return Series

Typical columns:

- `date`
- `daily_pnl`
- `daily_return`
- `equity`

If you have explicit daily returns or equity:

- derive risk metrics from that series
- say exactly which column was used

If you only have dollar PnL and no starting capital:

- do not pretend to know the canonical Sharpe
- use best / worst / median day and drawdown on cumulative PnL as descriptive stats

## 4. A/B Comparison Pack

Typical inputs:

- two summary ledgers
- one comparison CSV/JSON
- one markdown report

Rules:

- compare like-for-like populations only
- separate headline performance from quality composition
- check whether one side is winning only by adding more low-quality strategies

## 5. Common Warnings

1. `total_pnl` without `avg_pnl`, `WR`, `Sharpe`, and `cost/gross` is not enough
2. `holdout_sharpe` alone is not a deployment-grade anchor
3. mixed long/short tables hide asymmetric quality
4. strategy-count changes are not performance improvements by themselves
5. historical ledger evidence beats one-day observation
