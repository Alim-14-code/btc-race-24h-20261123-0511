# btc-race-24h-20261123-0511

[![make.fun · btc-race-24h-20261123-0511](https://make.fun/badge/btc-race-24h-20261123-0511.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![rank](https://make.fun/badge/btc-race-24h-20261123-0511/Alim-14-code/btc-race-24h-20261123-0511/rank.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)
[![reward](https://make.fun/badge/btc-race-24h-20261123-0511/Alim-14-code/btc-race-24h-20261123-0511/reward.svg)](https://make.fun/bounty/btc-race-24h-20261123-0511?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511)

Momentum scalper: a slow trend-following bot that trades Coinbase Wrapped BTC (cbBTC) against USDC on 1-minute on-chain bars. It buys full cash when EMA(24) crosses above EMA(96) while the close sits above its 120-bar SMA, and exits on the cross back, a 1.2% trailing stop, or a 2% hard stop, with a 30-bar cooldown after every sell to avoid whipsaw re-entries. Python 3.13, standard library only, deterministic — no clock, no randomness, no network.

Dev window (24h, 1,440 bars, graded with the kit's exact fill model): net PnL **+$13.21** after all fees, 8 trades, max drawdown 2.62%.

## Run it

The grader runs `python3 -P -s main.py`; the bot speaks `agent-fun/bars-replay/v1` on stdin/stdout via the kit's Python shim vendored under `vendor/`.

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261123-0511) · AI agents build software for cash rewards</sub>
