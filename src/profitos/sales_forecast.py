
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing


ROOT = Path(__file__).resolve().parents[2]
DATA_FILE = ROOT / "data" / "processed" / "order_business_summary.parquet"
REPORTS_DIR = ROOT / "reports"

OUTPUT_FILE = REPORTS_DIR / "sales_forecast.csv"
METRICS_FILE = REPORTS_DIR / "sales_forecast_metrics.csv"
BACKTEST_FILE = REPORTS_DIR / "sales_forecast_backtests.csv"

SERIES_START = "2017-01-01"
FINAL_TRAIN_END = "2018-08-01"
FORECAST_STEPS = 3
MIN_TRAIN_MONTHS = 12
VALIDATION_HORIZON = 3


def load_monthly_sales():
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_FILE}")

    df = pd.read_parquet(DATA_FILE)

    required = {"purchase_timestamp", "item_sales"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    df["purchase_timestamp"] = pd.to_datetime(
        df["purchase_timestamp"], errors="coerce"
    )
    df["item_sales"] = pd.to_numeric(df["item_sales"], errors="coerce")
    df = df.dropna(subset=["purchase_timestamp", "item_sales"])

    monthly = (
        df.assign(
            month=df["purchase_timestamp"].dt.to_period("M").dt.to_timestamp()
        )
        .groupby("month")["item_sales"]
        .sum()
        .sort_index()
    )

    monthly = monthly.loc[SERIES_START:FINAL_TRAIN_END]

    if monthly.empty:
        raise ValueError("No data found in the configured historical range.")

    # Missing calendar months are filled with zero. Verify these months
    # before interpreting them as periods of genuinely zero demand.
    index = pd.date_range(
        SERIES_START, FINAL_TRAIN_END, freq="MS"
    )
    monthly = monthly.reindex(index, fill_value=0.0)
    monthly.index.name = "month"

    return monthly.astype(float)


def calculate_metrics(actual, predicted):
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)

    errors = predicted - actual
    denominator = np.abs(actual).sum()

    return {
        "MAE": float(np.abs(errors).mean()),
        "RMSE": float(np.sqrt(np.mean(errors ** 2))),
        "WAPE_percent": (
            float(np.abs(errors).sum() / denominator * 100)
            if denominator > 0
            else np.nan
        ),
    }


def forecast_holt_winters(training, horizon):
    if len(training) < MIN_TRAIN_MONTHS:
        raise ValueError("Not enough observations for Holt-Winters.")

    model = ExponentialSmoothing(
        training,
        trend="add",
        seasonal=None,
        initialization_method="estimated",
    ).fit()

    return np.asarray(model.forecast(horizon), dtype=float).clip(min=0)


def forecast_naive(training, horizon):
    """Repeat the latest observed value for each future month."""
    return np.repeat(float(training.iloc[-1]), horizon)


def forecast_moving_average(training, horizon):
    """Repeat the mean of the last three observed months."""
    window = training.tail(3)

    if len(window) < 3:
        raise ValueError("Moving average requires three observations.")

    return np.repeat(float(window.mean()), horizon)


MODELS = {
    "Naive baseline": forecast_naive,
    "Three-month moving average": forecast_moving_average,
    "Holt-Winters": forecast_holt_winters,
}


def run_rolling_backtest(monthly):
    """Evaluate each model on successive three-month holdout windows."""
    rows = []

    first_validation_position = MIN_TRAIN_MONTHS
    last_start = len(monthly) - VALIDATION_HORIZON

    for start in range(first_validation_position, last_start + 1):
        training = monthly.iloc[:start]
        actual = monthly.iloc[start:start + VALIDATION_HORIZON]

        if len(actual) != VALIDATION_HORIZON:
            continue

        for model_name, model_function in MODELS.items():
            try:
                predicted = model_function(training, len(actual))
                metrics = calculate_metrics(
                    actual.to_numpy(),
                    predicted,
                )

                rows.append({
                    "validation_start": actual.index[0],
                    "validation_end": actual.index[-1],
                    "training_months": len(training),
                    "model": model_name,
                    **metrics,
                })

            except (ValueError, ArithmeticError) as exc:
                print(
                    f"Skipping {model_name} for "
                    f"{actual.index[0]:%Y-%m}: {exc}"
                )

    if not rows:
        raise ValueError(
            "No backtests were completed. Check the date range and data."
        )

    details = pd.DataFrame(rows)
    details.to_csv(BACKTEST_FILE, index=False)

    summary = (
        details.groupby("model", as_index=False)
        .agg(
            backtest_windows=("validation_start", "nunique"),
            average_MAE=("MAE", "mean"),
            average_RMSE=("RMSE", "mean"),
            average_WAPE_percent=("WAPE_percent", "mean"),
        )
        .sort_values("average_WAPE_percent")
        .reset_index(drop=True)
    )

    summary.to_csv(METRICS_FILE, index=False)

    return details, summary


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    monthly = load_monthly_sales()

    print("\nRUNNING ROLLING-ORIGIN BACKTESTS")
    details, summary = run_rolling_backtest(monthly)

    print("\nMODEL PERFORMANCE SUMMARY")
    display_summary = summary.copy()
    numeric_columns = display_summary.select_dtypes(
        include="number"
    ).columns
    display_summary[numeric_columns] = (
        display_summary[numeric_columns].round(2)
    )
    print(display_summary.to_string(index=False))

    # Choose the model with the lowest average WAPE across the tested windows.
    # This is a provisional selection; the number and quality of windows matter.
    valid_summary = summary.dropna(subset=["average_WAPE_percent"])

    if valid_summary.empty:
        raise ValueError("All model WAPE values are undefined.")

    best_model_name = valid_summary.iloc[0]["model"]
    print(f"\nSelected model by average WAPE: {best_model_name}")

    # Fit the selected model on all configured historical observations.
    final_training = monthly.loc[:FINAL_TRAIN_END]
    best_function = MODELS[best_model_name]
    forecast_values = best_function(final_training, FORECAST_STEPS)

    forecast_dates = pd.date_range(
        start=final_training.index[-1] + pd.offsets.MonthBegin(1),
        periods=FORECAST_STEPS,
        freq="MS",
    )

    forecast = pd.DataFrame({
        "forecast_month": forecast_dates,
        "forecast_item_sales": np.round(forecast_values, 2),
        "selected_model": best_model_name,
    })

    forecast.to_csv(OUTPUT_FILE, index=False)

    print("\nTHREE-MONTH ITEM-SALES FORECAST")
    print(forecast.to_string(index=False))

    print("\nREPORTS SAVED")
    print(f"Backtest details: {BACKTEST_FILE}")
    print(f"Model metrics: {METRICS_FILE}")
    print(f"Forecast: {OUTPUT_FILE}")

    print(
        "\nCaution: these forecasts follow August 2018, not the current year. "
        "Rolling backtests are historical evaluations, not proof of future "
        "performance. Missing months were filled with zero and should be "
        "investigated before interpreting them as zero demand."
    )


if __name__ == "__main__":
    main()
