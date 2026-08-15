from .actions import validate_action

class ActionExecutor:
    def __init__(self, computer):
        self.computer = computer

    def execute(self, action: dict):
        action = validate_action(action)
        action_type = action.get("action")

        print(f"\nACTION: {action}")

        if action_type == "click":
            return self._click(action)

        if action_type == "type_text":
            return self._type_text(action)

        if action_type == "press_keys":
            return self._press_keys(action)

        if action_type == "focus_window":
            return self._focus_window(action)

        if action_type == "launch_application":
            return self._launch_application(action)

        if action_type == "finish":
            return {
                "status": "finished",
                "answer": action.get("answer"),
            }

        raise ValueError(
            f"Unknown action type: {action_type!r}"
        )

    def _click(self, action):
        target_id = action["target"]

        control = self.computer.resolve(
            target_id
        )

        self.computer.input.click(control)

        return {
            "status": "success",
            "action": "click",
            "target": target_id,
        }

    def _type_text(self, action):
        target_id = action["target"]

        control = self.computer.resolve(
            target_id
        )

        self.computer.input.type_text(
            control,
            action["text"],
            clear_first=action.get(
                "clear_first",
                False,
            ),
        )

        return {
            "status": "success",
            "action": "type_text",
        }

    def _press_keys(self, action):
        self.computer.input.press(
            action["keys"]
        )

        return {
            "status": "success",
            "action": "press_keys",
        }

    def _focus_window(self, action):
        target_id = action["target"]

        window = self.computer.resolve(
            target_id
        )

        window.set_focus()

        return {
            "status": "success",
            "action": "focus_window",
        }

    def _launch_application(self, action):
        executable = action["executable"]

        self.computer.applications.launch(
            executable
        )

        return {
            "status": "success",
            "action": "launch_application",
            "executable": executable,
        }