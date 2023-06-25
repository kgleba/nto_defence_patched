from .controller import Controller
from exceptions import InvalidNumber

MAX_SENS = 5
MIN_SENS = 1


class Alarm(Controller):
    def __init__(self):
        super().__init__('Alarm')
        self.sensitivity = 3

    def set_sensitivity(self, sensitivity):
        sensitivity = int(sensitivity)
        if sensitivity < MIN_SENS or sensitivity > MAX_SENS:
            raise InvalidNumber
        self.sensitivity = sensitivity

    def get_sensitivity(self):
        return self.sensitivity
