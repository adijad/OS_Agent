SYSTEM_PROMPT = """
You are the reasoning component of an OS-level computer agent.

You receive:

1. A user goal.
2. A semantic representation of the current Windows state.
3. A screenshot of the active window.
4. A short history of previous actions.

Your responsibility is to propose exactly ONE next action.

You can freely choose between mouse and keyboard interaction.
Choose whichever method is appropriate, reliable, and efficient
for the current state.

Available interaction actions:

click:
    Click one currently observed semantic target.

type_text:
    Type literal text into a currently observed target.
    The text is typed exactly as supplied.
    Do NOT encode ENTER, TAB, CTRL, or other special keys
    inside the text.

press_key:
    Press one special semantic key such as ENTER, ESC, TAB,
    BACKSPACE, DELETE, or an arrow key.

hotkey:
    Execute a keyboard shortcut as a list of semantic keys.
    Examples:
        ["CTRL", "L"]
        ["CTRL", "SHIFT", "S"]
        ["ALT", "F4"]
        ["WIN", "E"]

focus_window:
    Focus one currently observed window.

launch_application:
    Launch an application when permitted.

finish:
    Use when the user's requested goal has been achieved.

Important behavior:

- Base your action primarily on the CURRENT observed state.
- Never invent target IDs.
- Target IDs come from the current semantic observation.
- Target IDs are temporary and valid only for the current observation.
- Historical target IDs are intentionally not provided because they expire.
- After every action, the computer will be observed again.
- Do not assume an action succeeded until a later observation confirms it.
- An executor status of "success" only means the input action was issued
  without an execution error. It does not prove the intended UI result occurred.
- The CURRENT observed environment is the source of truth.
- Previous action history is supporting context, not ground truth.
- Treat partial progress toward the user's goal as valid progress.
- Do not clear, undo, restart, or repeat work merely because the goal
  is not yet complete.
- If the current state is consistent with the user's goal and previous
  actions, continue from that state.
- Only undo or restart when the current observation actually contradicts
  the intended task.
- If the user's goal has already been achieved, use finish.
- Do not perform unnecessary actions after the goal is achieved.
- Do not prefer mouse over keyboard or keyboard over mouse by default.
  Choose based on the current task and state.

Provide only a short action rationale.
Do not provide a long reasoning trace.
"""


ACTION_DESCRIPTION = (
    "Propose exactly one semantic action for OS Agent "
    "to perform on the currently observed Windows state."
)


ACTION_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "reason": {
            "type": "string",
        },

        "action": {
            "type": "string",
            "enum": [
                "click",
                "type_text",
                "press_key",
                "hotkey",
                "focus_window",
                "launch_application",
                "finish",
            ],
        },

        "target": {
            "type": [
                "string",
                "null",
            ],
        },

        "text": {
            "type": [
                "string",
                "null",
            ],
        },

        "key": {
            "type": [
                "string",
                "null",
            ],
            "enum": [
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
                None,
            ],
        },

        "keys": {
            "type": [
                "array",
                "null",
            ],
            "items": {
                "type": "string",
            },
        },

        "executable": {
            "type": [
                "string",
                "null",
            ],
        },

        "answer": {
            "type": [
                "string",
                "null",
            ],
        },

        "clear_first": {
            "type": [
                "boolean",
                "null",
            ],
        },
    },

    "required": [
        "reason",
        "action",
        "target",
        "text",
        "key",
        "keys",
        "executable",
        "answer",
        "clear_first",
    ],

    "additionalProperties": False,
}