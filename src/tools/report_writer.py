"""Local Markdown report writer."""

from __future__ import annotations

import pandas as pd


class ReportWriterTool:
    """Create a business-friendly planning report from computed outputs."""

    def __init__(
        self,
        forecast_summary: dict,
        schedule_df: pd.DataFrame,
        warnings_df: pd.DataFrame,
        weekend_rankings: dict[str, pd.DataFrame],
        reasoning_log: list[str],
    ):
        self.forecast_summary = forecast_summary
        self.schedule_df = schedule_df
        self.warnings_df = warnings_df
        self.weekend_rankings = weekend_rankings
        self.reasoning_log = reasoning_log

    def run(self) -> str:
        """Generate the final Markdown report."""

        total_assignments = len(self.schedule_df)
        unique_agents = self.schedule_df["agent_id"].nunique() if not self.schedule_df.empty else 0
        high_warnings = int((self.warnings_df["severity"] == "high").sum()) if not self.warnings_df.empty else 0
        medium_warnings = int((self.warnings_df["severity"] == "medium").sum()) if not self.warnings_df.empty else 0
        low_warnings = int((self.warnings_df["severity"] == "low").sum()) if not self.warnings_df.empty else 0

        saturday_top = self._top_names("Saturday")
        sunday_top = self._top_names("Sunday")
        worst_lines = self._worst_interval_lines()
        validation_summary = (
            "No validation warnings were found."
            if self.warnings_df.empty
            else f"{len(self.warnings_df)} warning(s): {high_warnings} high, {medium_warnings} medium, {low_warnings} low."
        )

        return f"""# WFM Planning Agent Report

## Executive Summary

The WFM Planning Agent reviewed forecast demand, employee availability, weekend fairness, and scheduling constraints for the sample planning week. It generated {total_assignments} assignments across {unique_agents} unique agents and produced a validation pass before returning recommendations.

Validation result: {validation_summary}

## Forecast Findings

- Total forecast intervals reviewed: {self.forecast_summary['total_intervals']}
- Understaffed intervals: {self.forecast_summary['total_understaffed_intervals']}
- Overstaffed intervals: {self.forecast_summary['total_overstaffed_intervals']}
- Largest shortage: {self.forecast_summary['largest_shortage_fte']:.1f} FTE
- Largest surplus: {self.forecast_summary['largest_surplus_fte']:.1f} FTE
- Saturday peak requirement: {self.forecast_summary['weekend_required_staffing']['Saturday']:.0f} FTE
- Sunday peak requirement: {self.forecast_summary['weekend_required_staffing']['Sunday']:.0f} FTE

Most critical intervals:

{worst_lines}

## Schedule Generation Approach

The schedule generator selected available, non-vacation agents and assigned allowed start times. Weekday coverage uses a balanced rotation across configured shift starts. Weekend coverage uses the rotation fairness ranking so agents with fewer recent weekend assignments are preferred.

## Weekend Rotation Fairness

Top Saturday candidates: {saturday_top}

Top Sunday candidates: {sunday_top}

The ranking combines availability, recent weekend workload, and shift-start preference. This keeps the recommendation explainable and easy for a human planner to audit.

## Constraint Validation Result

{validation_summary}

The validator checks vacation assignments, weekend minimum staffing, allowed shift starts, shift length, lunch placement, duplicate assignments, double-weekend work, and peak interval coverage.

## Risks and Limitations

- The project uses fake sample data, not private employee data.
- It uses deterministic heuristics rather than a paid LLM or optimizer.
- Forecast coverage warnings are approximate and should be reviewed by a planner.
- It does not replace local labor law, HR policy, or union agreement checks.

## Human Review Recommendation

A WFM planner should review high and medium warnings first, then inspect agents scheduled on both weekend days. The generated files are intended as a planning draft, not an automatic final roster.

## Next Steps

1. Replace sample files with real anonymized planning data.
2. Tune fairness and coverage weights with WFM stakeholders.
3. Add market-specific compliance rules.
4. Integrate with HR and forecasting systems for production use.

## Agent Reasoning Trace

{self._reasoning_lines()}
"""

    def _top_names(self, day_name: str, limit: int = 5) -> str:
        ranking = self.weekend_rankings.get(day_name)
        if ranking is None or ranking.empty:
            return "No candidates available"
        names = ranking[ranking["available"]].head(limit)["agent_name"].tolist()
        return ", ".join(names) if names else "No candidates available"

    def _worst_interval_lines(self) -> str:
        worst = self.forecast_summary.get("worst_intervals", [])
        if not worst:
            return "- No understaffed intervals found."
        lines = []
        for item in worst:
            lines.append(
                f"- {item['day_name']} {item['date']} {item['interval']}: "
                f"required {item['required_fte']:.0f}, available {item['available_fte']:.0f}, gap {item['gap']:.0f}"
            )
        return "\n".join(lines)

    def _reasoning_lines(self) -> str:
        return "\n".join(f"- {line}" for line in self.reasoning_log)
