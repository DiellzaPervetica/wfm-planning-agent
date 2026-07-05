"""Command-line entrypoint for the WFM Planning Agent."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.agent import WFMPlanningAgent


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the local WFM Planning Agent.")
    parser.add_argument("--agents", default="data/sample_agents.csv", help="Path to agents CSV.")
    parser.add_argument("--forecast", default="data/sample_forecast.csv", help="Path to forecast CSV.")
    parser.add_argument("--rules", default="data/sample_rules.json", help="Path to rules JSON.")
    parser.add_argument("--output-dir", default="outputs", help="Directory for generated outputs.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    agent = WFMPlanningAgent(args.agents, args.forecast, args.rules)
    result = agent.run(output_dir=args.output_dir)

    print("WFM Planning Agent completed successfully.")
    print(f"Generated assignments: {len(result.schedule)}")
    print(f"Validation warnings: {len(result.validation_warnings)}")
    print("Saved outputs:")
    for label, path in result.output_paths.items():
        print(f"- {label}: {Path(path)}")


if __name__ == "__main__":
    main()
