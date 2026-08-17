import argparse

from agent.loop import AgentLoop
from computer import Computer
from observability import configure_telemetry


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--provider",
        choices=[
            "openai",
            "anthropic",
        ],
        default=None,
    )

    args = parser.parse_args()

    configure_telemetry()

    goal = input(
        "What would you like me to do?\n> "
    ).strip()

    if not goal:
        print("No goal provided.")
        return

    computer = Computer()

    agent = AgentLoop(
        computer,
        model_provider=args.provider,
        max_steps=20,
    )

    agent.run(goal)


if __name__ == "__main__":
    main()