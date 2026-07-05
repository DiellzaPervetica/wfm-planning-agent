# WFM Planning Agent

Local AI-agent-style assistant for staffing, schedule validation, and rotation fairness.

Kaggle track: Agents for Business

Repository: https://github.com/DiellzaPervetica/wfm-planning-agent

## Problem Statement

Workforce Management analysts often need to convert interval-level staffing forecasts into practical schedules while balancing coverage, vacation status, weekend rotation fairness, and business rules. This is usually manual, time-sensitive, and hard to audit.

WFM Planning Agent is a lightweight local prototype that helps a planner inspect staffing gaps, generate a draft schedule, validate constraints, and export a business-friendly report.

## Why This Matters

Understaffed intervals can increase customer wait time and service risk. Overstaffed intervals can waste paid capacity. Weekend scheduling can also become unfair if recent assignments are not tracked. A transparent local agent can help planners make faster, more consistent decisions while keeping a human in control.

## Main Features

- Forecast gap analysis by date and interval.
- Weekend candidate ranking using fairness and availability.
- Draft schedule generation for weekdays, Saturday, and Sunday.
- Constraint validation for vacation, weekend minimums, shift starts, shift length, lunch windows, duplicate assignments, double weekend work, and peak coverage.
- Explainable reasoning log for each tool call.
- Streamlit dashboard with charts, tables, and downloads.
- CLI runner that saves CSV and Markdown outputs.
- Pytest coverage for the core workflow.
- No paid APIs, no external LLM, and no API keys.

## Agent Architecture

The project demonstrates an agentic workflow through a deterministic local orchestrator:

1. `WFMPlanningAgent` receives forecast, agent, and rule inputs.
2. `ForecastAnalyzerTool` detects gaps and critical intervals.
3. `RotationFairnessTool` ranks weekend candidates.
4. `ScheduleGeneratorTool` creates a draft schedule.
5. `ConstraintValidatorTool` checks guardrails.
6. `ReportWriterTool` writes the final Markdown report.

The agent stores intermediate state and a reasoning log so a human planner can inspect why each step happened.

## Installation

```powershell
cd "C:\Users\perve\Desktop\kaggle project\wfm-planning-agent"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run the Streamlit App

```powershell
streamlit run app.py
```

If no files are uploaded, the app uses the bundled sample files in `data/`.

## Run the CLI

```powershell
python cli.py --agents data/sample_agents.csv --forecast data/sample_forecast.csv --rules data/sample_rules.json
```

Outputs are saved to `outputs/`:

- `generated_schedule.csv`
- `validation_warnings.csv`
- `planning_report.md`

## Run Tests

```powershell
pytest
```

## Sample Screenshots

Add screenshots after running the Streamlit app locally:

- Forecast Overview tab
- Generated Schedule tab
- Constraint Warnings tab
- Final Report tab

## Local-Only Safety Note

This project intentionally avoids paid external APIs. It does not require OpenAI, Gemini, Claude, Anthropic, Azure, Hugging Face endpoints, cloud services, credit cards, or API keys. The "agent" behavior is implemented locally through an orchestrator, tools, validation, and deterministic reasoning traces.

## Limitations

- Sample data is fake and simplified.
- The schedule uses heuristics, not mathematical optimization.
- Compliance rules are only examples and should be expanded for production.
- A human WFM planner should review the final schedule before use.

## Future Improvements

- Add anonymized real-world WFM datasets.
- Add configurable skill and site coverage rules.
- Add labor-law and contract compliance checks.
- Add optimization-based schedule search.
- Add integrations with HR, forecasting, and ticketing systems.
