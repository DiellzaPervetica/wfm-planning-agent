from pathlib import Path

from src.agent import WFMPlanningAgent
from src.utils import load_agents, load_rules


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def test_schedule_generator_never_schedules_vacation_agents():
    result = WFMPlanningAgent(
        DATA_DIR / "sample_agents.csv",
        DATA_DIR / "sample_forecast.csv",
        DATA_DIR / "sample_rules.json",
    ).run()
    agents = load_agents(DATA_DIR / "sample_agents.csv")
    vacation_ids = set(agents[agents["vacation"]]["agent_id"])

    assert not set(result.schedule["agent_id"]).intersection(vacation_ids)


def test_weekend_staffing_meets_minimums():
    result = WFMPlanningAgent(
        DATA_DIR / "sample_agents.csv",
        DATA_DIR / "sample_forecast.csv",
        DATA_DIR / "sample_rules.json",
    ).run()
    rules = load_rules(DATA_DIR / "sample_rules.json")
    saturday = result.schedule[result.schedule["day_name"] == "Saturday"]["agent_id"].nunique()
    sunday = result.schedule[result.schedule["day_name"] == "Sunday"]["agent_id"].nunique()

    assert saturday >= rules.min_saturday_agents
    assert sunday >= rules.min_sunday_agents
