import base64
import json
from pathlib import Path

from anthropic import Anthropic

from config import settings
from .base import ModelProvider
from .shared import (
    ACTION_DESCRIPTION,
    ACTION_INPUT_SCHEMA,
    SYSTEM_PROMPT,
)

from .result import (
    ModelCallResult,
    ModelUsage,
)

ACTION_TOOL = {
    "name": "computer_action",
    "description": ACTION_DESCRIPTION,
    "input_schema": ACTION_INPUT_SCHEMA,
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

        self.model = settings.anthropic_model

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

        usage = response.usage

        input_tokens = (
            getattr(
                usage,
                "input_tokens",
                0,
            )
            or 0
        )

        output_tokens = (
            getattr(
                usage,
                "output_tokens",
                0,
            )
            or 0
        )

        cached_input_tokens = (
            getattr(
                usage,
                "cache_read_input_tokens",
                0,
            )
            or 0
        )

        cache_creation_input_tokens = (
            getattr(
                usage,
                "cache_creation_input_tokens",
                0,
            )
            or 0
        )

        model_usage = ModelUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,

            total_tokens=(
                input_tokens
                + output_tokens
                + cached_input_tokens
                + cache_creation_input_tokens
            ),

            cached_input_tokens=(
                cached_input_tokens
            ),

            cache_creation_input_tokens=(
                cache_creation_input_tokens
            ),
        )

        for block in response.content:
            if (
                block.type == "tool_use"
                and block.name == "computer_action"
            ):
                return ModelCallResult(
                    action=block.input,
                    provider="anthropic",
                    model=response.model,
                    usage=model_usage
                )

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