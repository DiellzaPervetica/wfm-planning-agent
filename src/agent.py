"""Local orchestrator for the WFM Planning Agent."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.models import AgentRunResult, PlanningRules
from src.tools.constraint_validator import ConstraintValidatorTool
from src.tools.forecast_analyzer import ForecastAnalyzerTool
from src.tools.report_writer import ReportWriterTool
from src.tools.rotation_fairness import RotationFairnessTool
from src.tools.schedule_generator import ScheduleGeneratorTool
from src.utils import load_agents, load_forecast, load_rules


class WFMPlanningAgent:
    """Agent-style orchestrator that calls deterministic local planning tools."""

    def __init__(
        self,
        agents: str | Path | pd.DataFrame,
        forecast: str | Path | pd.DataFrame,
        rules: str | Path | dict[str, Any] | PlanningRules,
    ):
        self.agents_source = agents
        self.forecast_source = forecast
        self.rules_source = rules
        self.reasoning_log: list[str] = []

    def run(self, output_dir: str | Path | None = None) -> AgentRunResult:
        """Execute the complete planning workflow."""

        self.reasoning_log = []

        agents_df = load_agents(self.agents_source)
        forecast_df = load_forecast(self.forecast_source)
        rules = load_rules(self.rules_source)
        self.reasoning_log.append(
            f"Step 1: Loaded inputs with {len(agents_df)} agents, {len(forecast_df)} forecast intervals, and {len(rules.allowed_shift_starts)} allowed shift starts."
        )

        forecast_tool = ForecastAnalyzerTool(forecast_df)
        forecast_with_gap, forecast_summary = forecast_tool.run()
        self.reasoning_log.append(
            "Step 2: ForecastAnalyzerTool detected "
            f"{forecast_summary['total_understaffed_intervals']} understaffed intervals and "
            f"{forecast_summary['total_overstaffed_intervals']} overstaffed intervals."
        )

        fairness_tool = RotationFairnessTool(agents_df, rules)
        weekend_rankings = fairness_tool.rank_for_weekend()
        self.reasoning_log.append(
            "Step 3: RotationFairnessTool ranked Saturday and Sunday candidates using availability, recent weekend work, and preference weights."
        )

        schedule_tool = ScheduleGeneratorTool(agents_df, forecast_with_gap, rules, weekend_rankings)
        schedule_df = schedule_tool.run()
        self.reasoning_log.append(
            f"Step 4: ScheduleGeneratorTool generated {len(schedule_df)} assignments and avoided vacation agents by design."
        )

        validator_tool = ConstraintValidatorTool(schedule_df, agents_df, forecast_with_gap, rules)
        warnings_df = validator_tool.run()
        self.reasoning_log.append(
            f"Step 5: ConstraintValidatorTool returned {len(warnings_df)} warning(s) across coverage, fairness, and rule checks."
        )

        report_tool = ReportWriterTool(
            forecast_summary=forecast_summary,
            schedule_df=schedule_df,
            warnings_df=warnings_df,
            weekend_rankings=weekend_rankings,
            reasoning_log=self.reasoning_log,
        )
        report_markdown = report_tool.run()
        self.reasoning_log.append("Step 6: ReportWriterTool generated the final business-friendly Markdown report.")

        output_paths: dict[str, str] = {}
        if output_dir is not None:
            output_paths = self._save_outputs(output_dir, schedule_df, warnings_df, report_markdown)
            self.reasoning_log.append(f"Step 7: Saved schedule, warnings, and report to {Path(output_dir)}.")

        return AgentRunResult(
            forecast_summary=forecast_summary,
            forecast_with_gap=forecast_with_gap,
            weekend_rankings=weekend_rankings,
            schedule=schedule_df,
            validation_warnings=warnings_df,
            report_markdown=report_markdown,
            reasoning_log=self.reasoning_log,
            output_paths=output_paths,
        )

    def _save_outputs(
        self,
        output_dir: str | Path,
        schedule_df: pd.DataFrame,
        warnings_df: pd.DataFrame,
        report_markdown: str,
    ) -> dict[str, str]:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        schedule_path = output_path / "generated_schedule.csv"
        warnings_path = output_path / "validation_warnings.csv"
        report_path = output_path / "planning_report.md"

        schedule_df.to_csv(schedule_path, index=False)
        warnings_df.to_csv(warnings_path, index=False)
        report_path.write_text(report_markdown, encoding="utf-8")

        return {
            "generated_schedule": str(schedule_path),
            "validation_warnings": str(warnings_path),
            "planning_report": str(report_path),
        }
