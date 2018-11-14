#!/usr/bin/env python3
from time import sleep, time

from arbitrator import Arbitrator
from sensob import LineSensob, ProximitySensob, ColorSensob
from behaviour import CrashPreventionBehaviour, GoalBehaviour, LineBehaviour, ExploreBehaviour
from motob import Motob
from zumo_button import ZumoButton

class BBCON:
    def __init__(self, arbitrator):
        self.behaviours = []
        self.sensobs = []
        self.motobs = []
        self.arbitrator = arbitrator

    def add_behaviour(self, behaviour):
        behaviour.controller = self
        for sensob in behaviour.sensobs:
            self.add_sensob(sensob)
        self.behaviours.append(behaviour)

    def add_sensob(self, sensob, update=False):
        if sensob not in self.sensobs:
            self.sensobs.append(sensob)
            if update:
                sensob.update()

    def add_motob(self, motob):
        if motob not in self.motobs:
            self.motobs.append(motob)

    def run_one_timestep(self):
        for sensob in self.sensobs:
            sensob.update()
        for b in self.behaviours:
            b.update_activity()
        active = self._active_behaviours()
        for b in active:
            b.update()
        self.arbitrator.choose_action(active)
        if self.arbitrator.halt:
            for motob in self.motobs:
                motob.update(('s', None))
            return True
        for motob in self.motobs:
            print("Setting motob to {}".format(self.arbitrator.recommendation))
            motob.update(self.arbitrator.recommendation)
        sleep(0.5)
        for sensob in self.sensobs:
            sensob.reset()

    def activate(self, behaviour):
        for sensob in behaviour.sensobs:
            self.add_sensob(sensob, update=True)

    # Check if the deactivated behaviour is the last to use a sensob, and remove the sensob if it is
    def deactivate(self, behaviour):
        for sensob in behaviour.deactivated_sensobs:
            if sensob in self.sensobs and not any(sensob in b.sensobs for b in self._active_behaviours()):
                self.sensobs.remove(sensob)

    def _active_behaviours(self):
        return list(filter(lambda b: b.active, self.behaviours))


if __name__ == '__main__':
    arbitrator = Arbitrator()
    motob = Motob()
    bbcon = BBCON(arbitrator=arbitrator)
    bbcon.add_motob(motob)
    print("Start calibration")
    ZumoButton().wait_for_press()  # Start calibration after first button press
    line_sensob = LineSensob()
    #proximity_sensob = ProximitySensob()
    color_sensob = ColorSensob('green')
    #bbcon.add_behaviour(CrashPreventionBehaviour(proximity=proximity_sensob, priority=2))
    #bbcon.add_behaviour(GoalBehaviour(proximity=proximity_sensob, color=color_sensob, priority=5))
    bbcon.add_behaviour(LineBehaviour(line=line_sensob, priority=1))
    bbcon.add_behaviour(ExploreBehaviour(priority=0.25))
    while True:
        if bbcon.run_one_timestep():
            break
