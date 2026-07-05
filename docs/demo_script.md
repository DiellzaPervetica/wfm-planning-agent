# Demo Video Script

Target length: 2 to 4 minutes.

## Intro

Hi, my name is Diellza, and this is my Kaggle AI Agents capstone project for the Agents for Business track. The project is called WFM Planning Agent.

It is a local AI-agent-style assistant for workforce planning. It helps a planner analyze staffing gaps, generate a draft schedule, validate constraints, and produce a final planning report.

## Problem

In workforce management, planners often need to turn interval-level demand forecasts into practical schedules. They also need to avoid vacation conflicts, meet weekend staffing minimums, and keep weekend rotation fair.

This can be repetitive and hard to audit, especially when the planner needs to explain why certain people were assigned.

## Show the App

Here is the Streamlit app. On the left side, I show the project track and the local-only safety note. This project does not use paid APIs, external LLMs, or API keys. Everything runs locally with Python libraries.

The app can accept uploaded files for agents, forecast, and rules. For the demo, I will use the bundled sample data.

## Run Planning Agent

Now I click "Run Planning Agent."

The local orchestrator loads the inputs and calls five tools: a forecast analyzer, a weekend rotation fairness tool, a schedule generator, a constraint validator, and a report writer.

## Forecast Overview

In the Forecast Overview tab, we can see the number of understaffed and overstaffed intervals. The first chart shows the FTE gap for each interval. Negative values show where demand is higher than available staffing.

The second chart compares required FTE and available FTE across the planning week.

## Generated Schedule

In the Generated Schedule tab, the agent shows the draft schedule. It assigns agents only when they are available and not marked as vacation.

For weekends, the schedule uses the fairness ranking so agents with fewer recent weekend assignments are preferred. The chart shows how many weekend assignments each agent received.

## Constraint Warnings

In the Constraint Warnings tab, the validator lists issues that a human planner should review. These include coverage risks during peak intervals or fairness concerns such as an agent working both Saturday and Sunday.

This is important because the agent is not pretending the draft is perfect. It validates itself and highlights what needs human review.

## Agent Reasoning

In the Agent Reasoning tab, we can see the trace of the local workflow. Each step explains which tool was called and what it found.

This makes the process auditable and easier to trust than a black-box recommendation.

## Final Report

In the Final Report tab, the app generates a Markdown report with an executive summary, forecast findings, scheduling approach, weekend fairness, validation results, risks, and next steps.

The user can download the generated schedule, validation warnings, and planning report.

## Closing

To summarize, WFM Planning Agent demonstrates an agentic business workflow without paid APIs. It uses local tools, deterministic reasoning, guardrails, tests, and documentation to support a realistic workforce planning use case.

Thank you for watching.
