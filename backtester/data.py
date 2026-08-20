"""Load and clean the S&P 500 monthly dataset (Shiller / Core Datasets).

Source: https://github.com/datasets/s-and-p-500  (public-domain data,
originally compiled by Prof. Robert Shiller, Yale).

Columns used:
    Date                  month start
    SP500                 nominal price index level
    Dividend              trailing-12-month dividend (annualised, $ level)
    Long Interest Rate    10-year rate, % p.a. (used as the "cash" yield)
"""

from pathlib import Path

import pandas as pd

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "sp500_monthly.csv"


def load(total_return: bool = False) -> pd.DataFrame:
    """Return a DataFrame indexed by month with `price`, `ret` and `cash_ret`.

    total_return=False -> price returns only, full history (1871 - today).
    total_return=True  -> price + dividend returns, truncated where the
                          source stops publishing dividends (mid-2023).
    """
    df = pd.read_csv(DATA_FILE, parse_dates=["Date"])
    df = df.set_index("Date").sort_index()

    # The source publishes price promptly but dividends / rates with a lag,
    # padding recent months with 0.  Treat those zeros as missing.
    for col in ["Dividend", "Long Interest Rate"]:
        df[col] = df[col].replace(0.0, pd.NA)

    out = pd.DataFrame(index=df.index)
    out["price"] = df["SP500"]
    out["ret"] = out["price"].pct_change()

    if total_return:
        # Shiller's Dividend column is the annualised dividend level, so one
        # month's dividend cash-flow is Dividend/12, earned on last month's price.
        monthly_div = (df["Dividend"] / 12.0) / out["price"].shift(1)
        out["ret"] = out["ret"] + monthly_div
        out = out.loc[: df["Dividend"].last_valid_index()]

    # Cash earns the long rate (a simple, conservative proxy), forward-filled
    # over the months the source has not published yet.
    rate = df["Long Interest Rate"].ffill()
    out["cash_ret"] = rate / 100.0 / 12.0

    return out.dropna(subset=["ret"])
