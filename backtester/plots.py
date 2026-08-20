"""Charts. Dark theme, colorblind-checked palette."""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd

# palette (validated for color-vision-deficiency separation on this surface)
SURFACE = "#1a1a19"
INK = "#ffffff"
INK2 = "#c3c2b7"
MUTED = "#898781"
GRID = "#2c2c2a"
SERIES = {"Buy & Hold": "#3987e5", "SMA-10 Trend": "#d95926", "12M Momentum": "#199e70"}

plt.rcParams.update(
    {
        "figure.facecolor": SURFACE,
        "axes.facecolor": SURFACE,
        "savefig.facecolor": SURFACE,
        "text.color": INK2,
        "axes.edgecolor": GRID,
        "axes.labelcolor": INK2,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "axes.grid": True,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "font.family": "sans-serif",
        "font.size": 11,
    }
)

OUT = Path(__file__).resolve().parent.parent / "outputs"


def _style(ax, title):
    ax.set_title(title, color=INK, fontsize=14, fontweight="bold", loc="left", pad=14)
    ax.grid(axis="x", visible=False)
    ax.margins(x=0.01)


def equity_curves(results: dict, fname: str = "equity_curves.png"):
    fig, ax = plt.subplots(figsize=(10.5, 5.6))
    for name, res in results.items():
        ax.plot(res.index, res["equity"], color=SERIES[name], lw=2, label=name)
        # direct label at the line end
        ax.annotate(
            f" {name}  {res['equity'].iloc[-1]:,.0f}x",
            xy=(res.index[-1], res["equity"].iloc[-1]),
            color=SERIES[name], fontsize=10, fontweight="bold", va="center",
        )
    ax.set_yscale("log")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}x"))
    _style(ax, "Growth of $1, log scale")
    ax.legend(frameon=False, labelcolor=INK2, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / fname, dpi=160, bbox_inches="tight")
    plt.close(fig)


def drawdowns(results: dict, fname: str = "drawdowns.png"):
    fig, ax = plt.subplots(figsize=(10.5, 4.4))
    for name, res in results.items():
        ax.plot(res.index, res["drawdown"] * 100, color=SERIES[name], lw=1.6, label=name)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
    _style(ax, "Drawdown from peak")
    ax.legend(frameon=False, labelcolor=INK2, loc="lower left")
    fig.tight_layout()
    fig.savefig(OUT / fname, dpi=160, bbox_inches="tight")
    plt.close(fig)


def signal_zoom(data: pd.DataFrame, window: int = 10,
                start: str = "1997", end: str = "2012",
                fname: str = "signal_zoom.png"):
    """Price vs its SMA with the out-of-market months shaded --
    shows the strategy stepping aside in the dot-com and 2008 crashes."""
    px = data["price"]
    sma = px.rolling(window).mean()
    invested = (px > sma).shift(1).fillna(False).astype(bool)

    px, sma, invested = px.loc[start:end], sma.loc[start:end], invested.loc[start:end]

    fig, ax = plt.subplots(figsize=(10.5, 4.8))
    ax.fill_between(px.index, 0, 1, where=~invested, transform=ax.get_xaxis_transform(),
                    color="#45443f", alpha=0.9, linewidth=0, label="In cash")
    ax.plot(px.index, px, color=SERIES["Buy & Hold"], lw=2, label="S&P 500")
    ax.plot(sma.index, sma, color=SERIES["SMA-10 Trend"], lw=2, label=f"{window}-month SMA")
    _style(ax, "The trend filter in action, 1997-2012")
    ax.legend(frameon=False, labelcolor=INK2, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / fname, dpi=160, bbox_inches="tight")
    plt.close(fig)
