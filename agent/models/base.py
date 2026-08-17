from abc import ABC, abstractmethod
from .result import ModelCallResult


class ModelProvider(ABC):
    @abstractmethod
    def choose_action(
        self,
        *,
        goal: str,
        state: dict,
        history: list[dict],
    ) -> ModelCallResult:
        """
        Return exactly one proposed OS Agent action.
        """
        raise NotImplementedError