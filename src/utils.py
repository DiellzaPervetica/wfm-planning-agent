"""Shared loading, validation, and time helpers."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from src.models import Agent, ForecastInterval, PlanningRules


AGENT_COLUMNS = [
    "agent_id",
    "agent_name",
    "skill",
    "site",
    "contract_hours",
    "available_days",
    "preferred_start",
    "last_weekend_worked",
    "last_shift_start",
    "vacation",
]

FORECAST_COLUMNS = ["date", "day_name", "interval", "required_fte", "available_fte"]

OUTPUT_COLUMNS = {
    "schedule": [
        "date",
        "day_name",
        "agent_id",
        "agent_name",
        "skill",
        "site",
        "shift_start",
        "shift_end",
        "lunch_start",
        "lunch_end",
        "assignment_reason",
    ],
    "warnings": ["severity", "rule", "agent_name", "date", "message", "recommendation"],
}


def ensure_columns(df: pd.DataFrame, required: Iterable[str], source_name: str) -> None:
    """Raise a helpful error if a dataframe is missing required columns."""

    missing = [column for column in required if column not in df.columns]
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(f"{source_name} is missing required column(s): {missing_list}")


def parse_bool(value: Any) -> bool:
    """Parse common CSV boolean values."""

    if isinstance(value, bool):
        return value
    if pd.isna(value):
        return False
    return str(value).strip().lower() in {"1", "true", "yes", "y"}


def parse_available_days(value: Any) -> list[str]:
    """Parse a comma-separated available_days field into normalized day tokens."""

    if isinstance(value, list):
        return [str(day).strip() for day in value if str(day).strip()]
    if pd.isna(value):
        return []
    return [day.strip() for day in str(value).split(",") if day.strip()]


def normalize_day(day_name: str) -> str:
    """Return the three-letter day token used in agent availability."""

    return str(day_name).strip()[:3].title()


def load_agents(source: str | Path | pd.DataFrame) -> pd.DataFrame:
    """Load and validate agent data from a path or dataframe."""

    df = source.copy() if isinstance(source, pd.DataFrame) else pd.read_csv(source)
    ensure_columns(df, AGENT_COLUMNS, "agents CSV")
    df = df.copy()
    df["agent_id"] = df["agent_id"].astype(str)
    df["agent_name"] = df["agent_name"].astype(str)
    df["skill"] = df["skill"].astype(str)
    df["site"] = df["site"].astype(str)
    df["contract_hours"] = df["contract_hours"].astype(int)
    df["available_days"] = df["available_days"].apply(parse_available_days)
    df["preferred_start"] = df["preferred_start"].astype(str)
    df["last_weekend_worked"] = df["last_weekend_worked"].astype(int)
    df["last_shift_start"] = df["last_shift_start"].astype(str)
    df["vacation"] = df["vacation"].apply(parse_bool)

    for record in df.to_dict("records"):
        Agent(**record)
    return df


def load_forecast(source: str | Path | pd.DataFrame) -> pd.DataFrame:
    """Load and validate forecast data from a path or dataframe."""

    df = source.copy() if isinstance(source, pd.DataFrame) else pd.read_csv(source)
    ensure_columns(df, FORECAST_COLUMNS, "forecast CSV")
    df = df.copy()
    df["date"] = df["date"].astype(str)
    df["day_name"] = df["day_name"].astype(str)
    df["interval"] = df["interval"].astype(str)
    df["required_fte"] = pd.to_numeric(df["required_fte"])
    df["available_fte"] = pd.to_numeric(df["available_fte"])

    for record in df.to_dict("records"):
        ForecastInterval(**record)
    return df


def load_rules(source: str | Path | dict[str, Any] | PlanningRules) -> PlanningRules:
    """Load and validate planning rules from a path, dictionary, or model."""

    if isinstance(source, PlanningRules):
        return source
    if isinstance(source, (str, Path)):
        with Path(source).open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    else:
        payload = source
    return PlanningRules(**payload)


def time_to_minutes(value: str) -> int:
    """Convert HH:MM to minutes after midnight."""

    parsed = datetime.strptime(value, "%H:%M")
    return parsed.hour * 60 + parsed.minute


def minutes_to_time(value: int) -> str:
    """Convert minutes after midnight to HH:MM."""

    hours = (value // 60) % 24
    minutes = value % 60
    return f"{hours:02d}:{minutes:02d}"


def add_hours(start: str, hours: float) -> str:
    """Add fractional hours to an HH:MM time string."""

    base = datetime.strptime(start, "%H:%M")
    result = base + timedelta(minutes=int(hours * 60))
    return result.strftime("%H:%M")


def empty_schedule_frame() -> pd.DataFrame:
    """Return an empty schedule dataframe with stable columns."""

    return pd.DataFrame(columns=OUTPUT_COLUMNS["schedule"])


def empty_warnings_frame() -> pd.DataFrame:
    """Return an empty validation warning dataframe with stable columns."""

    return pd.DataFrame(columns=OUTPUT_COLUMNS["warnings"])
