"""Command-line entry point."""

from __future__ import annotations

import argparse
import sys

from crewai import CrewOutput

from hundred_schools.config import Settings
from hundred_schools.crews.council_crew import build_council_crew
from hundred_schools.models.response import AdviserOpinion, length_warning
from hundred_schools.observability import setup_langfuse


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="hundred-schools",
        description=(
            "Ask the Hundred Schools Advisory for advice from different philosophical traditions."
        ),
    )
    parser.add_argument("question", nargs="?", help="The question you want the advisory to analyze")
    return parser.parse_args()


def _print_output(result: CrewOutput) -> None:
    """Render CrewAI task outputs in task order."""
    outputs = result.tasks_output
    schools = ["Confucian", "Legalist", "Taoist", "Strategist"]
    if len(outputs) != len(schools):
        print(f"Note: expected {len(schools)} advice items, got {len(outputs)}.")

    for index, task_output in enumerate(outputs):
        school = schools[index] if index < len(schools) else f"Adviser {index + 1}"
        advice = str(task_output.raw).strip()
        opinion = AdviserOpinion(school=school, advice=advice)
        print(f"\n[{opinion.school} Adviser]\n{opinion.advice}")
        warning = length_warning(opinion)
        if warning:
            print(f"  [Length note] {warning}")


def main() -> int:
    """Run the interactive or one-shot CLI."""
    args = parse_args()
    question = (args.question or "").strip()
    if not question:
        try:
            question = input("Enter a question for the Hundred Schools to analyze: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nCancelled.", file=sys.stderr)
            return 130

    if not question:
        print("Question cannot be empty.", file=sys.stderr)
        return 2

    try:
        settings = Settings.from_env()
        setup_langfuse()
        crew = build_council_crew(settings)
        result = crew.kickoff(inputs={"question": question})
        _print_output(result)
    except Exception as exc:  # CLI boundary: show a concise actionable failure.
        print(f"Run failed: {exc}", file=sys.stderr)
        print(
            "Please check your model configuration in .env, API Key, and network connection.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
