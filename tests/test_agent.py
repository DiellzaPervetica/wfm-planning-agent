from pathlib import Path

from src.agent import WFMPlanningAgent


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def test_agent_returns_schedule_warnings_report_and_reasoning_log(tmp_path):
    result = WFMPlanningAgent(
        DATA_DIR / "sample_agents.csv",
        DATA_DIR / "sample_forecast.csv",
        DATA_DIR / "sample_rules.json",
    ).run(output_dir=tmp_path)

    assert not result.schedule.empty
    assert result.validation_warnings is not None
    assert "WFM Planning Agent Report" in result.report_markdown
    assert len(result.reasoning_log) >= 6
    assert (tmp_path / "generated_schedule.csv").exists()
    assert (tmp_path / "validation_warnings.csv").exists()
    assert (tmp_path / "planning_report.md").exists()
