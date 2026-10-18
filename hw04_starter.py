"""Homework 4: a close-to-close, no-lookahead strategy backtester.

Run with --train-only to examine candidate rules without downloading the test
period. The default run evaluates the locked rule on the test period once.
"""
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

LOOKBACK = 60
SPLIT_DATE = "2011-09-09"  # September 10 was a Saturday.
SNAPSHOT = Path("data/hw04_sp500tr.csv")


def download_prices(end=None):
    """Download total-return closes. `end` is exclusive when supplied."""
    frame = yf.download("^SP500TR", start="1990-01-01", end=end,
                        auto_adjust=False, progress=False)
    if frame.empty:
        raise RuntimeError("Yahoo Finance returned no ^SP500TR prices.")
    prices = frame["Close"]
    if isinstance(prices, pd.DataFrame):
        prices = prices.iloc[:, 0]
    prices = prices.dropna().astype(float)
    prices.name = "Close"
    return prices


def load_and_split(split_date=SPLIT_DATE, prices=None, warmup=LOOKBACK):
    """Split at a trading close; test includes warmup history ending at that close."""
    if prices is None:
        prices = download_prices()
    prices = pd.Series(prices).sort_index()
    split = pd.Timestamp(split_date)
    if split not in prices.index:
        raise ValueError("The split date must be an observed trading close.")
    split_pos = prices.index.get_loc(split)
    if split_pos < warmup - 1 or split_pos >= len(prices) - 1:
        raise ValueError("Not enough warmup history or no out-of-sample data.")
    return prices.iloc[:split_pos + 1].copy(), prices.iloc[split_pos - warmup + 1:].copy()


def always_hold(window):
    return True


def always_cash(window):
    return False


def make_random_hold(p=0.7, seed=0):
    rng = np.random.default_rng(seed)

    def random_hold(window):
        return bool(rng.random() < p)
    return random_hold


def five_day_reversal(window):
    """Hold unless the return from five sessions ago to today is positive."""
    return bool(window[-1] <= window[-6])


def moving_average_60(window):
    return bool(window[-1] > np.mean(window[-60:]))


def moving_average_30(window):
    return bool(window[-1] > np.mean(window[-30:]))


def momentum_30(window):
    return bool(window[-1] > window[-31])


def reversal_15(window):
    return bool(window[-1] <= window[-16])


def trend_and_pullback(window):
    return bool(window[-1] > np.mean(window[-60:]) and window[-1] <= window[-6])


CANDIDATES = [
    ("Close above 60-day moving average", moving_average_60),
    ("Close above 30-day moving average", moving_average_30),
    ("Positive trailing 30-day return", momentum_30),
    ("Nonpositive trailing 15-day return", reversal_15),
    ("Above 60-day average AND nonpositive 5-day return", trend_and_pullback),
]


def my_strategy(window):
    """Hold when the latest close is above its 60-day moving average; otherwise cash."""
    return moving_average_60(window)


def backtest(prices, strategy, lookback=LOOKBACK):
    """Use known closes through today to decide exposure to tomorrow's return."""
    values = np.asarray(prices, dtype=float)
    if len(values) <= lookback or np.any(~np.isfinite(values)) or np.any(values <= 0):
        raise ValueError("Need more than lookback finite, positive closes.")
    holdings = []
    portfolio = [1.0]
    index = [1.0]
    for i in range(lookback - 1, len(values) - 1):
        # The last element is today's close; tomorrow's close is not in the slice.
        hold = bool(strategy(values[i - lookback + 1:i + 1].copy()))
        daily_gross = values[i + 1] / values[i]
        holdings.append(hold)
        portfolio.append(portfolio[-1] * (daily_gross if hold else 1.0))
        index.append(index[-1] * daily_gross)
    portfolio = np.asarray(portfolio)
    index = np.asarray(index)
    days = len(holdings)
    drawdown = portfolio / np.maximum.accumulate(portfolio) - 1
    index_drawdown = index / np.maximum.accumulate(index) - 1
    return {
        "total_return": float(portfolio[-1] - 1),
        "annualised_return": float(portfolio[-1] ** (252 / days) - 1),
        "max_drawdown": float(drawdown.min()),
        "fraction_invested": float(np.mean(holdings)),
        "index_total_return": float(index[-1] - 1),
        "index_annualised_return": float(index[-1] ** (252 / days) - 1),
        "index_max_drawdown": float(index_drawdown.min()),
        "portfolio": portfolio,
        "index": index,
        "days": days,
    }


def describe_result(label, result):
    print(f"{label:<28} total {result['total_return']:+.2%}  annual {result['annualised_return']:+.2%}")


def plot_equity(prices, result, title, path):
    dates = prices.index[LOOKBACK - 1:]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(dates, result["portfolio"], label="Strategy", color="#164d80")
    ax.plot(dates, result["index"], label="Index buy-and-hold", color="#bf5b28")
    ax.set(title=title, ylabel="Portfolio value (starting at 1)", xlabel="Date")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train-only", action="store_true", help="Do not download or inspect the holdout period")
    parser.add_argument("--snapshot", action="store_true", help="Use the saved dataset instead of downloading new data")
    args = parser.parse_args()
    if args.train_only:
        train = download_prices(end="2011-09-10")
        print(f"Training closes: {len(train):,}; mean: {train.mean():,.2f}")
    else:
        if args.snapshot:
            prices = pd.read_csv(SNAPSHOT, index_col=0, parse_dates=True)["Close"].dropna()
        else:
            prices = download_prices()
            SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
            prices.to_csv(SNAPSHOT, float_format="%.12g")
        train, test = load_and_split(prices=prices)
        print(f"Training closes: {len(train):,}; mean: {train.mean():,.2f}")
        print(f"Test closes including 60 warmup closes: {len(test):,}; mean: {test.mean():,.2f}")
        print(f"First test return: {test.index[LOOKBACK - 1].date()} to {test.index[LOOKBACK].date()}")

    print("\nTraining controls:")
    for label, strategy in [("Always hold", always_hold), ("Always cash", always_cash),
                            ("Random 70%, seed 0", make_random_hold(0.7, seed=0)),
                            ("5-day reversal", five_day_reversal)]:
        result = backtest(train, strategy)
        describe_result(label, result)
        if label == "Always hold" and not args.train_only:
            plot_equity(train, result, "Training: always hold versus index", "hw04_train_control.png")
    print("\nEvery training candidate:")
    for label, strategy in CANDIDATES:
        print(f"{label}: {backtest(train, strategy)['annualised_return']:+.2%} annualised")
    if args.train_only:
        return

    print("\nFinal rule: " + my_strategy.__doc__)
    train_result = backtest(train, my_strategy)
    describe_result("Final rule training", train_result)
    plot_equity(train, train_result, "Training: final strategy versus index", "hw04_train_strategy.png")
    test_result = backtest(test, my_strategy)  # One final-strategy holdout evaluation.
    describe_result("Final rule test", test_result)
    print(f"Test index                   total {test_result['index_total_return']:+.2%}  annual {test_result['index_annualised_return']:+.2%}")
    print(f"Test max drawdown: strategy {test_result['max_drawdown']:.2%}; index {test_result['index_max_drawdown']:.2%}")
    print(f"Test fraction invested: {test_result['fraction_invested']:.2%}")
    plot_equity(test, test_result, "Holdout: final strategy versus index", "hw04_test_strategy.png")
    print(f"Latest signal using {prices.index[-1].date()} close: {'HOLD' if my_strategy(prices.iloc[-LOOKBACK:].to_numpy()) else 'CASH'}")


if __name__ == "__main__":
    main()
