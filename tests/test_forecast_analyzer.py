from pathlib import Path

from src.tools.forecast_analyzer import ForecastAnalyzerTool
from src.utils import load_forecast


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def test_forecast_analyzer_calculates_gap_correctly():
    forecast = load_forecast(DATA_DIR / "sample_forecast.csv")
    analyzed, _ = ForecastAnalyzerTool(forecast).run()

    first_row = analyzed.iloc[0]
    assert first_row["gap"] == 2


def test_forecast_analyzer_labels_understaffed_correctly():
    forecast = load_forecast(DATA_DIR / "sample_forecast.csv")
    analyzed, summary = ForecastAnalyzerTool(forecast).run()

    row = analyzed[
        (analyzed["date"] == "2026-07-08")
        & (analyzed["interval"] == "12:00")
    ].iloc[0]
    assert row["status"] == "understaffed"
    assert summary["total_understaffed_intervals"] > 0
