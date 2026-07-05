"""Constraint validation tool for generated schedules."""

from __future__ import annotations

import pandas as pd

from src.models import PlanningRules
from src.utils import empty_warnings_frame, time_to_minutes


class ConstraintValidatorTool:
    """Validate schedule outputs against planning rules and forecast demand."""

    def __init__(
        self,
        schedule_df: pd.DataFrame,
        agents_df: pd.DataFrame,
        forecast_df: pd.DataFrame,
        rules: PlanningRules,
    ):
        self.schedule_df = schedule_df.copy()
        self.agents_df = agents_df.copy()
        self.forecast_df = forecast_df.copy()
        self.rules = rules
        self.warnings: list[dict] = []

    def run(self) -> pd.DataFrame:
        """Run all schedule validation checks."""

        if self.schedule_df.empty:
            self._add(
                "high",
                "schedule_not_empty",
                None,
                None,
                "No schedule assignments were generated.",
                "Review input files and planning rules before submission.",
            )
            return self._to_frame()

        self._validate_vacation_assignments()
        self._validate_weekend_minimums()
        self._validate_shift_starts()
        self._validate_shift_end()
        self._validate_lunch_windows()
        self._validate_duplicate_agent_day()
        self._warn_double_weekend()
        self._warn_peak_coverage()
        return self._to_frame()

    def _validate_vacation_assignments(self) -> None:
        vacation_agents = set(self.agents_df[self.agents_df["vacation"]]["agent_id"])
        bad_rows = self.schedule_df[self.schedule_df["agent_id"].isin(vacation_agents)]
        for _, row in bad_rows.iterrows():
            self._add(
                "high",
                "avoid_vacation_assignments",
                row["agent_name"],
                row["date"],
                f"{row['agent_name']} is scheduled while marked as vacation=true.",
                "Remove this assignment or update the vacation source data if it is incorrect.",
            )

    def _validate_weekend_minimums(self) -> None:
        self._validate_day_minimum("Saturday", self.rules.min_saturday_agents)
        self._validate_day_minimum("Sunday", self.rules.min_sunday_agents)

    def _validate_day_minimum(self, day_name: str, minimum: int) -> None:
        rows = self.schedule_df[self.schedule_df["day_name"] == day_name]
        count = rows["agent_id"].nunique()
        if count < minimum:
            date = rows["date"].iloc[0] if not rows.empty else None
            self._add(
                "high",
                f"min_{day_name.lower()}_agents",
                None,
                date,
                f"{day_name} has {count} scheduled agents; minimum is {minimum}.",
                f"Add at least {minimum - count} eligible {day_name} assignment(s).",
            )

    def _validate_shift_starts(self) -> None:
        bad_rows = self.schedule_df[~self.schedule_df["shift_start"].isin(self.rules.allowed_shift_starts)]
        for _, row in bad_rows.iterrows():
            self._add(
                "medium",
                "allowed_shift_starts",
                row["agent_name"],
                row["date"],
                f"{row['shift_start']} is not an allowed shift start.",
                "Use one of the configured allowed_shift_starts.",
            )

    def _validate_shift_end(self) -> None:
        expected_minutes = self.rules.default_shift_hours * 60
        for _, row in self.schedule_df.iterrows():
            actual = time_to_minutes(row["shift_end"]) - time_to_minutes(row["shift_start"])
            if actual < 0:
                actual += 24 * 60
            if actual != expected_minutes:
                self._add(
                    "medium",
                    "default_shift_hours",
                    row["agent_name"],
                    row["date"],
                    f"Shift length is {actual / 60:.1f} hours; expected {self.rules.default_shift_hours}.",
                    "Recalculate shift_end from shift_start and default_shift_hours.",
                )

    def _validate_lunch_windows(self) -> None:
        for _, row in self.schedule_df.iterrows():
            start = time_to_minutes(row["shift_start"])
            end = time_to_minutes(row["shift_end"])
            lunch_start = time_to_minutes(row["lunch_start"])
            lunch_end = time_to_minutes(row["lunch_end"])
            if end <= start:
                end += 24 * 60
            if lunch_start < start:
                lunch_start += 24 * 60
                lunch_end += 24 * 60
            if not (start < lunch_start < lunch_end < end):
                self._add(
                    "medium",
                    "lunch_within_shift",
                    row["agent_name"],
                    row["date"],
                    "Lunch window is outside the shift boundaries.",
                    "Place lunch after shift start and before shift end.",
                )

    def _validate_duplicate_agent_day(self) -> None:
        duplicates = self.schedule_df[self.schedule_df.duplicated(["agent_id", "date"], keep=False)]
        for _, row in duplicates.iterrows():
            self._add(
                "high",
                "no_duplicate_same_agent_same_day",
                row["agent_name"],
                row["date"],
                f"{row['agent_name']} has more than one assignment on the same day.",
                "Keep one assignment per agent per date.",
            )

    def _warn_double_weekend(self) -> None:
        weekend = self.schedule_df[self.schedule_df["day_name"].isin(["Saturday", "Sunday"])]
        both_days = weekend.groupby(["agent_id", "agent_name"])["day_name"].nunique().reset_index()
        both_days = both_days[both_days["day_name"] > 1]
        for _, row in both_days.iterrows():
            self._add(
                "low",
                "weekend_rotation_fairness",
                row["agent_name"],
                None,
                f"{row['agent_name']} is scheduled on both Saturday and Sunday.",
                "Review manually; split weekend work if another eligible agent is available.",
            )

    def _warn_peak_coverage(self) -> None:
        for _, forecast in self.forecast_df.iterrows():
            scheduled_count = self._scheduled_count_for_interval(
                forecast["date"],
                forecast["interval"],
            )
            required = float(forecast["required_fte"])
            if scheduled_count < required:
                shortage = required - scheduled_count
                if shortage >= 3:
                    severity = "medium"
                else:
                    severity = "low"
                self._add(
                    severity,
                    "forecast_peak_coverage",
                    None,
                    forecast["date"],
                    (
                        f"{forecast['day_name']} {forecast['interval']} has estimated schedule "
                        f"coverage {scheduled_count}, below required FTE {required:.0f}."
                    ),
                    "Review peak interval coverage and consider overtime, voluntary weekend work, or shift start changes.",
                )

    def _scheduled_count_for_interval(self, date: str, interval: str) -> int:
        interval_minutes = time_to_minutes(interval)
        rows = self.schedule_df[self.schedule_df["date"] == date]
        count = 0
        for _, row in rows.iterrows():
            start = time_to_minutes(row["shift_start"])
            end = time_to_minutes(row["shift_end"])
            lunch_start = time_to_minutes(row["lunch_start"])
            lunch_end = time_to_minutes(row["lunch_end"])
            if end <= start:
                end += 24 * 60
            adjusted_interval = interval_minutes
            if adjusted_interval < start:
                adjusted_interval += 24 * 60
            in_shift = start <= adjusted_interval < end
            on_lunch = lunch_start <= adjusted_interval < lunch_end
            if in_shift and not on_lunch:
                count += 1
        return count

    def _add(
        self,
        severity: str,
        rule: str,
        agent_name: str | None,
        date: str | None,
        message: str,
        recommendation: str,
    ) -> None:
        self.warnings.append(
            {
                "severity": severity,
                "rule": rule,
                "agent_name": agent_name or "",
                "date": date or "",
                "message": message,
                "recommendation": recommendation,
            }
        )

    def _to_frame(self) -> pd.DataFrame:
        if not self.warnings:
            return empty_warnings_frame()
        return pd.DataFrame(self.warnings)
