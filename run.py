"""Run the full study: every strategy over the full history, metrics table,
charts, and a markdown results file.

Usage:
    python run.py                  # price returns, 1871 - today
    python run.py --total-return   # incl. dividends, 1871 - mid-2023
"""

import argparse

import pandas as pd

from backtester import data as data_mod
from backtester import engine, metrics, plots
from backtester.strategies import STRATEGIES


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--total-return", action="store_true",
                        help="include dividends (history ends mid-2023)")
    args = parser.parse_args()

    data = data_mod.load(total_return=args.total_return)
    span = f"{data.index[0]:%b %Y} - {data.index[-1]:%b %Y}"
    mode = "total return (incl. dividends)" if args.total_return else "price return"
    print(f"S&P 500 monthly, {span}, {len(data)} months, {mode}\n")

    results, table = {}, {}
    for name, strat in STRATEGIES.items():
        res = engine.run(data, strat(data["price"]))
        results[name] = res
        table[name] = metrics.summarize(res, data["cash_ret"])

    df = pd.DataFrame(table)
    print(df.to_string())

    plots.equity_curves(results)
    plots.drawdowns(results)
    plots.signal_zoom(data)

    out = plots.OUT / ("results_total_return.md" if args.total_return else "results.md")
    out.write_text(f"# Results - S&P 500 monthly, {span} ({mode})\n\n"
                   + df.to_markdown() + "\n")
    print(f"\nCharts + results written to {plots.OUT}/")


if __name__ == "__main__":
    main()
