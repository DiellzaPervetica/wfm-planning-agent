# WFM Planning Agent

## Track

Agents for Business

## Problem Statement

Workforce Management teams need to translate interval-level staffing forecasts into schedules that are practical, fair, and compliant with planning rules. This is often done under time pressure, especially when weekend staffing and vacation constraints change quickly.

WFM Planning Agent is a local agent-style assistant that helps a planner analyze staffing gaps, create a draft schedule, validate constraints, and generate a business-friendly report.

## Motivation

Call-center staffing decisions affect customer wait time, service quality, employee fairness, and operational cost. A planner needs more than a raw forecast; they need a repeatable workflow that explains why a recommendation was made and flags risks before the schedule is shared.

## What the Agent Does

The agent accepts three inputs:

- Agent availability and profile data.
- Interval-level forecast demand and available FTE.
- Planning rules for allowed starts, shift length, weekend minimums, vacation handling, and fairness weights.

It then:

- Calculates staffing gaps by interval.
- Identifies the most critical understaffed periods.
- Ranks Saturday and Sunday candidates by fairness.
- Generates a draft weekly schedule.
- Validates the schedule against guardrails.
- Writes a final Markdown report and exportable CSV files.

## Architecture

This project intentionally avoids paid external APIs. Instead, it demonstrates an agentic workflow through a local orchestrator, deterministic tools, validation, and explainable reasoning.

The orchestrator is `WFMPlanningAgent`. It calls five tools:

1. `ForecastAnalyzerTool`
2. `RotationFairnessTool`
3. `ScheduleGeneratorTool`
4. `ConstraintValidatorTool`
5. `ReportWriterTool`

Each tool has a clear responsibility and returns structured intermediate outputs. The agent stores a reasoning log so the final result is auditable.

## Tool Use

`ForecastAnalyzerTool` computes `gap = available_fte - required_fte` and labels intervals as understaffed, balanced, or overstaffed.

`RotationFairnessTool` scores weekend candidates based on availability, vacation status, recent weekend workload, and preferred shift start.

`ScheduleGeneratorTool` creates weekday and weekend assignments using allowed starts and avoiding vacation agents.

`ConstraintValidatorTool` checks vacation assignments, weekend minimums, shift start validity, shift length, lunch placement, duplicate assignments, double weekend work, and peak interval coverage.

`ReportWriterTool` creates a human-readable Markdown report from the computed outputs.

## Technical Implementation

The project is written in Python and uses:

- pandas and numpy for data handling.
- pydantic for input models and rule validation.
- streamlit for the local dashboard.
- plotly for charts.
- pytest for automated tests.

The app runs with:

```powershell
streamlit run app.py
```

The CLI runs with:

```powershell
python cli.py --agents data/sample_agents.csv --forecast data/sample_forecast.csv --rules data/sample_rules.json
```

## Evaluation and Tests

The test suite verifies that:

- Forecast gaps are calculated correctly.
- Understaffed intervals are labeled correctly.
- Vacation agents are not scheduled by the generator.
- Saturday and Sunday minimum staffing rules are met.
- The validator catches a deliberate vacation assignment.
- The full agent returns a schedule, warnings, report, reasoning log, and saved outputs.

Tests run with:

```powershell
pytest
```

## Guardrails and Safety

The project has several guardrails:

- No paid APIs.
- No external LLM calls.
- No API keys.
- No private employee data.
- Explicit validation warnings before outputs are presented as recommendations.
- Human review recommendation in the final report.

## Results

On the bundled sample week, the agent detects understaffed intervals, generates a complete draft schedule, ranks weekend candidates, flags coverage and fairness risks, and exports three planning artifacts:

- `generated_schedule.csv`
- `validation_warnings.csv`
- `planning_report.md`

The Streamlit UI also displays forecast charts, schedule tables, warning tables, reasoning trace, and the final report.

## Limitations

This is a prototype, not a production WFM optimizer. It uses fake sample data and deterministic heuristics. Real deployments would need anonymized production data, local compliance rules, labor policy checks, HR integrations, forecasting integrations, and planner approval workflows.

## Future Work

- Add skill-specific coverage checks.
- Add site-level staffing minimums.
- Add optimization-based shift search.
- Add scenario comparison.
- Add planner feedback loops to tune fairness weights.
- Integrate with HR and forecasting systems.

## Repository Link

https://github.com/DiellzaPervetica/wfm-planning-agent

## Video Link

TODO: Add YouTube or Kaggle video link after recording.
