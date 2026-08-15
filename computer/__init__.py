from .applications import ApplicationManager
from .controls import ControlManager
from .input import InputManager


class Computer:
    def __init__(self):
        self.applications = ApplicationManager()
        self.controls = ControlManager()
        self.input = InputManager()