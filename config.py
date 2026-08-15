import os

from dotenv import load_dotenv


load_dotenv(override=True)


class Settings:
    def __init__(self):
        self.model_provider = os.getenv(
            "OS_AGENT_PROVIDER",
            "anthropic",
        ).strip()

        self.model_name = os.getenv(
            "OS_AGENT_MODEL",
            "claude-sonnet-4-20250514",
        ).strip()

        anthropic_key = os.getenv(
            "ANTHROPIC_API_KEY"
        )

        self.anthropic_api_key = (
            anthropic_key.strip()
            if anthropic_key
            else None
        )

        self.openai_api_key = os.getenv(
            "OPENAI_API_KEY"
        )

        self.gemini_api_key = os.getenv(
            "GEMINI_API_KEY"
        )


settings = Settings()