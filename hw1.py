"""Homework 1: compare one year of Palantir and S&P 500 prices.

Run with: python3 hw1.py
The script prints the requested statistics and saves hw1_plot.png.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

TICKER = "PLTR"
BENCHMARK = "SPY"


def main() -> None:
    # Exclude today so the analysis cannot use an incomplete trading day.
    end_date = pd.Timestamp.today().normalize()
    start_date = end_date - pd.DateOffset(years=1)

    raw = yf.download(
        [TICKER, BENCHMARK],
        start=start_date,
        end=end_date,
        auto_adjust=False,
        progress=False,
    )
    prices = raw["Close"][[TICKER, BENCHMARK]].dropna(how="any")

    if prices.empty:
        raise RuntimeError("No complete closing-price data was downloaded.")

    print(f"Tickers: {TICKER} and {BENCHMARK}")
    print(f"Trading days: {len(prices)}")
    print(f"First date: {prices.index[0].date()}")
    print(f"Last date: {prices.index[-1].date()}\n")

    daily_returns = prices.pct_change().dropna()
    summary = pd.DataFrame(
        {
            "last close": prices.iloc[-1],
            "one-year return": prices.iloc[-1] / prices.iloc[0] - 1,
            "annualised volatility": daily_returns.std() * np.sqrt(252),
        }
    )

    for symbol, row in summary.iterrows():
        print(
            f"{symbol}: last close ${row['last close']:.2f}; "
            f"return {row['one-year return']:.2%}; "
            f"annualised volatility {row['annualised volatility']:.2%}"
        )

    rebased = prices / prices.iloc[0] * 100
    ax = rebased.plot(figsize=(11, 6), linewidth=2)
    ax.set_title(f"One-year performance: {TICKER} vs. {BENCHMARK}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Rebased price (start = 100)")
    ax.legend(title="Ticker")
    ax.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("hw1_plot.png", dpi=200)
    plt.close()

    ticker_returns = daily_returns[TICKER]
    largest_move_date = ticker_returns.abs().idxmax()
    largest_move = ticker_returns.loc[largest_move_date]
    direction = "up" if largest_move > 0 else "down"
    print(
        f"\n{TICKER}'s largest single-day move was {direction} "
        f"{abs(largest_move):.2%} on {largest_move_date.date()}."
    )
    print("Saved chart to hw1_plot.png")


if __name__ == "__main__":
    main()
