import argparse
import json
import time
from datetime import datetime
from pathlib import Path

from agent.executor import ActionExecutor
from agent.loop import AgentLoop
from computer import Computer
from evals.calculator_cases import (
    CALCULATOR_CASES,
)


PROVIDERS = [
    "anthropic",
    "openai",
]


def normalize_number(
    value: str | None,
):
    if value is None:
        return None

    return (
        value
        .replace(",", "")
        .replace(" ", "")
        .strip()
    )


def prepare_calculator(
    computer: Computer,
):
    """
    Benchmark setup only.

    Ensure Calculator is open/focused,
    then clear it before each case.
    """

    computer.applications.ensure(
        title_pattern=r".*Calculator.*",
        executable="calc.exe",
    )

    time.sleep(0.4)

    observation = (
        computer.observe()
    )

    clear_control = None

    for control in observation[
        "controls"
    ]:
        if (
            control.get("role")
            == "Button"
            and control.get("name")
            == "Clear"
        ):
            clear_control = control
            break

    if clear_control is None:
        raise RuntimeError(
            "Could not find Calculator "
            "Clear button."
        )

    executor = ActionExecutor(
        computer
    )

    executor.execute(
        {
            "action": "click",
            "target":
                clear_control["id"],
        }
    )

    time.sleep(0.4)


def read_calculator_display(
    computer: Computer,
):
    observation = (
        computer.observe()
    )

    for control in observation[
        "controls"
    ]:
        name = control.get(
            "name",
            "",
        )

        if name.startswith(
            "Display is "
        ):
            return name.removeprefix(
                "Display is "
            )

    return None


def count_clear_actions(
    history: list[dict],
):
    return sum(
        1
        for item in history
        if item.get(
            "target_name"
        )
        in {
            "Clear",
            "Clear entry",
        }
    )


def run_case(
    computer: Computer,
    provider: str,
    case: dict,
):
    print(
        "\n\n"
        "======================================"
    )
    print(
        f"PROVIDER: {provider.upper()}"
    )
    print(
        f"CASE: {case['id']}"
    )
    print(
        f"GOAL: {case['goal']}"
    )
    print(
        "======================================"
    )

    prepare_calculator(
        computer
    )

    agent = AgentLoop(
        computer,
        model_provider=provider,
        max_steps=20,
    )

    started = (
        time.perf_counter()
    )

    try:
        result = agent.run(
            case["goal"]
        )

        runtime_error = None

    except Exception as exc:
        result = {
            "status": "runtime_error",
            "history": [],
        }

        runtime_error = (
            f"{type(exc).__name__}: "
            f"{exc}"
        )

    elapsed = (
        time.perf_counter()
        - started
    )

    actual = (
        read_calculator_display(
            computer
        )
    )

    expected = (
        normalize_number(
            case["expected"]
        )
    )

    actual_normalized = (
        normalize_number(
            actual
        )
    )

    history = result.get(
        "history",
        [],
    )

    passed = (
        result.get("status")
        == "success"
        and actual_normalized
        == expected
    )

    return {
        "provider": provider,
        "case": case["id"],
        "goal": case["goal"],
        "passed": passed,
        "expected": case[
            "expected"
        ],
        "actual": actual,
        "agent_status": result.get(
            "status"
        ),
        "action_count": len(
            history
        ),
        "clear_actions":
            count_clear_actions(
                history
            ),
        "elapsed_seconds": round(
            elapsed,
            2,
        ),
        "runtime_error":
            runtime_error,
    }


def print_summary(
    results: list[dict],
):
    print(
        "\n\n"
        "======================================"
    )
    print(
        "MODEL COMPARISON SUMMARY"
    )
    print(
        "======================================"
    )

    for provider in PROVIDERS:
        provider_results = [
            result
            for result in results
            if result["provider"]
            == provider
        ]

        if not provider_results:
            continue

        passed = sum(
            result["passed"]
            for result
            in provider_results
        )

        total = len(
            provider_results
        )

        actions = sum(
            result["action_count"]
            for result
            in provider_results
        )

        clears = sum(
            result["clear_actions"]
            for result
            in provider_results
        )

        elapsed = sum(
            result["elapsed_seconds"]
            for result
            in provider_results
        )

        print(
            f"\n{provider.upper()}"
        )

        for result in (
            provider_results
        ):
            icon = (
                "✅"
                if result["passed"]
                else "❌"
            )

            print(
                f"{icon} "
                f"{result['case']}: "
                f"expected="
                f"{result['expected']}, "
                f"actual="
                f"{result['actual']}, "
                f"status="
                f"{result['agent_status']}, "
                f"actions="
                f"{result['action_count']}, "
                f"clears="
                f"{result['clear_actions']}, "
                f"time="
                f"{result['elapsed_seconds']}s"
            )

        print(
            f"Success rate: "
            f"{passed}/{total} "
            f"({passed / total:.0%})"
        )

        print(
            "Average actions: "
            f"{actions / total:.2f}"
        )

        print(
            "Clear actions: "
            f"{clears}"
        )

        print(
            "Average time: "
            f"{elapsed / total:.2f}s"
        )


def save_results(
    results: list[dict],
):
    output_dir = Path(
        ".runtime/evals"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = (
        datetime.now()
        .strftime(
            "%Y%m%d_%H%M%S"
        )
    )

    path = (
        output_dir
        / f"model_comparison_{timestamp}.json"
    )

    path.write_text(
        json.dumps(
            results,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"\nResults saved to: {path}"
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--smoke",
        action="store_true",
        help=(
            "Run one case per provider "
            "before the full benchmark."
        ),
    )

    args = parser.parse_args()

    cases = (
        CALCULATOR_CASES[:1]
        if args.smoke
        else CALCULATOR_CASES[:5]
    )

    computer = Computer()

    results = []

    for provider in PROVIDERS:
        for case in cases:
            result = run_case(
                computer,
                provider,
                case,
            )

            results.append(
                result
            )

    print_summary(
        results
    )

    save_results(
        results
    )


if __name__ == "__main__":
    main()