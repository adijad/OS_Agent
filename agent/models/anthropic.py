import base64
import json
from pathlib import Path

from anthropic import Anthropic

from config import settings
from .base import ModelProvider


SYSTEM_PROMPT = """
You are the reasoning component of an OS-level computer agent.

You receive:

1. A user goal.
2. A semantic representation of the current Windows state.
3. A screenshot of the active window.
4. A short history of previous actions.

Your responsibility is to propose exactly ONE next action.

Important behavior:

- Base your action only on the currently observed state.
- Never invent target IDs.
- Target IDs come from the semantic observation.
- Target IDs are temporary and only valid for the current observation.
- After every action, the computer will be observed again.
- Do not assume an action succeeded until a later observation confirms it.
- Prefer visible semantic controls when appropriate.
- For this initial experiment, prefer clicking visible Calculator
  controls rather than using keyboard shortcuts.
- If the goal has already been achieved, use finish.
- Do not perform unnecessary actions after success.

Provide only a short action rationale.
Do not provide a long reasoning trace.
"""


ACTION_TOOL = {
    "name": "computer_action",
    "description": (
        "Propose exactly one action for OS Agent to perform "
        "on the currently observed Windows state. The action "
        "must be grounded in the supplied semantic controls. "
        "Use finish when the user's requested goal has already "
        "been achieved."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "reason": {
                "type": "string",
                "description": (
                    "A short explanation of why this is "
                    "the appropriate next action."
                ),
            },
            "action": {
                "type": "string",
                "enum": [
                    "click",
                    "type_text",
                    "press_keys",
                    "focus_window",
                    "launch_application",
                    "finish",
                ],
            },
            "target": {
                "type": "string",
                "description": (
                    "Current semantic target ID when "
                    "the chosen action requires one."
                ),
            },
            "text": {
                "type": "string",
                "description": (
                    "Text to enter for type_text."
                ),
            },
            "keys": {
                "type": "string",
                "description": (
                    "Keyboard keys for press_keys."
                ),
            },
            "executable": {
                "type": "string",
                "description": (
                    "Executable name for "
                    "launch_application."
                ),
            },
            "answer": {
                "type": "string",
                "description": (
                    "Final answer to return when "
                    "the action is finish."
                ),
            },
        },
        "required": [
            "reason",
            "action",
        ],
    },
}


class AnthropicProvider(ModelProvider):
    def __init__(self):
        if not settings.anthropic_api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is missing."
            )

        self.client = Anthropic(
            api_key=settings.anthropic_api_key
        )

        self.model = settings.model_name

    def choose_action(
        self,
        *,
        goal: str,
        state: dict,
        history: list[dict],
    ) -> dict:
        semantic = state["semantic"]

        screenshot_path = Path(
            state["visual"]["path"]
        )

        screenshot_data = base64.b64encode(
            screenshot_path.read_bytes()
        ).decode("utf-8")

        prompt = self._build_prompt(
            goal=goal,
            semantic=semantic,
            history=history,
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": screenshot_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt,
                        },
                    ],
                }
            ],
            tools=[ACTION_TOOL],
            tool_choice={
                "type": "tool",
                "name": "computer_action",
            },
        )

        for block in response.content:
            if (
                block.type == "tool_use"
                and block.name == "computer_action"
            ):
                return block.input

        raise RuntimeError(
            "Claude did not return a computer action."
        )

    def _build_prompt(
        self,
        *,
        goal: str,
        semantic: dict,
        history: list[dict],
    ) -> str:
        recent_history = history[-10:]

        return (
            f"USER GOAL:\n{goal}\n\n"
            "CURRENT SEMANTIC COMPUTER STATE:\n"
            f"{json.dumps(semantic, indent=2)}\n\n"
            "RECENT ACTION HISTORY:\n"
            f"{json.dumps(recent_history, indent=2)}"
        )