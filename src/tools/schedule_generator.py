"""Schedule generation tool."""

from __future__ import annotations

import itertools

import pandas as pd

from src.models import PlanningRules
from src.utils import add_hours, empty_schedule_frame, normalize_day


class ScheduleGeneratorTool:
    """Generate a practical schedule from agents, forecast dates, rules, and rankings."""

    def __init__(
        self,
        agents_df: pd.DataFrame,
        forecast_df: pd.DataFrame,
        rules: PlanningRules,
        weekend_rankings: dict[str, pd.DataFrame],
    ):
        self.agents_df = agents_df.copy()
        self.forecast_df = forecast_df.copy()
        self.rules = rules
        self.weekend_rankings = weekend_rankings

    def run(self) -> pd.DataFrame:
        """Generate weekday and weekend assignments."""

        assignments: list[dict] = []
        dates = self.forecast_df[["date", "day_name"]].drop_duplicates().sort_values("date")
        start_cycle = itertools.cycle(self.rules.allowed_shift_starts)

        for _, date_row in dates.iterrows():
            date = date_row["date"]
            day_name = date_row["day_name"]
            if day_name == "Saturday":
                selected = self._select_weekend_agents("Saturday", self.rules.min_saturday_agents)
            elif day_name == "Sunday":
                selected = self._select_weekend_agents("Sunday", self.rules.min_sunday_agents)
            else:
                selected = self._select_weekday_agents(day_name)

            for _, agent in selected.iterrows():
                proposed_start = agent.get("preferred_start")
                if day_name not in {"Saturday", "Sunday"}:
                    proposed_start = next(start_cycle)
                shift_start = self._choose_shift_start(agent, proposed_start, start_cycle)
                assignments.append(self._assignment(date, day_name, agent, shift_start))

        if not assignments:
            return empty_schedule_frame()
        return pd.DataFrame(assignments)

    def _select_weekday_agents(self, day_name: str) -> pd.DataFrame:
        day_token = normalize_day(day_name)
        eligible = self.agents_df[
            (~self.agents_df["vacation"])
            & (self.agents_df["available_days"].apply(lambda days: day_token in days))
        ].copy()
        return eligible.sort_values(["site", "skill", "agent_name"]).reset_index(drop=True)

    def _select_weekend_agents(self, day_name: str, minimum: int) -> pd.DataFrame:
        ranking = self.weekend_rankings[day_name]
        selected_ids = ranking[ranking["available"]].head(minimum)["agent_id"].tolist()
        selected = self.agents_df[self.agents_df["agent_id"].isin(selected_ids)].copy()
        ordering = {agent_id: index for index, agent_id in enumerate(selected_ids)}
        selected["weekend_order"] = selected["agent_id"].map(ordering)
        return selected.sort_values("weekend_order").drop(columns=["weekend_order"]).reset_index(drop=True)

    def _choose_shift_start(self, agent: pd.Series, proposed_start: str, start_cycle: itertools.cycle) -> str:
        allowed = self.rules.allowed_shift_starts
        if proposed_start not in allowed:
            proposed_start = next(start_cycle)
        if agent["last_shift_start"] == proposed_start and len(allowed) > 1:
            current_index = allowed.index(proposed_start)
            return allowed[(current_index + 1) % len(allowed)]
        return proposed_start

    def _assignment(self, date: str, day_name: str, agent: pd.Series, shift_start: str) -> dict:
        shift_end = add_hours(shift_start, self.rules.default_shift_hours)
        lunch_offset = 4
        if self.rules.lunch_after_hours:
            lunch_offset = sorted(self.rules.lunch_after_hours, key=lambda value: abs(value - 4))[0]
        lunch_start = add_hours(shift_start, float(lunch_offset))
        lunch_end = add_hours(lunch_start, 0.5)

        if day_name in {"Saturday", "Sunday"}:
            reason = (
                f"Weekend assignment selected by fairness ranking; recent weekend count "
                f"{agent['last_weekend_worked']} and availability confirmed."
            )
        else:
            reason = "Weekday assignment for available non-vacation agent using balanced start rotation."

        return {
            "date": date,
            "day_name": day_name,
            "agent_id": agent["agent_id"],
            "agent_name": agent["agent_name"],
            "skill": agent["skill"],
            "site": agent["site"],
            "shift_start": shift_start,
            "shift_end": shift_end,
            "lunch_start": lunch_start,
            "lunch_end": lunch_end,
            "assignment_reason": reason,
        }
