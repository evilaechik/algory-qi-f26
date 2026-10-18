# Homework 4: A small, honest strategy backtest

`hw04_starter.py` builds a daily, close-to-close backtest for the S&P 500 total-return index (`^SP500TR`). It compares several simple rules on training data, locks a 60-day moving-average rule, and evaluates it against buy-and-hold in a later holdout. The program reports return, drawdown, exposure, every candidate tried, and the most recent signal; it also saves equity-curve plots.

## Run

Requires Python 3 and `numpy`, `pandas`, `matplotlib`, and `yfinance` (`reportlab` is only needed to recreate the PDF). From this directory:

```sh
python3 -m pip install numpy pandas matplotlib yfinance
python3 check_hw04.py
python3 hw04_starter.py --train-only
python3 hw04_starter.py --snapshot
```

`--train-only` downloads only prices through the split and never reads holdout data. `--snapshot` uses the saved `data/hw04_sp500tr.csv`, downloaded on October 18, 2026, which fixes the dataset used in the report. Running without either flag downloads current data and refreshes that snapshot; new data may change the test metrics and the latest signal. The PDF's numerical results describe the original saved snapshot, not a later refresh. `check_hw04.py` uses synthetic data and needs no network.

## Timing and split

September 10, 2011 was a Saturday, so the split is the prior trading close, September 9. Training ends on that close. The test input contains the last 60 training closes as warmup history, with no returns earned during that overlap; its first earned return runs from the September 9 close to September 12. A strategy sees a window of 60 closes ending at today's close and makes a decision for the return from today's close to tomorrow's, never seeing tomorrow's price. All strategies and the benchmark start at 1 on the first decision close. Annualisation uses 252 trading days.

## Research protocol and results

Five candidate rules are listed in the code and were all evaluated on the training period. The selected rule holds the index when its latest close is above its 60-day moving average, and holds cash otherwise; it was fixed before running the holdout. Its training annualised return was 5.72%. On the October 18 snapshot, its holdout annualised return was 7.32% versus 15.47% for buy-and-hold, with maximum drawdowns of -21.40% and -33.79%, respectively. The rule was not changed after that result. The holdout dates and market history are public, so this is a historical out-of-sample exercise, not a claim of a genuinely unseen prospective test.

The model assumes frictionless execution at the signal close, zero transaction costs, taxes, slippage and cash interest. The total-return index is not directly tradable. The close-execution assumption can be especially optimistic because the signal depends on that same close. Results are not investment advice, and the single holdout does not establish a reliable edge. The written submission discusses these limitations.
