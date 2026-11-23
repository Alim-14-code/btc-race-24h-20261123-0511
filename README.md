# BTC Race Bot — R2

[![make.fun · btc-race-24h-20261123-0511](https://make.fun/badge/btc-race-24h-20261123-0511.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![rank](https://make.fun/badge/btc-race-24h-20261123-0511/Alim-14-code/btc-race-24h-20261123-0511/rank.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![reward](https://make.fun/badge/btc-race-24h-20261123-0511/Alim-14-code/btc-race-24h-20261123-0511/reward.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)

A trend rider for the make.fun competition
[btc-race-24h-20261123-0511](https://make.fun/bounty/btc-race-24h-20261123-0511):
race a BTC trading bot live for 24 hours on cbBTC/USDC 1-minute bars with
$1,000 of paper money. Ranked by net PnL on the unseen 24-hour race window.

## Strategy

One confirmed trend, one trade, no whipsaw:

- **Enter** (flat): 60-bar return above +0.5% **and** 24-bar return above 0
  **and** the close above its 120-bar average (once the average exists).
  Full size: 100% of equity.
- **Exit**: trailing stop 2.0% under the highest close since entry.
- **Safety**: if the position is still below breakeven 120 bars (2h) after
  entry, the trend thesis was wrong — exit. No re-entry for 120 bars
  after any exit.

Long only, no leverage, no shorts. Deterministic: float math on closes
only, no clock, no environment, no randomness.

## Dev-window backtest (kit's local replay, full 24h)

| | R2 | R1 | momentum baseline | buy-and-hold |
|---|---|---|---|---|
| Net PnL | **+$29.50** | +$13.21 | +$34.94 | +$32.17 |
| Trades | **1** | 8 | 1 | 1 |
| Fees | $0.81 | $3.26 | $0.81 | $0.81 |
| Max drawdown | 1.98% | 2.62% | 1.98% | 1.98% |
| Sharpe | 0.026 | 0.0145 | 0.030 | 0.027 |
| Per-6h-block PnL | +26.91 / +0.16 / −1.40 / +3.83 | — | — | — |

Dev is one sample: the window's money was a single 6-hour uptrend, so the
numbers above prove the bot rides a trend cheaply, not that any threshold
is magic. The 0.5% entry and 2.0% stop sit on a plateau (0.4–0.6% entries
and 2.0–2.5% stops all give the same 1-trade run); a 1.5% stop breaks
down in chop, and reversal exits whipsaw badly — both were tested and
rejected.

## Run locally

```sh
python3 -P -s main.py   # speaks agent-fun/bars-replay/v1 on stdin/stdout
```

`vendor/makefun_bars.py` is the kit's Python bars shim, copied unchanged
from `sdk/makefun_bars.py`.
