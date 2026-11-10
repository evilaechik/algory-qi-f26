"""Homework 7: time-ordered ML on next-day SPY returns.

Features are calculated at the close of date t and the only forward-looking
quantity is the label, the close-to-close return from t to t+1.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


FEATURE_NAMES = ["return_1", "return_5", "return_20", "return_60", "realised_vol_20", "price_to_ma50"]


def build_features(prices, lookbacks=(1, 5, 20, 60)):
    """Return [six past-only features, next-day return] rows in time order."""
    prices = np.asarray(prices, dtype=float)
    rows = []
    start = max(max(lookbacks), 50)
    for i in range(start, len(prices) - 1):
        past_returns = np.diff(prices[i - 19:i + 1]) / prices[i - 19:i]
        row = [
            prices[i] / prices[i - 1] - 1,
            prices[i] / prices[i - 5] - 1,
            prices[i] / prices[i - 20] - 1,
            prices[i] / prices[i - 60] - 1,
            np.std(past_returns, ddof=1),
            prices[i] / np.mean(prices[i - 49:i + 1]) - 1,
            prices[i + 1] / prices[i] - 1,  # The label is deliberately the only future value.
        ]
        rows.append(row)
    return rows


def split_by_time(rows, train=0.6, val=0.2):
    """Partition ordered rows once: training, validation, then test."""
    n = len(rows)
    train_end = int(n * train)
    val_end = train_end + int(n * val)
    return rows[:train_end], rows[train_end:val_end], rows[val_end:]


def up_day_baseline(prices):
    """Share of close-to-close returns that are positive."""
    prices = np.asarray(prices, dtype=float)
    return float(np.mean(np.diff(prices) > 0))


def make_dataset(data):
    """Build a dated DataFrame with seven features and a next-day-return label."""
    close = data["Close"].astype(float)
    volume = data["Volume"].astype(float)
    returns = close.pct_change()
    features = pd.DataFrame(index=data.index)
    features["return_1"] = close.pct_change(1)
    features["return_5"] = close.pct_change(5)
    features["return_20"] = close.pct_change(20)
    features["return_60"] = close.pct_change(60)
    features["realised_vol_20"] = returns.rolling(20).std()
    features["price_to_ma50"] = close / close.rolling(50).mean() - 1
    features["volume_to_avg20"] = volume / volume.rolling(20).mean() - 1
    features["next_day_return"] = returns.shift(-1)
    return features.dropna()


def base_models():
    """Untuned models used for the initial training/validation comparison."""
    return {
        "Linear regression": Pipeline([("scale", StandardScaler()), ("model", LinearRegression())]),
        "Ridge (alpha=1)": Pipeline([("scale", StandardScaler()), ("model", Ridge(alpha=1.0))]),
        "Random forest (unrestricted)": RandomForestRegressor(n_estimators=300, max_depth=None, min_samples_leaf=1,
                                                                 random_state=7, n_jobs=-1),
        "Gradient boosting (depth=3)": GradientBoostingRegressor(n_estimators=400, learning_rate=0.05,
                                                                    max_depth=3, random_state=7),
    }


def tune_models(x_train, y_train, x_val, y_val):
    """Tune exactly one hyperparameter per non-linear/regularised model on validation only."""
    grids = {
        "Ridge alpha": ([0.001, 0.01, 0.1, 1, 10, 100], lambda x: Pipeline([
            ("scale", StandardScaler()), ("model", Ridge(alpha=x))])),
        "Random forest max_depth": ([2, 3, 5, 8, 12], lambda x: RandomForestRegressor(
            n_estimators=300, max_depth=x, min_samples_leaf=3, random_state=7, n_jobs=-1)),
        "Gradient boosting max_depth": ([1, 2, 3, 4, 5], lambda x: GradientBoostingRegressor(
            n_estimators=200, learning_rate=0.03, max_depth=x, random_state=7)),
    }
    results = {}
    for name, (values, factory) in grids.items():
        scores = []
        for value in values:
            model = factory(value).fit(x_train, y_train)
            scores.append(r2_score(y_val, model.predict(x_val)))
        best_index = int(np.argmax(scores))
        results[name] = {"values": values, "scores": scores, "best_value": values[best_index],
                         "best_score": scores[best_index], "model": factory(values[best_index])}
    return results


def plot_tuning(tuned, path="hw07_validation_tuning.png"):
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.3))
    for axis, (name, result) in zip(axes, tuned.items()):
        values = result["values"]
        axis.plot(range(len(values)), result["scores"], marker="o", color="#174a7e")
        axis.axhline(0, color="gray", linewidth=0.8)
        axis.set_xticks(range(len(values)), [str(v) for v in values])
        axis.set_title(name)
        axis.set_xlabel("Hyperparameter")
        axis.set_ylabel("Validation R-squared")
        axis.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def prediction_backtest(close, test_dates, predictions):
    """Reuse Homework 4's backtester with a sequential, test-date-aligned signal."""
    from hw04_starter import LOOKBACK, backtest
    start = close.index.get_loc(test_dates[0])
    end = close.index.get_loc(test_dates[-1])
    prices = close.iloc[start - LOOKBACK + 1:end + 2]
    signals = iter(np.asarray(predictions) > 0)

    def model_signal(window):
        return bool(next(signals))
    return backtest(prices, model_signal)


