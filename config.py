import os

from dotenv import load_dotenv


load_dotenv(
    override=True
)


class Settings:
    def __init__(self):
        self.model_provider = os.getenv(
            "OS_AGENT_PROVIDER",
            "anthropic",
        ).strip()

        self.anthropic_model = os.getenv(
            "ANTHROPIC_MODEL",
            "claude-sonnet-5",
        ).strip()

        self.openai_model = os.getenv(
            "OPENAI_MODEL",
            "gpt-5.6",
        ).strip()

        anthropic_key = os.getenv(
            "ANTHROPIC_API_KEY"
        )

        self.anthropic_api_key = (
            anthropic_key.strip()
            if anthropic_key
            else None
        )

        openai_key = os.getenv(
            "OPENAI_API_KEY"
        )

        self.openai_api_key = (
            openai_key.strip()
            if openai_key
            else None
        )


settings = Settings()