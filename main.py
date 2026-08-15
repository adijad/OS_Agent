import json
import time

from computer import Computer


def main():
    computer = Computer()

    print("Switch to the window you want me to observe...")
    print("Observing in 5 seconds...")

    time.sleep(5)

    observation = computer.observe()

    print(
        json.dumps(
            observation,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()