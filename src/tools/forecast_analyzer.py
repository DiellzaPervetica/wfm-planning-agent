"""Forecast analysis tool for staffing gaps."""

from __future__ import annotations

import pandas as pd


class ForecastAnalyzerTool:
    """Analyze staffing demand, availability, and interval-level gaps."""

    def __init__(self, forecast_df: pd.DataFrame):
        self.forecast_df = forecast_df.copy()
        self.analyzed_df: pd.DataFrame | None = None

    def run(self) -> tuple[pd.DataFrame, dict]:
        """Calculate gaps, status labels, and a compact business summary."""

        df = self.forecast_df.copy()
        df["gap"] = df["available_fte"] - df["required_fte"]
        df["status"] = df["gap"].apply(self._label_status)
        self.analyzed_df = df

        understaffed = df[df["status"] == "understaffed"]
        overstaffed = df[df["status"] == "overstaffed"]
        weekend = df[df["day_name"].isin(["Saturday", "Sunday"])]

        worst = (
            understaffed.sort_values("gap")
            .head(8)[["date", "day_name", "interval", "required_fte", "available_fte", "gap"]]
            .to_dict("records")
        )

        summary = {
            "total_intervals": int(len(df)),
            "total_understaffed_intervals": int(len(understaffed)),
            "total_overstaffed_intervals": int(len(overstaffed)),
            "total_balanced_intervals": int((df["status"] == "balanced").sum()),
            "worst_intervals": worst,
            "largest_shortage_fte": float(abs(understaffed["gap"].min())) if not understaffed.empty else 0.0,
            "largest_surplus_fte": float(overstaffed["gap"].max()) if not overstaffed.empty else 0.0,
            "weekend_required_staffing": {
                "Saturday": float(weekend[weekend["day_name"] == "Saturday"]["required_fte"].max() or 0),
                "Sunday": float(weekend[weekend["day_name"] == "Sunday"]["required_fte"].max() or 0),
            },
            "average_required_fte": float(df["required_fte"].mean()),
            "average_available_fte": float(df["available_fte"].mean()),
        }
        return df, summary

    def get_peak_understaffed_periods(self, limit: int = 5) -> pd.DataFrame:
        """Return the most understaffed intervals after analysis."""

        if self.analyzed_df is None:
            self.run()
        assert self.analyzed_df is not None
        return self.analyzed_df[self.analyzed_df["gap"] < 0].sort_values("gap").head(limit)

    @staticmethod
    def _label_status(gap: float) -> str:
        if gap < 0:
            return "understaffed"
        if gap > 0:
            return "overstaffed"
        return "balanced"
