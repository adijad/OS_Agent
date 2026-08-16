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


# =========================================================
# NORMALIZATION
# =========================================================

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


# =========================================================
# BENCHMARK SETUP
# =========================================================

def prepare_calculator(
    computer: Computer,
):
    """
    Benchmark setup only.

    Ensure Calculator is open and focused,
    then clear it before each case.

    These setup actions are not counted
    as agent actions.
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


# =========================================================
# CALCULATOR STATE
# =========================================================

def read_calculator_state(
    computer: Computer,
):
    """
    Read both:

        current display
        current expression

    Example:

        display:
            38,346

        expression:
            Expression is 913 × 42 =

    This lets us distinguish:

        merely entering a number

    from:

        actually completing the calculation.
    """

    observation = (
        computer.observe()
    )

    display = None
    expression = None

    for control in observation[
        "controls"
    ]:
        name = control.get(
            "name",
            "",
        ).strip()

        text = control.get(
            "text",
            "",
        ).strip()

        # ---------------------------------------------
        # Calculator main display
        # ---------------------------------------------

        if name.startswith(
            "Display is "
        ):
            display = (
                name.removeprefix(
                    "Display is "
                )
            )

        # ---------------------------------------------
        # Calculator expression
        # ---------------------------------------------

        if name.startswith(
            "Expression is "
        ):
            expression = name

        elif (
            expression is None
            and text.startswith(
                "Expression is "
            )
        ):
            expression = text

    return {
        "display": display,
        "expression": expression,
    }


def expression_is_complete(
    expression: str | None,
):
    """
    Determine whether Calculator appears to have
    actually evaluated the expression.

    Typical completed expression:

        Expression is 913 × 42 =

    We intentionally require evidence of completion
    instead of trusting only the displayed number.
    """

    if not expression:
        return False

    normalized = (
        expression
        .strip()
        .lower()
    )

    # Standard Calculator accessibility state.
    if normalized.endswith("="):
        return True

    # Defensive fallback in case accessibility text
    # describes '=' using a word.
    if normalized.endswith("equals"):
        return True

    return False


# =========================================================
# ACTION METRICS
# =========================================================

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


def count_action_types(
    history: list[dict],
):
    counts = {
        "click": 0,
        "type_text": 0,
        "press_key": 0,
        "hotkey": 0,
        "focus_window": 0,
        "launch_application": 0,
    }

    for item in history:
        action_type = (
            item
            .get(
                "action",
                {},
            )
            .get(
                "action"
            )
        )

        if action_type in counts:
            counts[
                action_type
            ] += 1

    return counts


# =========================================================
# RUN ONE CASE
# =========================================================

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
        f"PROVIDER: "
        f"{provider.upper()}"
    )

    print(
        f"CASE: "
        f"{case['id']}"
    )

    print(
        f"GOAL: "
        f"{case['goal']}"
    )

    print(
        "======================================"
    )

    # -----------------------------------------------------
    # Prepare clean benchmark environment
    # -----------------------------------------------------

    prepare_calculator(
        computer
    )

    # -----------------------------------------------------
    # Create requested model agent
    # -----------------------------------------------------

    agent = AgentLoop(
        computer,
        model_provider=provider,
        max_steps=20,
    )

    started = (
        time.perf_counter()
    )

    # -----------------------------------------------------
    # Run autonomous trajectory
    # -----------------------------------------------------

    try:
        result = agent.run(
            case["goal"]
        )

        runtime_error = None

    except Exception as exc:
        result = {
            "status":
                "runtime_error",

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

    # -----------------------------------------------------
    # Independently inspect Calculator after agent stops
    # -----------------------------------------------------

    calculator_state = (
        read_calculator_state(
            computer
        )
    )

    actual = (
        calculator_state[
            "display"
        ]
    )

    expression = (
        calculator_state[
            "expression"
        ]
    )

    completed_expression = (
        expression_is_complete(
            expression
        )
    )

    # -----------------------------------------------------
    # Normalize expected / observed result
    # -----------------------------------------------------

    expected_normalized = (
        normalize_number(
            case["expected"]
        )
    )

    actual_normalized = (
        normalize_number(
            actual
        )
    )

    # -----------------------------------------------------
    # Trajectory metrics
    # -----------------------------------------------------

    history = result.get(
        "history",
        [],
    )

    action_types = (
        count_action_types(
            history
        )
    )

    # -----------------------------------------------------
    # STRICT PASS CONDITION
    #
    # We now require:
    #
    # 1. Agent declared success
    # 2. Display matches expected answer
    # 3. Expression indicates evaluation completed
    #
    # This prevents false positives such as:
    #
    #     144 ÷ 12
    #
    # where the current divisor is 12 and also happens
    # to equal the expected answer.
    # -----------------------------------------------------

    passed = (
        result.get("status")
        == "success"

        and actual_normalized
        == expected_normalized

        and completed_expression
    )

    return {
        "provider": provider,

        "case": case[
            "id"
        ],

        "goal": case[
            "goal"
        ],

        "passed": passed,

        "expected": case[
            "expected"
        ],

        "actual": actual,

        "expression":
            expression,

        "expression_complete":
            completed_expression,

        "agent_status":
            result.get(
                "status"
            ),

        "action_count": len(
            history
        ),

        "clear_actions":
            count_clear_actions(
                history
            ),

        # ---------------------------------------------
        # Interaction strategy
        # ---------------------------------------------

        "click_actions":
            action_types[
                "click"
            ],

        "type_text_actions":
            action_types[
                "type_text"
            ],

        "press_key_actions":
            action_types[
                "press_key"
            ],

        "hotkey_actions":
            action_types[
                "hotkey"
            ],

        "focus_window_actions":
            action_types[
                "focus_window"
            ],

        "launch_application_actions":
            action_types[
                "launch_application"
            ],

        "elapsed_seconds": round(
            elapsed,
            2,
        ),

        "runtime_error":
            runtime_error,
    }


# =========================================================
# SUMMARY
# =========================================================

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
            if result[
                "provider"
            ]
            == provider
        ]

        if not provider_results:
            continue

        passed = sum(
            result[
                "passed"
            ]
            for result
            in provider_results
        )

        total = len(
            provider_results
        )

        actions = sum(
            result[
                "action_count"
            ]
            for result
            in provider_results
        )

        clears = sum(
            result[
                "clear_actions"
            ]
            for result
            in provider_results
        )

        elapsed = sum(
            result[
                "elapsed_seconds"
            ]
            for result
            in provider_results
        )

        clicks = sum(
            result[
                "click_actions"
            ]
            for result
            in provider_results
        )

        type_texts = sum(
            result[
                "type_text_actions"
            ]
            for result
            in provider_results
        )

        press_keys = sum(
            result[
                "press_key_actions"
            ]
            for result
            in provider_results
        )

        hotkeys = sum(
            result[
                "hotkey_actions"
            ]
            for result
            in provider_results
        )

        focus_windows = sum(
            result[
                "focus_window_actions"
            ]
            for result
            in provider_results
        )

        launches = sum(
            result[
                "launch_application_actions"
            ]
            for result
            in provider_results
        )

        print(
            f"\n{provider.upper()}"
        )

        # -------------------------------------------------
        # Individual cases
        # -------------------------------------------------

        for result in (
            provider_results
        ):
            icon = (
                "✅"
                if result[
                    "passed"
                ]
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
                "    Expression: "
                f"{result['expression']!r}"
            )

            print(
                "    Expression complete: "
                f"{result['expression_complete']}"
            )

            print(
                "    Action mix: "
                f"click="
                f"{result['click_actions']}, "
                f"type_text="
                f"{result['type_text_actions']}, "
                f"press_key="
                f"{result['press_key_actions']}, "
                f"hotkey="
                f"{result['hotkey_actions']}, "
                f"focus="
                f"{result['focus_window_actions']}"
            )

            if result[
                "runtime_error"
            ]:
                print(
                    "    Runtime error: "
                    f"{result['runtime_error']}"
                )

        # -------------------------------------------------
        # Provider totals
        # -------------------------------------------------

        print()

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

        print(
            "Action mix:"
        )

        print(
            f"  Click: "
            f"{clicks}"
        )

        print(
            f"  Type text: "
            f"{type_texts}"
        )

        print(
            f"  Press key: "
            f"{press_keys}"
        )

        print(
            f"  Hotkey: "
            f"{hotkeys}"
        )

        print(
            f"  Focus window: "
            f"{focus_windows}"
        )

        print(
            f"  Launch application: "
            f"{launches}"
        )


# =========================================================
# SAVE RESULTS
# =========================================================

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
        / (
            "model_comparison_"
            f"{timestamp}.json"
        )
    )

    path.write_text(
        json.dumps(
            results,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"\nResults saved to: "
        f"{path}"
    )


# =========================================================
# MAIN
# =========================================================

def main():
    parser = (
        argparse.ArgumentParser()
    )

    parser.add_argument(
        "--smoke",
        action="store_true",
        help=(
            "Run one case per provider "
            "before the full benchmark."
        ),
    )

    args = (
        parser.parse_args()
    )

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