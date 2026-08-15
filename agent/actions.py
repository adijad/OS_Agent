VALID_ACTIONS = {
    "click",
    "type_text",
    "press_keys",
    "focus_window",
    "launch_application",
    "finish",
}


class InvalidActionError(Exception):
    pass


def validate_action(action: dict):
    if not isinstance(action, dict):
        raise InvalidActionError(
            "Action must be a dictionary."
        )

    action_type = action.get("action")

    if action_type not in VALID_ACTIONS:
        raise InvalidActionError(
            f"Unsupported action: {action_type!r}"
        )

    if action_type in {
        "click",
        "focus_window",
    }:
        _require(action, "target")

    elif action_type == "type_text":
        _require(action, "target")
        _require(action, "text")

    elif action_type == "press_keys":
        _require(action, "keys")

    elif action_type == "launch_application":
        _require(action, "executable")

    return action


def _require(action: dict, field: str):
    if field not in action:
        raise InvalidActionError(
            f"Action {action.get('action')!r} "
            f"requires field {field!r}."
        )