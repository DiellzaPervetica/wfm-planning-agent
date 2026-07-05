# Evaluation

## Core Concept and Value

The project addresses a real business planning workflow: creating a draft WFM schedule from forecast and agent data. It has practical value because it helps a planner see coverage gaps, fairness tradeoffs, and validation risks before publishing a schedule.

## Technical Implementation

The implementation is intentionally lightweight and runnable in a short time window. It includes a Python package, Streamlit app, CLI entrypoint, sample data, structured models, deterministic tools, tests, and documentation.

## Agentic Tool Use

The system behaves like a local business agent:

- It receives a planning request.
- It chooses a fixed sequence of specialized tools.
- It stores intermediate outputs.
- It creates a reasoning log.
- It validates its own output before returning a final report.

This demonstrates orchestration and tool use without relying on paid APIs.

## Quality and Testing

The test suite covers the highest-risk pieces:

- Forecast gap calculation.
- Understaffed interval labeling.
- Vacation assignment avoidance.
- Weekend minimum staffing.
- Validation of a known bad schedule.
- End-to-end agent output generation.

## Documentation

The repository includes:

- `README.md` for setup and usage.
- `docs/architecture.md` for design.
- `docs/kaggle_writeup.md` for submission text.
- `docs/demo_script.md` for a 2-4 minute video.
- `docs/limitations.md` for honest constraints.

## Business Relevance

The project is aligned with the Agents for Business track because it automates a repeatable business decision-support workflow. It is not a toy chatbot; it produces operational artifacts that a WFM analyst could review, export, and improve.

## Suggested Manual Review

Before submitting, run the app, inspect the warnings, record the video, then update the writeup with the final GitHub and video links.
