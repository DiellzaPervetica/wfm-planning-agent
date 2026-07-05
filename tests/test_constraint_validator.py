from pathlib import Path

import pandas as pd

from src.tools.constraint_validator import ConstraintValidatorTool
from src.utils import load_agents, load_forecast, load_rules


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def test_constraint_validator_catches_vacation_assignment():
    agents = load_agents(DATA_DIR / "sample_agents.csv")
    forecast = load_forecast(DATA_DIR / "sample_forecast.csv")
    rules = load_rules(DATA_DIR / "sample_rules.json")
    vacation_agent = agents[agents["vacation"]].iloc[0]
    schedule = pd.DataFrame(
        [
            {
                "date": "2026-07-06",
                "day_name": "Monday",
                "agent_id": vacation_agent["agent_id"],
                "agent_name": vacation_agent["agent_name"],
                "skill": vacation_agent["skill"],
                "site": vacation_agent["site"],
                "shift_start": "08:00",
                "shift_end": "16:00",
                "lunch_start": "12:00",
                "lunch_end": "12:30",
                "assignment_reason": "Test fixture intentionally schedules a vacation agent.",
            }
        ]
    )

    warnings = ConstraintValidatorTool(schedule, agents, forecast, rules).run()

    assert "avoid_vacation_assignments" in set(warnings["rule"])
