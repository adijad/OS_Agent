from time import sleep

from pywinauto import Desktop
from pywinauto.application import Application
from pywinauto.keyboard import send_keys


def launch_notepad():
    print("=== APPLICATION LIFECYCLE ===")

    desktop = Desktop(backend="uia")

    # First check whether Notepad already exists.
    existing_notepad = desktop.window(
        title_re=r".*Notepad.*"
    )

    if existing_notepad.exists(timeout=1):
        print("Notepad is already running.")

        try:
            existing_notepad.restore()
        except Exception:
            pass

        existing_notepad.set_focus()

        return existing_notepad

    print("Notepad is not running.")
    print("Launching Notepad...")

    Application(
        backend="uia"
    ).start("notepad.exe")

    # Now rediscover it through the desktop.
    notepad = desktop.window(
        title_re=r".*Notepad.*"
    )

    print("Waiting for Notepad to become ready...")

    notepad.wait(
        "exists visible enabled ready",
        timeout=10,
    )

    notepad.set_focus()

    print("Notepad is ready.")

    return notepad


def get_editor(notepad):
    print("\n=== FINDING EDITOR ===")

    documents = notepad.descendants(
        control_type="Document"
    )

    if not documents:
        raise RuntimeError(
            "Could not find a Document control in Notepad."
        )

    editor = documents[0]

    print(f"Name         : {editor.element_info.name!r}")
    print(f"Control type : {editor.element_info.control_type}")
    print(f"Class name   : {editor.element_info.class_name!r}")

    return editor


def write_text(editor, text):
    print("\n=== WRITING ===")

    editor.set_focus()

    sleep(0.5)

    # Start with a clean document for this experiment.
    send_keys("^a")
    send_keys("{BACKSPACE}")

    send_keys(
        text,
        with_spaces=True,
        pause=0.05,
    )

    print(f"Wrote: {text!r}")


def read_text(editor):
    print("\n=== READING THROUGH UI AUTOMATION ===")

    text_pattern = editor.iface_text

    document_range = text_pattern.DocumentRange

    text = document_range.GetText(-1)

    print(f"Observed: {text!r}")

    return text


def verify(expected, observed):
    print("\n=== CHECKPOINT ===")

    if observed.strip() == expected:
        print("✅ CHECKPOINT PASSED")
        return True

    print("❌ CHECKPOINT FAILED")
    print(f"Expected: {expected!r}")
    print(f"Observed: {observed!r}")

    return False


def main():
    text = "Hello World"

    notepad = launch_notepad()

    editor = get_editor(notepad)

    write_text(editor, text)

    sleep(1)

    observed = read_text(editor)

    verify(text, observed)


if __name__ == "__main__":
    main()