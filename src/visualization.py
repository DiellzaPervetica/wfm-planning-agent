"""Plotly chart helpers for the Streamlit app."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def fte_gap_chart(forecast_df: pd.DataFrame) -> go.Figure:
    """Create a bar chart showing staffing gap by date and interval."""

    chart_df = forecast_df.copy()
    chart_df["slot"] = chart_df["date"].astype(str) + " " + chart_df["interval"].astype(str)
    fig = px.bar(
        chart_df,
        x="slot",
        y="gap",
        color="status",
        color_discrete_map={
            "understaffed": "#D64545",
            "balanced": "#6B7280",
            "overstaffed": "#2E8B57",
        },
        title="FTE Gap by Interval",
        labels={"slot": "Planning interval", "gap": "Available FTE - Required FTE"},
    )
    fig.update_layout(xaxis_tickangle=-45, height=420, margin=dict(l=20, r=20, t=60, b=120))
    return fig


def required_vs_available_chart(forecast_df: pd.DataFrame) -> go.Figure:
    """Create a line chart comparing required and available FTE."""

    chart_df = forecast_df.copy()
    chart_df["slot"] = chart_df["date"].astype(str) + " " + chart_df["interval"].astype(str)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=chart_df["slot"],
            y=chart_df["required_fte"],
            mode="lines+markers",
            name="Required FTE",
            line=dict(color="#1F4E79", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=chart_df["slot"],
            y=chart_df["available_fte"],
            mode="lines+markers",
            name="Available FTE",
            line=dict(color="#D19A00", width=2),
        )
    )
    fig.update_layout(
        title="Required vs Available FTE",
        xaxis_title="Planning interval",
        yaxis_title="FTE",
        xaxis_tickangle=-45,
        height=420,
        margin=dict(l=20, r=20, t=60, b=120),
    )
    return fig


def weekend_assignment_chart(schedule_df: pd.DataFrame) -> go.Figure:
    """Create a weekend assignment count chart."""

    weekend = schedule_df[schedule_df["day_name"].isin(["Saturday", "Sunday"])]
    if weekend.empty:
        fig = go.Figure()
        fig.update_layout(title="Weekend Assignment Count by Agent")
        return fig

    counts = (
        weekend.groupby("agent_name")["date"]
        .count()
        .reset_index(name="weekend_assignments")
        .sort_values(["weekend_assignments", "agent_name"], ascending=[False, True])
    )
    fig = px.bar(
        counts,
        x="agent_name",
        y="weekend_assignments",
        title="Weekend Assignment Count by Agent",
        labels={"agent_name": "Agent", "weekend_assignments": "Assignments"},
        color="weekend_assignments",
        color_continuous_scale=["#76B7B2", "#E15759"],
    )
    fig.update_layout(xaxis_tickangle=-45, height=400, margin=dict(l=20, r=20, t=60, b=110))
    return fig
