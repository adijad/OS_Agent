from config import settings

from .anthropic import AnthropicProvider


def create_model_provider():
    provider = settings.model_provider.lower()

    if provider == "anthropic":
        return AnthropicProvider()

    raise ValueError(
        f"Unsupported model provider: {provider!r}"
    )