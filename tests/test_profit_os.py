
import numpy as np
import pandas as pd
import pytest

from src.profitos.sales_forecast import (
    calculate_metrics,
    forecast_naive,
    forecast_moving_average,
)


def test_naive_forecast_repeats_last_observation():
    training = pd.Series([100.0, 120.0, 150.0])

    result = forecast_naive(training, 3)

    assert result.tolist() == [150.0, 150.0, 150.0]


def test_moving_average_forecast_uses_last_three_months():
    training = pd.Series([100.0, 200.0, 300.0, 400.0])

    result = forecast_moving_average(training, 3)

    assert result.tolist() == [300.0, 300.0, 300.0]


def test_moving_average_requires_three_observations():
    training = pd.Series([100.0, 200.0])

    with pytest.raises(ValueError):
        forecast_moving_average(training, 3)


def test_forecast_metrics_are_calculated_correctly():
    actual = np.array([100.0, 200.0, 300.0])
    predicted = np.array([110.0, 180.0, 330.0])

    metrics = calculate_metrics(actual, predicted)

    assert metrics["MAE"] == pytest.approx(20.0)
    assert metrics["RMSE"] == pytest.approx(np.sqrt(1400.0 / 3))
    assert metrics["WAPE_percent"] == pytest.approx(10.0)


def test_wape_is_nan_when_actual_sales_are_zero():
    actual = np.array([0.0, 0.0])
    predicted = np.array([10.0, 20.0])

    metrics = calculate_metrics(actual, predicted)

    assert np.isnan(metrics["WAPE_percent"])


def test_forecast_metrics_handle_perfect_predictions():
    actual = np.array([100.0, 200.0, 300.0])

    metrics = calculate_metrics(actual, actual)

    assert metrics["MAE"] == 0.0
    assert metrics["RMSE"] == 0.0
    assert metrics["WAPE_percent"] == 0.0
