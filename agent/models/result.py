from dataclasses import dataclass


@dataclass(
    frozen=True
)
class ModelUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    cached_input_tokens: int = 0
    cache_creation_input_tokens: int = 0
    reasoning_tokens: int = 0


@dataclass(
    frozen=True
)
class ModelCallResult:
    action: dict
    provider: str
    model: str
    usage: ModelUsage