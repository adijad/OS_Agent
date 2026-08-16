VALID_ACTIONS = {
    "click",
    "type_text",
    "press_key",
    "hotkey",
    "focus_window",
    "open_application",
    "finish",
}


SPECIAL_KEYS = {
    "ENTER",
    "ESC",
    "TAB",
    "BACKSPACE",
    "DELETE",
    "SPACE",
    "LEFT",
    "RIGHT",
    "UP",
    "DOWN",
    "HOME",
    "END",
    "PAGEUP",
    "PAGEDOWN",
    "INSERT",
    "F1",
    "F2",
    "F3",
    "F4",
    "F5",
    "F6",
    "F7",
    "F8",
    "F9",
    "F10",
    "F11",
    "F12",
}


MODIFIER_KEYS = {
    "CTRL",
    "ALT",
    "SHIFT",
    "WIN",
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

    elif action_type == "press_key":
        _require(action, "key")
        _validate_press_key(
            action["key"]
        )

    elif action_type == "hotkey":
        _require(action, "keys")
        _validate_hotkey(
            action["keys"]
        )

    elif action_type == "open_application":
        _require(
            action,
            "application",
        )

    return action


def _require(
    action: dict,
    field: str,
):
    if (
        field not in action
        or action[field] is None
    ):
        raise InvalidActionError(
            f"Action "
            f"{action.get('action')!r} "
            f"requires field "
            f"{field!r}."
        )


def _validate_press_key(
    key: str,
):
    if not isinstance(key, str):
        raise InvalidActionError(
            "press_key requires "
            "a string key."
        )

    key = key.upper()

    if key not in SPECIAL_KEYS:
        raise InvalidActionError(
            f"Unsupported special key: "
            f"{key!r}"
        )


def _validate_hotkey(
    keys,
):
    if not isinstance(keys, list):
        raise InvalidActionError(
            "hotkey requires a list "
            "of keys."
        )

    if len(keys) < 2:
        raise InvalidActionError(
            "hotkey requires at least "
            "two keys."
        )

    normalized = []

    for key in keys:
        if not isinstance(key, str):
            raise InvalidActionError(
                "Every hotkey item "
                "must be a string."
            )

        normalized.append(
            key.upper()
        )

    modifiers = [
        key
        for key in normalized
        if key in MODIFIER_KEYS
    ]

    non_modifiers = [
        key
        for key in normalized
        if key not in MODIFIER_KEYS
    ]

    if not modifiers:
        raise InvalidActionError(
            "hotkey requires at least "
            "one modifier such as CTRL, "
            "ALT, SHIFT, or WIN."
        )

    if len(non_modifiers) != 1:
        raise InvalidActionError(
            "hotkey currently supports "
            "exactly one non-modifier key."
        )

    final_key = non_modifiers[0]

    if final_key in SPECIAL_KEYS:
        return

    if (
        len(final_key) == 1
        and final_key.isalnum()
    ):
        return

    raise InvalidActionError(
        f"Unsupported hotkey key: "
        f"{final_key!r}"
    )