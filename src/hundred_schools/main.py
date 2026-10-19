"""Command-line entry point."""

from __future__ import annotations

import argparse
import sys

from crewai import CrewOutput

from hundred_schools.config import Settings
from hundred_schools.crews.council_crew import build_council_crew
from hundred_schools.models.response import AdviserOpinion, length_warning


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="hundred-schools",
        description="向诸子百家智囊团提问，获取不同思想流派的建议。",
    )
    parser.add_argument("question", nargs="?", help="希望智囊团分析的问题")
    return parser.parse_args()


def _print_output(result: CrewOutput) -> None:
    """Render CrewAI task outputs in task order."""
    outputs = result.tasks_output
    schools = ["儒家", "法家", "道家", "兵家"]
    if len(outputs) != len(schools):
        print(f"提示：预期得到 {len(schools)} 条建议，实际得到 {len(outputs)} 条。")

    for index, task_output in enumerate(outputs):
        school = schools[index] if index < len(schools) else f"智囊 {index + 1}"
        advice = str(task_output.raw).strip()
        opinion = AdviserOpinion(school=school, advice=advice)
        print(f"\n【{opinion.school}智囊】\n{opinion.advice}")
        warning = length_warning(opinion)
        if warning:
            print(f"  [长度提示] {warning}")


def main() -> int:
    """Run the interactive or one-shot CLI."""
    args = parse_args()
    question = (args.question or "").strip()
    if not question:
        try:
            question = input("请输入希望诸子百家分析的问题：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n已取消。", file=sys.stderr)
            return 130

    if not question:
        print("问题不能为空。", file=sys.stderr)
        return 2

    try:
        settings = Settings.from_env()
        crew = build_council_crew(settings)
        result = crew.kickoff(inputs={"question": question})
        _print_output(result)
    except Exception as exc:  # CLI boundary: show a concise actionable failure.
        print(f"运行失败：{exc}", file=sys.stderr)
        print("请检查 .env 中的模型配置、API Key 和网络连接。", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
