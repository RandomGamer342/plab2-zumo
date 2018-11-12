from typing import Tuple
from bbcon import BBCON


class Behaviour:
    def __init__(self, priority):
        self.controller = None
        self.sensors = []
        self.deactivated_sensors = []
        self.motor_recommendation = None
        self.active = False
        self.halt_request = False
        self.priority = priority
        self.match_degree = None
        self.weight = None

    def update(self):
        if not self.active:
            self.consider_activation()
        else:
            self.consider_deactivation()
        if self.active:
            self.sense_and_act()
            self.weight = self.match_degree * self.priority

    def consider_activation(self):
        raise NotImplementedError()

    def consider_deactivation(self):
        raise NotImplementedError()

    def sense_and_act(self):
        raise NotImplementedError()


