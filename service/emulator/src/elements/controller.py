from .base_element import BaseElement


class Controller(BaseElement):
    def __init__(self, type_, enabled=True):
        super().__init__(type_)
        self.enabled = enabled

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def get_enabled(self):
        return self.enabled
