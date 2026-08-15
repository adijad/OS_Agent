import re
import time

from agent.executor import ActionExecutor
from agent.loop import AgentLoop
from computer import Computer
from evals.calculator_cases import CALCULATOR_CASES


def normalize_number(value: str) -> str:
    """
    Turn values like:

        '38,346'
        ' 38346 '
        'Display is 38,346'

    into:

        '38346'
    """

    return (
        value
        .replace(",", "")
        .replace(" ", "")
        .strip()
    )


def read_calculator_display(
    computer: Computer,
):
    observation = computer.observe()

    for control in observation["controls"]:
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


def clear_calculator(
    computer: Computer,
):
    """
    Reset Calculator before each evaluation case.

    This is benchmark setup, not agent reasoning.
    """

    observation = computer.observe()

    clear_control = None

    for control in observation["controls"]:
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
            "target": clear_control["id"],
        }
    )

    time.sleep(0.5)


def count_unnecessary_actions(
    history: list[dict],
):
    """
    For a benchmark that begins with a clean
    Calculator, Clear/Clear Entry actions are
    generally unnecessary.
    """

    count = 0

    for item in history:
        target_name = item.get(
            "target_name"
        )

        if target_name in {
            "Clear",
            "Clear entry",
        }:
            count += 1

    return count


def run_case(
    computer: Computer,
    case: dict,
):
    print(
        "\n\n"
        "======================================"
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

    clear_calculator(
        computer
    )

    agent = AgentLoop(
        computer,
        max_steps=20,
    )

    started = time.perf_counter()

    result = agent.run(
        case["goal"]
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

    expected_normalized = (
        normalize_number(
            case["expected"]
        )
    )

    actual_normalized = (
        normalize_number(actual)
        if actual is not None
        else None
    )

    passed = (
        result["status"]
        == "success"
        and actual_normalized
        == expected_normalized
    )

    history = result.get(
        "history",
        [],
    )

    return {
        "case": case["id"],
        "goal": case["goal"],
        "passed": passed,
        "expected": case[
            "expected"
        ],
        "actual": actual,
        "action_count": len(
            history
        ),
        "unnecessary_actions":
            count_unnecessary_actions(
                history
            ),
        "elapsed_seconds": round(
            elapsed,
            2,
        ),
        "agent_status": result[
            "status"
        ],
    }


def print_summary(
    results: list[dict],
):
    print(
        "\n\n"
        "======================================"
    )
    print(
        "CALCULATOR EVALUATION SUMMARY"
    )
    print(
        "======================================"
    )

    passed = sum(
        result["passed"]
        for result in results
    )

    total = len(results)

    total_actions = sum(
        result["action_count"]
        for result in results
    )

    unnecessary = sum(
        result[
            "unnecessary_actions"
        ]
        for result in results
    )

    for result in results:
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
            f"actions="
            f"{result['action_count']}, "
            f"unnecessary="
            f"{result['unnecessary_actions']}, "
            f"time="
            f"{result['elapsed_seconds']}s"
        )

    print()

    print(
        f"Success rate: "
        f"{passed}/{total} "
        f"({passed / total:.0%})"
    )

    if total:
        print(
            f"Average actions: "
            f"{total_actions / total:.2f}"
        )

    print(
        f"Unnecessary actions: "
        f"{unnecessary}"
    )


def main():
    computer = Computer()

    print(
        "Switch to Calculator."
    )
    print(
        "Evaluation starts in 5 seconds..."
    )

    time.sleep(5)

    # Start with THREE cases.
    #
    # Do not immediately spend API calls
    # running the entire suite.
    cases = CALCULATOR_CASES[:3]

    results = []

    for case in cases:
        result = run_case(
            computer,
            case,
        )

        results.append(
            result
        )

    print_summary(
        results
    )


if __name__ == "__main__":
    main()