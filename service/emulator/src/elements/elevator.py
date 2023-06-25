from .controller import Controller
from exceptions import InvalidNumber
import random

MIN_FLOOR = 1
MAX_FLOOR = 6


class Elevator(Controller):
    def __init__(self):
        super().__init__('Elevator')
        self.__set_random_floor()

    def __set_random_floor(self):
        if self.enabled:
            self.floor = random.randint(MIN_FLOOR, MAX_FLOOR)

    def set_floor(self, floor):
        floor = int(floor)
        if floor < MIN_FLOOR or floor > MAX_FLOOR:
            raise InvalidNumber
        if self.enabled:
            self.floor = floor

    def get_floor(self):
        self.__set_random_floor()
        return self.floor
