from abc import ABC, abstractmethod


class ModelProvider(ABC):
    @abstractmethod
    def choose_action(
        self,
        *,
        goal: str,
        state: dict,
        history: list[dict],
    ) -> dict:
        """
        Return exactly one proposed OS Agent action.
        """
        raise NotImplementedError