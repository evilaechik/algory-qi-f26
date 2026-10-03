"""Homework 3 - Algory QI Education, Fall 2026."""
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt


# ---------------------------------------------------------------- Q1
def simulate_dice(trials, seed=0):
    """Estimate P(picked the 4-sided die | rolled a 1)."""
    rng = np.random.default_rng(seed)
    die_sides = rng.choice([4, 6], size=trials)
    rolls = (rng.random(trials) * die_sides).astype(int) + 1
    one_rolls = rolls == 1
    return np.mean(die_sides[one_rolls] == 4)


# ---------------------------------------------------------------- Q2
def simulate_coins(trials, seed=0):
    """Return the mean payout after three fair coins, paid heads times tails."""
    rng = np.random.default_rng(seed)
    heads = rng.integers(0, 2, size=(trials, 3)).sum(axis=1)
    tails = 3 - heads
    return np.mean(heads * tails)


# ---------------------------------------------------------------- Q5/Q6
def p_down(returns):
    """Fraction of days with a negative return, counted directly."""
    returns = list(returns)
    return sum(return_ < 0 for return_ in returns) / len(returns)


def p_down_given_down(returns):
    """P(tomorrow is down | today was down), counted directly."""
    returns = list(returns)
    qualifying_days = 0
    down_tomorrows = 0
    for day in range(len(returns) - 1):
        if returns[day] < 0:
            qualifying_days += 1
            if returns[day + 1] < 0:
                down_tomorrows += 1
    return down_tomorrows / qualifying_days if qualifying_days else np.nan


def p_down_given_big_drop(returns, threshold=-0.02):
    """P(tomorrow is down | today fell more than threshold), counted directly."""
    returns = list(returns)
    qualifying_days = 0
    down_tomorrows = 0
    for day in range(len(returns) - 1):
        if returns[day] < threshold:
            qualifying_days += 1
            if returns[day + 1] < 0:
                down_tomorrows += 1
    return down_tomorrows / qualifying_days if qualifying_days else np.nan


# ---------------------------------------------------------------- Q7
def expected_present_value(cash_flows, rate, survival_prob):
    """Present value when survival probability compounds after the first year."""
    return sum(
        cash_flow * survival_prob ** year / (1 + rate) ** (year + 1)
        for year, cash_flow in enumerate(cash_flows)
    )


def main():
    seed = 42
    dice_estimate = simulate_dice(100_000, seed=seed)
    coin_estimate = simulate_coins(100_000, seed=seed)
    print(f"Q1  Seed = {seed}")
    print(f"    Simulated P(4-sided | rolled a 1) = {dice_estimate:.4f}")
    print(f"    Exact probability = 0.6000; difference = {dice_estimate - 0.6:+.4f}")
    print(f"Q2  Simulated expected three-coin payout = {coin_estimate:.4f}")
    print("    Exact expected payout = 1.5000")

    trial_counts = [100, 1_000, 10_000, 100_000]
    estimates = [simulate_coins(trials, seed=seed) for trials in trial_counts]
    print("Q3  Three-coin payout estimates")
    for trials, estimate in zip(trial_counts, estimates):
        print(f"    {trials:>7,} trials: {estimate:.4f}")
    plt.figure(figsize=(7, 4.5))
    plt.plot(trial_counts, estimates, marker="o", color="navy", label="Simulation estimate")
    plt.axhline(1.5, color="firebrick", linestyle="--", label="Exact value (1.5)")
    plt.xscale("log")
    plt.xticks(trial_counts, [f"{trials:,}" for trials in trial_counts])
    plt.xlabel("Number of trials (log scale)")
    plt.ylabel("Estimated expected payout")
    plt.title("Three-Coin Payout: Simulation Convergence")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("hw03_coin_convergence.png", dpi=200)
    plt.close()
    print("    Plot saved as hw03_coin_convergence.png")

    prices = yf.download("SPY", period="10y", interval="1d", auto_adjust=False, progress=False)["Close"]
    if hasattr(prices, "columns"):
        prices = prices.iloc[:, 0]
    returns = prices.pct_change().dropna()
    return_values = returns.to_numpy()
    down_days = sum(return_ < 0 for return_ in return_values)
    preceding_down_days = sum(return_values[day] < 0 for day in range(len(return_values) - 1))
    big_drop_days = sum(return_values[day] < -0.02 for day in range(len(return_values) - 1))

    print(f"Q4  SPY trading days = {len(prices)}")
    print(f"    Mean daily return = {returns.mean():.4%}")
    print(f"Q5  P(tomorrow is down) = {p_down(return_values):.4f} ({down_days} down days / {len(return_values)} returns)")
    print(f"    P(tomorrow is down | today was down) = {p_down_given_down(return_values):.4f} (based on {preceding_down_days} down days)")
    print(f"Q6  P(tomorrow is down | today was down more than 2%) = {p_down_given_big_drop(return_values):.4f} (based on {big_drop_days} big-drop days)")
    print(f"Q7  Expected present value = {expected_present_value([10, 10, 10], 0.10, 0.5):.2f}")


if __name__ == "__main__":
    main()
