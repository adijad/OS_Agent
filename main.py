import time

from agent.loop import AgentLoop
from computer import Computer


def main():
    goal = input(
        "What would you like me to do?\n> "
    ).strip()

    if not goal:
        print("No goal provided.")
        return

    computer = Computer()

    print("\nSwitch to Calculator.")
    print("The agent starts in 5 seconds...")

    time.sleep(5)

    agent = AgentLoop(
        computer,
        max_steps=15,
    )

    agent.run(goal)


if __name__ == "__main__":
    main()