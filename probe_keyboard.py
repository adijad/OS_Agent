import time

from agent.executor import (
    ActionExecutor,
)
from computer import Computer


def main():
    computer = Computer()
    executor = ActionExecutor(
        computer
    )

    print(
        "Switch to Calculator."
    )
    print(
        "Starting in 5 seconds..."
    )

    time.sleep(5)

    # Clear using semantic UI
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
            "Could not find Clear."
        )

    executor.execute(
        {
            "action": "click",
            "target":
                clear_control["id"],
        }
    )

    time.sleep(0.5)

    # Fresh snapshot because target IDs
    # are snapshot-scoped.
    observation = (
        computer.observe()
    )

    active_window = (
        observation[
            "active_window"
        ]
    )

    executor.execute(
        {
            "action": "type_text",
            "target":
                active_window["id"],
            "text": "24+83",
        }
    )

    time.sleep(0.5)

    executor.execute(
        {
            "action": "press_key",
            "key": "ENTER",
        }
    )

    time.sleep(0.5)

    final_state = (
        computer.observe()
    )

    for control in final_state[
        "controls"
    ]:
        name = control.get(
            "name",
            "",
        )

        if name.startswith(
            "Display is "
        ):
            print(
                f"\nFINAL: {name}"
            )


if __name__ == "__main__":
    main()