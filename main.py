import time

from agent.executor import ActionExecutor
from computer import Computer


def find_control(observation, name):
    for control in observation["controls"]:
        if control["name"] == name:
            return control

    raise RuntimeError(
        f"Could not find control: {name!r}"
    )


def main():
    computer = Computer()
    executor = ActionExecutor(computer)

    print("Switch to Calculator...")
    print("Starting in 5 seconds...")

    time.sleep(5)

    sequence = [
        "Nine",
        "One",
        "Three",
        "Multiply by",
        "Four",
        "Seven",
        "Equals",
    ]

    for control_name in sequence:
        # IMPORTANT:
        # Observe again before every action.
        observation = computer.observe()

        target = find_control(
            observation,
            control_name,
        )

        print(
            f"\nFound {control_name!r}"
            f" -> {target['id']}"
        )

        executor.execute(
            {
                "action": "click",
                "target": target["id"],
            }
        )

        time.sleep(0.3)

    # Observe final result.
    final_observation = computer.observe()

    print("\n=== FINAL STATE ===")

    for control in final_observation["controls"]:
        name = control["name"]

        if name.startswith("Display is"):
            print(name)


if __name__ == "__main__":
    main()