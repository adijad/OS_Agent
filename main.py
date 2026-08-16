from agent.loop import AgentLoop
from computer import Computer


def main():
    goal = input(
        "What would you like me to do?\n> "
    ).strip()

    if not goal:
        print(
            "No goal provided."
        )
        return

    computer = Computer()

    agent = AgentLoop(
        computer,
        max_steps=20,
    )

    agent.run(
        goal
    )


if __name__ == "__main__":
    main()