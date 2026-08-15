from .applications import ApplicationManager
from .controls import ControlManager
from .input import InputManager
from .observation import ObservationManager


class Computer:
    def __init__(self):
        self.applications = ApplicationManager()
        self.controls = ControlManager()
        self.input = InputManager()
        self.observation = ObservationManager()

    def observe(self):
        return self.observation.observe()

    def resolve(self, target_id: str):
        return self.observation.resolve(target_id)