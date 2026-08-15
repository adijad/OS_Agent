from config import settings

from .anthropic import AnthropicProvider
from .openai import OpenAIProvider


def create_model_provider(
    provider: str | None = None,
):
    provider_name = (
        provider
        or settings.model_provider
    ).lower()

    if provider_name == "anthropic":
        return AnthropicProvider()

    if provider_name == "openai":
        return OpenAIProvider()

    raise ValueError(
        "Unsupported model provider: "
        f"{provider_name!r}"
    )