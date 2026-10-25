"""Homework 5: option payoff functions and a live SPY option-chain snapshot."""
from datetime import date
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf


def intrinsic(kind, strike, spot):
    """Value if exercised immediately; `kind` is call or put."""
    if kind == "call":
        return np.maximum(np.asarray(spot) - strike, 0)
    if kind == "put":
        return np.maximum(strike - np.asarray(spot), 0)
    raise ValueError("kind must be 'call' or 'put'")


def extrinsic(kind, strike, spot, premium):
    """Premium paid for time and uncertainty after intrinsic value."""
    return np.asarray(premium) - intrinsic(kind, strike, spot)


def payoff(kind, strike, premium, spot):
    """Profit per share at expiration for a long or short call or put."""
    if kind == "long_call":
        return intrinsic("call", strike, spot) - premium
    if kind == "long_put":
        return intrinsic("put", strike, spot) - premium
    if kind == "short_call":
        return premium - intrinsic("call", strike, spot)
    if kind == "short_put":
        return premium - intrinsic("put", strike, spot)
    raise ValueError("kind must be long_call, long_put, short_call, or short_put")


def choose_expiries(expiries, today=None):
    """Choose the first listed expiry roughly one month and at least six months away."""
    today = pd.Timestamp(today or date.today())
    dates = pd.to_datetime(expiries)
    short = dates[dates >= today + pd.Timedelta(days=25)][0]
    long = dates[dates >= today + pd.Timedelta(days=180)][0]
    return short.strftime("%Y-%m-%d"), long.strftime("%Y-%m-%d")


def prepare_calls(calls, spot):
    """Keep quoted calls and calculate mid, intrinsic, and extrinsic values."""
    calls = calls.loc[(calls["bid"] > 0) & (calls["ask"] > 0), ["strike", "bid", "ask"]].copy()
    calls["mid"] = (calls["bid"] + calls["ask"]) / 2
    calls["intrinsic"] = intrinsic("call", calls["strike"].to_numpy(), spot)
    calls["extrinsic"] = calls["mid"] - calls["intrinsic"]
    return calls.sort_values("strike").reset_index(drop=True)


def print_near_spot(calls, spot, title):
    nearest = calls.assign(distance=(calls["strike"] - spot).abs()).nsmallest(10, "distance")
    nearest = nearest.sort_values("strike")
    print(f"\n{title}: ten call strikes nearest spot")
    print(nearest[["strike", "mid", "intrinsic", "extrinsic"]].to_string(
        index=False, formatters={column: "{:.2f}".format for column in ["strike", "mid", "intrinsic", "extrinsic"]}
    ))


def plot_payoffs(path="hw05_payoffs.png"):
    spots = np.linspace(60, 140, 401)
    kinds = ["long_call", "long_put", "short_call", "short_put"]
    fig, axes = plt.subplots(2, 2, figsize=(8, 6), sharex=True, sharey=True)
    for axis, kind in zip(axes.ravel(), kinds):
        axis.plot(spots, payoff(kind, 100, 6, spots), color="#174a7e", linewidth=2)
        axis.axvline(100, color="gray", linestyle="--", linewidth=1)
        axis.axhline(0, color="black", linewidth=0.8)
        axis.set_title(kind.replace("_", " ").title())
        axis.grid(alpha=0.25)
    fig.supxlabel("Spot price at expiry")
    fig.supylabel("Profit per share ($)")
    fig.suptitle("Option payoffs: strike 100, premium 6")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_extrinsic(short_calls, long_calls, short_expiry, long_expiry, spot,
                   path="hw05_extrinsic_curves.png"):
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.plot(short_calls["strike"], short_calls["extrinsic"], marker="o", markersize=2.5,
            linewidth=1.2, label=f"{short_expiry} calls")
    ax.plot(long_calls["strike"], long_calls["extrinsic"], marker="o", markersize=2.5,
            linewidth=1.2, label=f"{long_expiry} calls")
    ax.axvline(spot, color="black", linestyle="--", linewidth=1, label=f"Spot ${spot:.2f}")
    ax.axhline(0, color="gray", linewidth=0.8)
    ax.set(xlabel="Strike ($)", ylabel="Extrinsic value ($ per share)",
           title="SPY call extrinsic value by strike")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main():
    print("Q1  Payoffs (strike $100, premium $6)")
    for kind in ["long_call", "long_put", "short_call", "short_put"]:
        values = ", ".join(f"spot {spot}: ${float(payoff(kind, 100, 6, spot)):+.2f}" for spot in [80, 100, 120])
        print(f"  {kind:<10} {values}")
    plot_payoffs()

    ticker_name = "SPY"
    ticker = yf.Ticker(ticker_name)
    expiries = ticker.options
    if not expiries:
        raise RuntimeError("No option expiries returned by Yahoo Finance.")
    short_expiry, long_expiry = choose_expiries(expiries)
    history = ticker.history(period="5d", auto_adjust=False)
    spot = float(history["Close"].dropna().iloc[-1])
    short_chain = ticker.option_chain(short_expiry)
    long_chain = ticker.option_chain(long_expiry)
    short_calls = prepare_calls(short_chain.calls, spot)
    long_calls = prepare_calls(long_chain.calls, spot)
    Path("data").mkdir(exist_ok=True)
    short_calls.to_csv(f"data/hw05_spy_calls_{short_expiry}.csv", index=False)
    long_calls.to_csv(f"data/hw05_spy_calls_{long_expiry}.csv", index=False)

    print(f"\nQ3  {ticker_name} | short expiry {short_expiry} | long expiry {long_expiry}")
    print(f"    Current spot (latest close): ${spot:.2f}")
    print(f"    Short chain: {len(short_chain.calls)} calls, {len(short_chain.puts)} puts")
    print(f"    Long chain:  {len(long_chain.calls)} calls, {len(long_chain.puts)} puts")
    print_near_spot(short_calls, spot, f"Q4  {short_expiry}")
    print_near_spot(long_calls, spot, f"Q6  {long_expiry}")
    short_max = short_calls.loc[short_calls["extrinsic"].idxmax()]
    long_max = long_calls.loc[long_calls["extrinsic"].idxmax()]
    print(f"\nQ5  Largest short-expiry extrinsic: ${short_max['extrinsic']:.2f} at strike ${short_max['strike']:.2f}; spot ${spot:.2f}")
    print(f"Q6  Largest long-expiry extrinsic:  ${long_max['extrinsic']:.2f} at strike ${long_max['strike']:.2f}; spot ${spot:.2f}")
    plot_extrinsic(short_calls, long_calls, short_expiry, long_expiry, spot)


if __name__ == "__main__":
    main()
