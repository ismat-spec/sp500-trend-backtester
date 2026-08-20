"""The backtest engine: turn positions into a portfolio equity curve."""

import pandas as pd


def run(data: pd.DataFrame, position: pd.Series) -> pd.DataFrame:
    """Apply a 0/1 position series to the asset returns.

    While invested (1) the portfolio earns the index return; while flat (0)
    it earns the cash yield instead of nothing, which is what an investor
    would actually do with the money.
    """
    pos = position.reindex(data.index).fillna(0.0)

    strat_ret = pos * data["ret"] + (1.0 - pos) * data["cash_ret"]
    equity = (1.0 + strat_ret).cumprod()

    out = pd.DataFrame(
        {
            "position": pos,
            "ret": strat_ret,
            "equity": equity,
            "drawdown": equity / equity.cummax() - 1.0,
        }
    )
    return out
