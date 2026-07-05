"""Streamlit dashboard for the WFM Planning Agent."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src.agent import WFMPlanningAgent
from src.visualization import fte_gap_chart, required_vs_available_chart, weekend_assignment_chart


BASE_DIR = Path(__file__).parent
SAMPLE_AGENTS = BASE_DIR / "data" / "sample_agents.csv"
SAMPLE_FORECAST = BASE_DIR / "data" / "sample_forecast.csv"
SAMPLE_RULES = BASE_DIR / "data" / "sample_rules.json"
OUTPUT_DIR = BASE_DIR / "outputs"


def load_uploads() -> tuple[pd.DataFrame | Path, pd.DataFrame | Path, dict | Path]:
    """Load uploaded files or fall back to sample data."""

    agents_file = st.file_uploader("Agents CSV", type=["csv"])
    forecast_file = st.file_uploader("Forecast CSV", type=["csv"])
    rules_file = st.file_uploader("Rules JSON", type=["json"])

    agents = pd.read_csv(agents_file) if agents_file else SAMPLE_AGENTS
    forecast = pd.read_csv(forecast_file) if forecast_file else SAMPLE_FORECAST
    rules = json.load(rules_file) if rules_file else SAMPLE_RULES
    return agents, forecast, rules


def main() -> None:
    st.set_page_config(page_title="WFM Planning Agent", page_icon="WFM", layout="wide")
    st.title("WFM Planning Agent")
    st.caption("Local AI-agent-style assistant for staffing, schedule validation, and rotation fairness")

    with st.sidebar:
        st.header("Project")
        st.write("Track: Agents for Business")
        st.write("Runs locally. No paid API. No external LLM.")
        st.write(
            "The agent analyzes forecast gaps, ranks weekend candidates, generates shifts, validates constraints, and writes a planning report."
        )

    agents, forecast, rules = load_uploads()
    run_button = st.button("Run Planning Agent", type="primary")

    if not run_button:
        st.info("Upload files or use the bundled sample data, then run the planning agent.")
        return

    try:
        agent = WFMPlanningAgent(agents=agents, forecast=forecast, rules=rules)
        result = agent.run(output_dir=OUTPUT_DIR)
    except Exception as exc:
        st.error(f"Planning agent failed: {exc}")
        return

    st.success("Planning agent completed.")
    forecast_df = result.forecast_with_gap
    schedule_df = result.schedule
    warnings_df = result.validation_warnings

    tab_forecast, tab_schedule, tab_warnings, tab_reasoning, tab_report = st.tabs(
        [
            "Forecast Overview",
            "Generated Schedule",
            "Constraint Warnings",
            "Agent Reasoning",
            "Final Report",
        ]
    )

    with tab_forecast:
        metric_cols = st.columns(4)
        metric_cols[0].metric("Intervals", result.forecast_summary["total_intervals"])
        metric_cols[1].metric("Understaffed", result.forecast_summary["total_understaffed_intervals"])
        metric_cols[2].metric("Overstaffed", result.forecast_summary["total_overstaffed_intervals"])
        metric_cols[3].metric("Largest shortage", f"{result.forecast_summary['largest_shortage_fte']:.0f} FTE")
        st.plotly_chart(fte_gap_chart(forecast_df), use_container_width=True)
        st.plotly_chart(required_vs_available_chart(forecast_df), use_container_width=True)
        st.dataframe(forecast_df, use_container_width=True, hide_index=True)

    with tab_schedule:
        st.plotly_chart(weekend_assignment_chart(schedule_df), use_container_width=True)
        st.dataframe(schedule_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download generated_schedule.csv",
            schedule_df.to_csv(index=False).encode("utf-8"),
            file_name="generated_schedule.csv",
            mime="text/csv",
        )

    with tab_warnings:
        if warnings_df.empty:
            st.success("No validation warnings found.")
        else:
            st.dataframe(warnings_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download validation_warnings.csv",
            warnings_df.to_csv(index=False).encode("utf-8"),
            file_name="validation_warnings.csv",
            mime="text/csv",
        )

    with tab_reasoning:
        for line in result.reasoning_log:
            st.write(line)

    with tab_report:
        st.markdown(result.report_markdown)
        st.download_button(
            "Download planning_report.md",
            result.report_markdown.encode("utf-8"),
            file_name="planning_report.md",
            mime="text/markdown",
        )


if __name__ == "__main__":
    main()
