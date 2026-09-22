"""Homework 2 starter — Algory QI Education, Fall 2026

Fill in every function marked TODO. Do not rename them: the checker looks for
these exact names. Run `python check_hw02.py` before you submit.
"""
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------------------------- Q1
def present_value(cash_flows, rate):
    """Present value of a list of cash flows, the first arriving in one year.

    present_value([10, 15, 20], 0.10) -> 36.51
    """
    return sum(cash_flow / (1 + rate) ** year
               for year, cash_flow in enumerate(cash_flows, start=1))


# ---------------------------------------------------------------- Q2
def bond_price(face, coupon_rate, years, market_rate):
    """Price of a bond paying an annual coupon and repaying face at maturity.

    The final year pays the coupon AND the face value. That is the usual bug.
    bond_price(1000, 0.04, 10, 0.04) -> exactly 1000.0
    """
    coupon = face * coupon_rate
    cash_flows = [coupon] * years
    cash_flows[-1] += face
    return present_value(cash_flows, market_rate)


# ---------------------------------------------------------------- Q4/Q5
def annualised_return(prices):
    """Annualised return from a price series, using 252 trading days."""
    prices = pd.Series(prices).dropna()
    if len(prices) < 2:
        raise ValueError("At least two prices are required.")
    trading_days = len(prices) - 1
    return (prices.iloc[-1] / prices.iloc[0]) ** (252 / trading_days) - 1


def annualised_volatility(prices):
    """Annualised standard deviation of daily returns."""
    returns = pd.Series(prices).pct_change().dropna()
    if len(returns) < 2:
        raise ValueError("At least three prices are required.")
    return returns.std(ddof=1) * np.sqrt(252)


def beta(stock_prices, market_prices):
    """Beta of a stock against the market.

    Covariance of the two RETURN series divided by the variance of the market's.
    Computing this on prices instead of returns is a common and silent error.
    beta(spy, spy) -> 1.0
    """
    stock_returns = pd.Series(stock_prices).pct_change()
    market_returns = pd.Series(market_prices).pct_change()
    paired_returns = pd.concat(
        [stock_returns.rename("stock"), market_returns.rename("market")], axis=1
    ).dropna()
    if len(paired_returns) < 2:
        raise ValueError("At least two matched daily returns are required.")
    return paired_returns["stock"].cov(paired_returns["market"]) / paired_returns["market"].var()


# ---------------------------------------------------------------- your answers
def main():
    """Everything the assignment asks you to print goes here."""
    print(f"Q1  present_value([10, 15, 20], 0.10) = {present_value([10, 15, 20], 0.10):.2f}")

    face, coupon_rate, years = 1000, 0.04, 10
    rates = [0.02, 0.04, 0.0496]
    print("\nQ3  10-year, 4% coupon bond prices")
    for market_rate in rates:
        price = bond_price(face, coupon_rate, years, market_rate)
        print(f"  Market rate {market_rate:.2%}: ${price:,.2f}")

    curve_rates = np.linspace(0, 0.10, 201)
    curve_prices = [bond_price(face, coupon_rate, years, rate) for rate in curve_rates]
    plt.figure(figsize=(7, 4.5))
    plt.plot(curve_rates * 100, curve_prices, color="navy", linewidth=2)
    plt.xlabel("Market rate (%)")
    plt.ylabel("Bond price ($)")
    plt.title("Price of a 10-Year 4% Coupon Bond")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig("hw02_bond_price_curve.png", dpi=200)
    plt.close()
    print("  Plot saved as hw02_bond_price_curve.png")
    print("  The downward-sloping curve is convex: an equal fall in rates raises price more than an equal rise lowers it.")

    # AAPL (technology), JPM (financials), and XOM (energy) are distinct sectors.
    tickers = ["AAPL", "JPM", "XOM"]
    all_tickers = tickers + ["SPY"]
    closes = yf.download(
        all_tickers, period="5y", interval="1d", auto_adjust=False,
        progress=False, group_by="column"
    )["Close"].dropna()

    print("\nQ4  Trading days in five years of daily closing prices")
    for ticker in all_tickers:
        print(f"  {ticker}: {closes[ticker].count()}")

    metrics = pd.DataFrame(index=tickers, columns=["Annualised Return", "Annualised Volatility", "Beta"])
    for ticker in tickers:
        metrics.loc[ticker] = [
            annualised_return(closes[ticker]),
            annualised_volatility(closes[ticker]),
            beta(closes[ticker], closes["SPY"]),
        ]
    metrics = metrics.astype(float)
    print("\nQ5  Risk and return metrics")
    print(metrics.to_string(formatters={
        "Annualised Return": "{:.2%}".format,
        "Annualised Volatility": "{:.2%}".format,
        "Beta": "{:.2f}".format,
    }))

    print("\nQ6  Rankings (highest first)")
    print("  By beta: " + " > ".join(metrics.sort_values("Beta", ascending=False).index))
    print("  By volatility: " + " > ".join(metrics.sort_values("Annualised Volatility", ascending=False).index))


if __name__ == "__main__":
    main()
