"""R2 bot for make.fun btc-race-24h-20261123-0511: one-trade trend rider.

Idea (written from scratch for this entry, no other entry's code read):
the dev window's money was one sustained 6-hour uptrend followed by flat
chop. Fast EMA crosses whipsaw on 1-minute bars (the kit's own ema-cross
baseline loses -$114.83 in 76 trades); cross-down / momentum-reversal exits
do the same. So this bot enters ONCE, on a confirmed hourly move, then
holds with a wide trailing stop and never exits on a cross.

  Entry (flat): 60-bar return > +0.5% AND 24-bar return > 0 AND the close
    above SMA(120) once the average exists (before bar 120 the average
    does not gate). Full size: 100% of equity.
  Exit: trailing stop 2.0% under the highest close since entry.
  Safety: if the position is still below breakeven 120 bars (2h) after
    entry, the trend thesis was wrong — exit. No re-entry for 120 bars
    after any exit, so a bad day cannot bleed through repeated bounces.

Long only, no leverage, no shorts. Deterministic: float math on closes
only, no clock, no environment, no randomness, so two runs agree exactly.
Standard library only, plus the kit's vendored bars shim.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"

# Entry: the hourly move that confirms a trend, and the short-term move
# still pointing the same way.
ENTRY_R60_BPS = 50          # 60-bar return above +0.5%
ENTRY_R24_MIN = 0.0         # 24-bar return above 0
SMA_BARS = 120              # 2-hour average; gates entries once it exists

# Exit: a trailing stop wide enough to survive the chop (1-2% ranges),
# a time stop for trades that never follow through, and a re-entry pause.
TRAILING_STOP = 0.02        # 2.0% under the peak close since entry
TIME_STOP_BARS = 120        # 2 hours
COOLDOWN_BARS = 120         # no re-entry for 2 hours after an exit
MAX_SLIPPAGE_BPS = 300      # 3% past the close decided on; 1-min gaps stay well under it

_closes = []
_peak = None        # highest close seen since entry
_entry_cost = None  # cash spent on the open position (notional, fees included)
_entry_seq = None   # batch seq of the entry decision
_last_exit_seq = -10 ** 9


def _return_bars(n):
    """Close now over the close n bars back, minus one; None without history."""
    if len(_closes) <= n:
        return None
    return _closes[-1] / _closes[-1 - n] - 1.0


def _sma(n):
    """Simple mean of the last n closes; None without enough history."""
    if len(_closes) < n:
        return None
    return sum(_closes[-n:]) / n


def on_batch(state, batch):
    close = state.close(SYMBOL)
    if close is not None:
        _closes.append(close)
    if state.warming_up:
        return []

    global _peak, _entry_cost, _entry_seq, _last_exit_seq

    if close is None:
        return []
    held = state.positions.get(SYMBOL)
    seq = state.seq

    if held is not None:
        # Track the peak close since entry, then check the exits.
        if _peak is None or close > _peak:
            _peak = close
        exit_now = False
        if _peak is not None and close < _peak * (1.0 - TRAILING_STOP):
            exit_now = True
        if not exit_now and _entry_seq is not None and _entry_cost is not None:
            if seq - _entry_seq >= TIME_STOP_BARS:
                if state.value(SYMBOL, held.qty) < _entry_cost:
                    exit_now = True
        if exit_now:
            _peak = None
            _entry_cost = None
            _entry_seq = None
            _last_exit_seq = seq
            return [{"side": "sell", "symbol": SYMBOL, "qty": held.qty,
                     "max_slippage_bps": MAX_SLIPPAGE_BPS}]
        return []

    # Flat: enter only on a confirmed hourly move, with the short-term
    # move agreeing and the price above its 2-hour average.
    if seq - _last_exit_seq < COOLDOWN_BARS:
        return []
    r60 = _return_bars(60)
    r24 = _return_bars(24)
    sma = _sma(SMA_BARS)
    if r60 is None or r60 <= ENTRY_R60_BPS / 10000.0:
        return []
    if r24 is None or r24 <= ENTRY_R24_MIN:
        return []
    if sma is not None and close <= sma:
        return []
    notional = state.equity if state.equity < state.cash else state.cash
    if notional < 1_000_000:
        return []
    _peak = close
    _entry_cost = notional
    _entry_seq = seq
    return [{"side": "buy", "symbol": SYMBOL,
             "notional_quote_units": notional,
             "max_slippage_bps": MAX_SLIPPAGE_BPS}]


makefun_bars.run(on_batch)
