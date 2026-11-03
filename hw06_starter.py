"""Homework 6: payoff combinations, Black-Scholes, and implied volatility."""
from datetime import date
from math import erf, exp, log, sqrt
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf


def normal_cdf(x):
    return 0.5 * (1 + erf(x / sqrt(2)))


def black_scholes(kind, spot, strike, years, rate, vol):
    """Price a European call or put; time is in years and rate/vol are decimals."""
    if spot <= 0 or strike <= 0 or years <= 0 or vol <= 0:
        raise ValueError("spot, strike, years, and vol must be positive")
    d1 = (log(spot / strike) + (rate + 0.5 * vol ** 2) * years) / (vol * sqrt(years))
    d2 = d1 - vol * sqrt(years)
    if kind == "call":
        return spot * normal_cdf(d1) - strike * exp(-rate * years) * normal_cdf(d2)
    if kind == "put":
        return strike * exp(-rate * years) * normal_cdf(-d2) - spot * normal_cdf(-d1)
    raise ValueError("kind must be 'call' or 'put'")


def implied_volatility(price, spot, strike, years, rate, kind):
    """Solve Black-Scholes implied volatility by bisection."""
    if price <= 0 or years <= 0:
        return np.nan
    lower_bound = max(spot - strike * exp(-rate * years), 0) if kind == "call" else max(strike * exp(-rate * years) - spot, 0)
    upper_bound = spot if kind == "call" else strike * exp(-rate * years)
    if not lower_bound <= price <= upper_bound:
        return np.nan
    low, high = 0.001, 5.0
    if price < black_scholes(kind, spot, strike, years, rate, low) or price > black_scholes(kind, spot, strike, years, rate, high):
        return np.nan
    for _ in range(100):
        mid = (low + high) / 2
        if black_scholes(kind, spot, strike, years, rate, mid) < price:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def payoff(kind, strike, premium, spot):
    """Expiry profit per share for the four elementary option positions."""
    spot = np.asarray(spot)
    call_value = np.maximum(spot - strike, 0)
    put_value = np.maximum(strike - spot, 0)
    values = {
        "long_call": call_value - premium,
        "long_put": put_value - premium,
        "short_call": premium - call_value,
        "short_put": premium - put_value,
    }
    if kind not in values:
        raise ValueError("unknown option kind")
    return values[kind]


def covered_call(entry, strike, premium, spot):
    """Per-share profit: long stock plus one short call per 100 shares."""
    return np.asarray(spot) - entry + payoff("short_call", strike, premium, spot)


def protective_put(entry, strike, premium, spot):
    return np.asarray(spot) - entry + payoff("long_put", strike, premium, spot)


def long_straddle(strike, call_premium, put_premium, spot):
    return payoff("long_call", strike, call_premium, spot) + payoff("long_put", strike, put_premium, spot)


def bull_call_spread(low_strike, low_premium, high_strike, high_premium, spot):
    return payoff("long_call", low_strike, low_premium, spot) + payoff("short_call", high_strike, high_premium, spot)


def plot_combinations(path="hw06_combinations.png"):
    spots = np.linspace(0, 160, 641)
    positions = [
        ("Covered call", covered_call(100, 105, 4, spots)),
        ("Protective put", protective_put(100, 95, 3, spots)),
        ("Long straddle", long_straddle(100, 6, 6, spots)),
        ("Bull call spread", bull_call_spread(95, 8, 105, 4, spots)),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(8, 6), sharex=True)
    for axis, (name, profits) in zip(axes.ravel(), positions):
        axis.plot(spots, profits, color="#174a7e", linewidth=2)
        axis.axhline(0, color="black", linewidth=0.8)
        axis.grid(alpha=0.25)
        axis.set_title(name)
    fig.supxlabel("Spot price at expiry")
    fig.supylabel("Profit per share ($)")
    fig.suptitle("Combination-strategy payoffs")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def choose_expiry(expiries, today=None):
    today = pd.Timestamp(today or date.today())
    options = pd.to_datetime(expiries)
    return options[options >= today + pd.Timedelta(days=25)][0].strftime("%Y-%m-%d")


