import base64
import json
from pathlib import Path

from openai import OpenAI

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


class OpenAIProvider(ModelProvider):
    def __init__(self):
        if not settings.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is missing."
            )

        self.client = OpenAI(
            api_key=settings.openai_api_key
        )

        self.model = (
            settings.openai_model
        )

    def choose_action(
        self,
        *,
        goal: str,
        state: dict,
        history: list[dict],
    ) -> dict:
        semantic = state[
            "semantic"
        ]

        screenshot_path = Path(
            state["visual"]["path"]
        )

        encoded = base64.b64encode(
            screenshot_path.read_bytes()
        ).decode("utf-8")

        image_data_url = (
            "data:image/png;base64,"
            + encoded
        )

        prompt = self._build_prompt(
            goal=goal,
            semantic=semantic,
            history=history,
        )

        response = (
            self.client.responses.create(
                model=self.model,
                instructions=SYSTEM_PROMPT,
                input=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "input_image",
                                "image_url": image_data_url,
                                "detail": "auto",
                            },
                            {
                                "type": "input_text",
                                "text": prompt,
                            },
                        ],
                    }
                ],
                tools=[
                    {
                        "type": "function",
                        "name": "computer_action",
                        "description":
                            ACTION_DESCRIPTION,
                        "parameters":
                            ACTION_INPUT_SCHEMA,
                        "strict": True,
                    }
                ],
                tool_choice={
                    "type": "function",
                    "name": "computer_action",
                },
            )
        )

        usage = response.usage
        input_details = getattr(
            usage,
            "input_tokens_details",
            None,
        )

        output_details = getattr(
            usage,
            "output_tokens_details",
            None,
        )

        model_usage = ModelUsage(
            input_tokens=(
                getattr(
                    usage,
                    "input_tokens",
                    0,
                )
                or 0
            ),

            output_tokens=(
                getattr(
                    usage,
                    "output_tokens",
                    0,
                )
                or 0
            ),

            total_tokens=(
                getattr(
                    usage,
                    "total_tokens",
                    0,
                )
                or 0
            ),

            cached_input_tokens=(
                getattr(
                    input_details,
                    "cached_tokens",
                    0,
                )
                or 0
            ),

            reasoning_tokens=(
                getattr(
                    output_details,
                    "reasoning_tokens",
                    0,
                )
                or 0
            ),
        )

        for item in response.output:
            if (
                item.type == "function_call"
                and item.name
                == "computer_action"
            ):
                return ModelCallResult(
                    action=json.loads(
                        item.arguments
                    ),
                    provider="openai",
                    model=response.model,
                    usage=model_usage
                )

        raise RuntimeError(
            "OpenAI did not return "
            "a computer action."
        )

    def _build_prompt(
        self,
        *,
        goal: str,
        semantic: dict,
        history: list[dict],
    ) -> str:
        recent_history = (
            history[-10:]
        )

        return (
            f"USER GOAL:\n{goal}\n\n"
            "CURRENT SEMANTIC COMPUTER STATE:\n"
            f"{json.dumps(semantic, indent=2)}\n\n"
            "RECENT ACTION HISTORY:\n"
            f"{json.dumps(recent_history, indent=2)}"
        )