from time import sleep

from computer import Computer


def main():
    computer = Computer()

    expected = "Hello World from OS Agent"

    notepad = computer.applications.ensure(
        title_pattern=r".*Notepad.*",
        executable="notepad.exe",
    )

    editor = computer.controls.find(
        notepad,
        control_type="Document",
        name="Text editor",
    )

    computer.input.type_text(
        editor,
        expected,
        clear_first=True,
    )

    sleep(0.5)

    observed = computer.controls.read_text(editor)

    print(f"Expected: {expected!r}")
    print(f"Observed: {observed!r}")

    if observed.strip() == expected:
        print("✅ CHECKPOINT PASSED")
    else:
        print("❌ CHECKPOINT FAILED")


if __name__ == "__main__":
    main()