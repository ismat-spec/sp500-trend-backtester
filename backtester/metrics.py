"""Performance metrics computed from a backtest result."""

import numpy as np
import pandas as pd

MONTHS = 12


def summarize(result: pd.DataFrame, cash_ret: pd.Series) -> dict:
    r = result["ret"].dropna()
    equity = result["equity"].dropna()
    years = len(r) / MONTHS

    cagr = equity.iloc[-1] ** (1.0 / years) - 1.0
    vol = r.std() * np.sqrt(MONTHS)

    excess = r - cash_ret.reindex(r.index).fillna(0.0)
    sharpe = excess.mean() / excess.std() * np.sqrt(MONTHS)

    max_dd = result["drawdown"].min()

    return {
        "CAGR": f"{cagr:.2%}",
        "Volatility": f"{vol:.2%}",
        "Sharpe": f"{sharpe:.2f}",
        "Max drawdown": f"{max_dd:.1%}",
        "Worst month": f"{r.min():.1%}",
        "Time in market": f"{result['position'].mean():.0%}",
        "Trades": int(result["position"].diff().abs().sum()),
    }