def feature_ranking(model, feature_names):
    """Return signed/unsigned feature effects ranked by magnitude."""
    if hasattr(model, "feature_importances_"):
        values = model.feature_importances_
        return sorted(zip(feature_names, values), key=lambda pair: abs(pair[1]), reverse=True), "importance"
    if isinstance(model, Pipeline):
        values = model.named_steps["model"].coef_
    else:
        values = model.coef_
    return sorted(zip(feature_names, values), key=lambda pair: abs(pair[1]), reverse=True), "standardised coefficient"


def main():
    data = yf.download("SPY", period="15y", interval="1d", auto_adjust=False, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    data = data[["Close", "Volume"]].dropna()
    Path("data").mkdir(exist_ok=True)
    data.to_csv("data/hw07_spy_15y.csv")
    dataset = make_dataset(data)
    feature_names = FEATURE_NAMES + ["volume_to_avg20"]
    print(f"Q1  Feature table shape: {dataset.shape}")
    print("    Columns: " + ", ".join(dataset.columns))
    print(dataset.head(3).to_string(float_format="{:.6f}".format))
    first_date = dataset.index[0]
    print(f"    Manual timing check: row {first_date.date()} uses returns/prices through that close; its label is the following close-to-close return.")

    train, validation, test = split_by_time(dataset)
    print("\nQ2  Time-ordered splits")
    for name, frame in [("Training", train), ("Validation", validation), ("Test", test)]:
        print(f"    {name:<10} {frame.index[0].date()} to {frame.index[-1].date()} | {len(frame):,} rows")
    x_train, y_train = train[feature_names], train["next_day_return"]
    x_val, y_val = validation[feature_names], validation["next_day_return"]
    x_test, y_test = test[feature_names], test["next_day_return"]

    print("\nQ3  Initial model R-squared")
    for name, model in base_models().items():
        model.fit(x_train, y_train)
        print(f"    {name:<31} train {model.score(x_train, y_train):+.4f}  validation {model.score(x_val, y_val):+.4f}")

    tuned = tune_models(x_train, y_train, x_val, y_val)
    plot_tuning(tuned)
    print("\nQ4  Validation-only tuning")
    for name, result in tuned.items():
        print(f"    {name:<29} chosen {result['best_value']!s:<5} validation R-squared {result['best_score']:+.4f}")

    candidates = [("Linear regression", Pipeline([("scale", StandardScaler()), ("model", LinearRegression())]))]
    candidates += [(name, result["model"]) for name, result in tuned.items()]
    fitted = []
    for name, model in candidates:
        model.fit(x_train, y_train)
        fitted.append((name, model, model.score(x_val, y_val)))
    best_name, best_model, best_validation = max(fitted, key=lambda item: item[2])
    # The test set is evaluated exactly once, after model selection above.
    test_predictions = best_model.predict(x_test)
    test_r2 = r2_score(y_test, test_predictions)
    correlation = np.corrcoef(test_predictions, y_test)[0, 1]
    print(f"\nQ5  Best validation model: {best_name} ({best_validation:+.4f})")
    print(f"    Test R-squared {test_r2:+.4f}; predicted-vs-actual correlation {correlation:+.4f}")

    backtest_result = prediction_backtest(data["Close"], test.index, test_predictions)
    print("\nQ6  Test-set sign strategy versus buy-and-hold")
    print(f"    Strategy: annualised {backtest_result['annualised_return']:+.2%}; max drawdown {backtest_result['max_drawdown']:.2%}; invested {backtest_result['fraction_invested']:.2%}")
    print(f"    Index:    annualised {backtest_result['index_annualised_return']:+.2%}; max drawdown {backtest_result['index_max_drawdown']:.2%}; invested 100.00%")

    ranking, kind = feature_ranking(best_model, feature_names)
    print(f"\nQ7  Feature {kind}s for {best_name}")
    for feature, value in ranking:
        print(f"    {feature:<20} {value:+.6f}")


if __name__ == "__main__":
    main()