def get_live_iv_data(ticker_name="SPY", rate=0.04):
    ticker = yf.Ticker(ticker_name)
    history = ticker.history(period="3mo", auto_adjust=False)
    spot = float(history["Close"].dropna().iloc[-1])
    last_close_date = pd.Timestamp(history.index[-1]).tz_localize(None).normalize()
    expiry = choose_expiry(ticker.options, today=last_close_date)
    years = max((pd.Timestamp(expiry) - last_close_date).days / 365, 1 / 365)
    calls = ticker.option_chain(expiry).calls.copy()
    calls = calls.loc[(calls["bid"] > 0) & (calls["ask"] > 0), ["strike", "bid", "ask"]].copy()
    calls["mid"] = (calls["bid"] + calls["ask"]) / 2
    calls["implied_volatility"] = [
        implied_volatility(mid, spot, strike, years, rate, "call")
        for strike, mid in zip(calls["strike"], calls["mid"])
    ]
    calls = calls.replace([np.inf, -np.inf], np.nan).dropna(subset=["implied_volatility"])
    return spot, last_close_date, expiry, years, calls.sort_values("strike").reset_index(drop=True), history


def plot_iv_smile(calls, spot, expiry, path="hw06_iv_smile.png"):
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.plot(calls["strike"], calls["implied_volatility"] * 100, marker="o", markersize=3,
            linewidth=1.2, color="#174a7e")
    ax.axvline(spot, color="black", linestyle="--", linewidth=1, label=f"Spot ${spot:.2f}")
    ax.set(xlabel="Strike ($)", ylabel="Implied volatility (%)",
           title=f"SPY call implied-volatility smile: {expiry}")
    ax.grid(alpha=0.25)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main():
    print("Q1  Combination metrics (per share)")
    metrics = [
        ("Covered call (stock 100, short 105 call for 4)", "$9.00", "-$96.00", "$96.00"),
        ("Protective put (stock 100, long 95 put for 3)", "Unlimited", "-$8.00", "$103.00"),
        ("Long straddle (100 calls and puts, 6 each)", "Unlimited", "-$12.00", "$88.00, $112.00"),
        ("Bull call spread (long 95 for 8, short 105 for 4)", "$6.00", "-$4.00", "$99.00"),
    ]
    for name, max_profit, max_loss, break_evens in metrics:
        print(f"  {name}\n    max profit {max_profit}; max loss {max_loss}; break-even(s) {break_evens}")
    plot_combinations()
    print("\nQ3  Black-Scholes: call = {:.2f}; put = {:.2f}".format(
        black_scholes("call", 100, 100, 1, 0.04, 0.25), black_scholes("put", 100, 100, 1, 0.04, 0.25)))
    own_call = black_scholes("call", 100, 100, 1, 0.04, 0.25)
    print("Q4  IV recovered from own call price = {:.4f}".format(implied_volatility(own_call, 100, 100, 1, 0.04, "call")))

    spot, close_date, expiry, years, calls, history = get_live_iv_data()
    nearest = calls.iloc[(calls["strike"] - spot).abs().argsort().iloc[0]]
    vix_history = yf.Ticker("^VIX").history(period="5d", auto_adjust=False)
    vix = float(vix_history["Close"].dropna().iloc[-1])
    returns = history["Close"].pct_change().dropna().tail(30)
    realised_vol = returns.std(ddof=1) * sqrt(252)
    Path("data").mkdir(exist_ok=True)
    calls.to_csv(f"data/hw06_spy_calls_{expiry}.csv", index=False)
    print(f"\nQ5  SPY spot (latest close {close_date.date()}): ${spot:.2f}; expiry {expiry}; {len(calls)} quoted calls")
    print(f"    ATM strike ${nearest['strike']:.2f}: implied volatility {nearest['implied_volatility']:.2%}; VIX {vix:.2f}")
    print(f"Q6  30-day realised volatility: {realised_vol:.2%}; ATM implied volatility: {nearest['implied_volatility']:.2%}")
    plot_iv_smile(calls, spot, expiry)


if __name__ == "__main__":
    main()
