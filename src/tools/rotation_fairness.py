"""Weekend rotation fairness scoring."""

from __future__ import annotations

import pandas as pd

from src.models import PlanningRules
from src.utils import normalize_day


class RotationFairnessTool:
    """Rank agents for weekend shifts using local, explainable heuristics."""

    def __init__(self, agents_df: pd.DataFrame, rules: PlanningRules):
        self.agents_df = agents_df.copy()
        self.rules = rules

    def rank_for_weekend(self) -> dict[str, pd.DataFrame]:
        """Return ranked Saturday and Sunday candidate dataframes."""

        return {
            "Saturday": self._rank_for_day("Saturday"),
            "Sunday": self._rank_for_day("Sunday"),
        }

    def _rank_for_day(self, day_name: str) -> pd.DataFrame:
        day_token = normalize_day(day_name)
        rows: list[dict] = []
        for _, agent in self.agents_df.iterrows():
            available_days = agent["available_days"]
            is_available = day_token in available_days
            is_vacation = bool(agent["vacation"])

            availability_score = 1.0 if is_available and not is_vacation else 0.0
            weekend_score = max(0.0, 1.0 - (float(agent["last_weekend_worked"]) / 3.0))
            preference_score = 1.0 if agent["preferred_start"] != agent["last_shift_start"] else 0.35

            weighted_score = (
                self.rules.coverage_weight * availability_score
                + self.rules.weekend_fairness_weight * weekend_score
                + self.rules.preference_weight * preference_score
            )

            if is_vacation:
                reason = "Excluded from weekend ranking because agent is on vacation."
            elif not is_available:
                reason = f"Excluded because {day_name} is not in available_days."
            else:
                reason = (
                    f"Available on {day_name}; last_weekend_worked={agent['last_weekend_worked']}; "
                    f"preferred_start={agent['preferred_start']}."
                )

            rows.append(
                {
                    "day_name": day_name,
                    "agent_id": agent["agent_id"],
                    "agent_name": agent["agent_name"],
                    "skill": agent["skill"],
                    "site": agent["site"],
                    "preferred_start": agent["preferred_start"],
                    "last_weekend_worked": int(agent["last_weekend_worked"]),
                    "vacation": bool(agent["vacation"]),
                    "available": bool(is_available and not is_vacation),
                    "fairness_score": round(weighted_score, 3),
                    "ranking_reason": reason,
                }
            )

        ranking = pd.DataFrame(rows)
        ranking = ranking.sort_values(
            by=["available", "fairness_score", "last_weekend_worked", "agent_name"],
            ascending=[False, False, True, True],
        ).reset_index(drop=True)
        ranking["rank"] = ranking.index + 1
        return ranking
