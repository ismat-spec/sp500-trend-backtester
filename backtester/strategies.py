"""Trading strategies.

Every strategy is a function: price series -> position series (0 or 1),
where 1 = fully invested in the index and 0 = parked in cash.

The position is shifted by one month before it is applied: a signal
computed with this month's closing data can only be traded NEXT month.
Skipping that shift is look-ahead bias, the classic backtesting mistake.
"""

import pandas as pd


def buy_and_hold(price: pd.Series) -> pd.Series:
    """Always invested. The benchmark every strategy has to beat."""
    return pd.Series(1.0, index=price.index)


def sma_timing(price: pd.Series, window: int = 10) -> pd.Series:
    """Faber-style trend filter: invested while price sits above its
    `window`-month simple moving average, in cash while below it."""
    sma = price.rolling(window).mean()
    signal = (price > sma).astype(float)
    return signal.shift(1).fillna(0.0)


def tsmom(price: pd.Series, lookback: int = 12) -> pd.Series:
    """Time-series momentum: invested while the trailing `lookback`-month
    return is positive, in cash while it is negative."""
    signal = (price > price.shift(lookback)).astype(float)
    return signal.shift(1).fillna(0.0)


STRATEGIES = {
    "Buy & Hold": buy_and_hold,
    "SMA-10 Trend": sma_timing,
    "12M Momentum": tsmom,
}
