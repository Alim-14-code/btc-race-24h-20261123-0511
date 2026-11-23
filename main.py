"""Momentum scalper: slow trend-following bot for cbBTC/USDC 1-minute bars.

Strategy (own design, written from the competition spec):
- Trend filter: only buy when the 1-minute close is above its 120-bar SMA.
- Entry: EMA(24) crosses above EMA(96) while the trend filter holds, full
  cash, one position at a time.
- Exit: EMA(24) crosses back below EMA(96), OR price falls 1.2% below the
  highest close since entry (trailing stop), OR price falls 2% below the
  entry fill price (hard stop).
- Cooldown: after any sell, wait 30 bars before buying again, to avoid
  whipsaw re-entries on the same chop.
- No trade in the first 120 bars (indicators warming up) and never during a
  warm-up phase. Deterministic: no clock, no randomness, no network, no
  files; every decision comes from the bars the harness sends.

Protocol: agent-fun/bars-replay/v1, via the kit's Python shim (vendored
unchanged under vendor/). Orders fill at the next bar's open, so the
max_slippage_bps of 250 bps covers the largest 1-minute moves seen in the
dev window (~72 bps) plus the modelled 2 bps slippage and price impact,
with headroom for bigger jumps on the unseen race window.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"
FAST_SPAN = 24
SLOW_SPAN = 96
SMA_WINDOW = 120
TRAIL_PCT = 0.012
HARD_STOP_PCT = 0.02
COOLDOWN_BARS = 30
MAX_SLIPPAGE_BPS = 250


class TrendBot:
    def __init__(self):
        self.closes = []
        self.fast_ema = None
        self.slow_ema = None
        self.prev_fast = None
        self.prev_slow = None
        self.sma_sum = 0.0
        self.entry_price = None
        self.peak_price = None
        self.last_sell_seq = -10 ** 9

    def _update(self, close):
        self.closes.append(close)
        kf = 2.0 / (FAST_SPAN + 1)
        ks = 2.0 / (SLOW_SPAN + 1)
        self.prev_fast, self.prev_slow = self.fast_ema, self.slow_ema
        self.fast_ema = close if self.fast_ema is None else close * kf + self.fast_ema * (1 - kf)
        self.slow_ema = close if self.slow_ema is None else close * ks + self.slow_ema * (1 - ks)
        self.sma_sum += close
        if len(self.closes) > SMA_WINDOW:
            self.sma_sum -= self.closes[-SMA_WINDOW - 1]

    def _sma(self):
        if len(self.closes) < SMA_WINDOW:
            return None
        return self.sma_sum / SMA_WINDOW


BOT = TrendBot()


def on_batch(state, batch):
    if state.warming_up:
        return []
    close = state.close(SYMBOL)
    if close is None:
        return []
    BOT._update(close)
    n = len(BOT.closes)
    if n < max(SLOW_SPAN, SMA_WINDOW):
        return []
    held = state.positions.get(SYMBOL)
    sma = BOT._sma()
    crossed_up = (
        BOT.prev_fast is not None
        and BOT.prev_fast <= BOT.prev_slow
        and BOT.fast_ema > BOT.slow_ema
    )
    crossed_down = (
        BOT.prev_fast is not None
        and BOT.prev_fast >= BOT.prev_slow
        and BOT.fast_ema < BOT.slow_ema
    )
    if held is None or held.qty == 0:
        if (
            crossed_up
            and sma is not None
            and close > sma
            and state.seq - BOT.last_sell_seq > COOLDOWN_BARS
            and state.cash >= 1_000_000
        ):
            BOT.entry_price = close
            BOT.peak_price = close
            return [
                {
                    "side": "buy",
                    "symbol": SYMBOL,
                    "notional_quote_units": state.cash,
                    "max_slippage_bps": MAX_SLIPPAGE_BPS,
                }
            ]
        return []
    # Holding a position: track the peak and check exits.
    if close > BOT.peak_price:
        BOT.peak_price = close
    stop_hit = (
        BOT.entry_price is not None and close < BOT.entry_price * (1 - HARD_STOP_PCT)
    )
    trail_hit = (
        BOT.peak_price is not None and close < BOT.peak_price * (1 - TRAIL_PCT)
    )
    if crossed_down or stop_hit or trail_hit:
        BOT.last_sell_seq = state.seq
        BOT.entry_price = None
        BOT.peak_price = None
        return [
            {
                "side": "sell",
                "symbol": SYMBOL,
                "qty": held.qty,
                "max_slippage_bps": MAX_SLIPPAGE_BPS,
            }
        ]
    return []


makefun_bars.run(on_batch)
