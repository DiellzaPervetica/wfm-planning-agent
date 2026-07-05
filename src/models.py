"""Pydantic models for the WFM Planning Agent."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Agent(BaseModel):
    """A planning agent or employee available for scheduling."""

    agent_id: str
    agent_name: str
    skill: str
    site: str
    contract_hours: int
    available_days: list[str]
    preferred_start: str
    last_weekend_worked: int = 0
    last_shift_start: str
    vacation: bool = False


class ForecastInterval(BaseModel):
    """Forecasted required and available FTE for one interval."""

    date: str
    day_name: str
    interval: str
    required_fte: float
    available_fte: float


class PlanningRules(BaseModel):
    """Scheduling and validation rules used by the agent."""

    allowed_shift_starts: list[str]
    default_shift_hours: int = 8
    min_saturday_agents: int = 15
    min_sunday_agents: int = 15
    max_same_start_repetition: int = 2
    avoid_vacation_assignments: bool = True
    weekend_fairness_weight: float = 0.4
    coverage_weight: float = 0.4
    preference_weight: float = 0.2
    lunch_after_hours: list[float] = Field(default_factory=lambda: [4])


class ScheduleAssignment(BaseModel):
    """One generated shift assignment."""

    date: str
    day_name: str
    agent_id: str
    agent_name: str
    skill: str
    site: str
    shift_start: str
    shift_end: str
    lunch_start: str
    lunch_end: str
    assignment_reason: str


class ValidationWarning(BaseModel):
    """Validation finding emitted by the constraint validator."""

    severity: str
    rule: str
    agent_name: str | None = None
    date: str | None = None
    message: str
    recommendation: str


class AgentRunResult(BaseModel):
    """Final output object returned by the local planning agent."""

    forecast_summary: dict[str, Any]
    forecast_with_gap: Any
    weekend_rankings: dict[str, Any]
    schedule: Any
    validation_warnings: Any
    report_markdown: str
    reasoning_log: list[str]
    output_paths: dict[str, str] = Field(default_factory=dict)
