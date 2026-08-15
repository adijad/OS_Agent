import json
import time

from computer import Computer


def main():
    computer = Computer()

    print("Switch to the window you want me to observe...")
    print("Capturing in 5 seconds...")

    time.sleep(5)

    semantic = computer.observe()

    screenshot = computer.screenshot()

    print("\n=== SEMANTIC OBSERVATION ===")

    print(
        json.dumps(
            semantic,
            indent=2,
            ensure_ascii=False,
        )
    )

    print("\n=== VISUAL OBSERVATION ===")

    print(
        json.dumps(
            screenshot,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()