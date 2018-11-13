from typing import List
from time import sleep

from behaviour import Behaviour
from arbitrator import Arbitrator
from sensob import LineSensob, ProximitySensob, ColorSensob
from behaviour import CrashPreventionBehaviour, GoalBehaviour, LineBehaviour, ExploreBehaviour
from zumo_button import ZumoButton

class BBCON:
    def __init__(self, arbitrator):
        self.behaviours: List[Behaviour] = []
        self.sensobs = []
        self.motobs = []
        self.arbitrator = arbitrator

    def add_behaviour(self, behaviour):
        self.behaviours.append(behaviour)

    # Handled by activate/deactivate
    # def add_sensob(self, sensob):
    #     self.sensobs.append(sensob)

    def run_one_timestep(self):
        for b in self.behaviours:
            b.update_activity()
        for sensob in self.sensobs:
            sensob.update()
        active = self._active_behaviours()
        for b in active:
            b.update()
        self.arbitrator.choose_action(active)
        if self.arbitrator.halt:
            for motob in self.motobs:
                motob.update(('s', None))
            return True
        for motob in self.motobs:
            motob.update(self.arbitrator.recommendation)
        sleep(0.5)
        for sensob in self.sensobs:
            sensob.reset()

    def activate(self, behaviour):
        for sensob in behaviour:
            if sensob not in self.sensobs:
                self.sensobs.append(sensob)

    # Check if the deactivated behaviour is the last to use a sensob, and remove the sensob if it is
    def deactivate(self, behaviour):
        for sensob in behaviour:
            if sensob in self.sensobs and not any(sensob in b.sensobs for b in self._active_behaviours()):
                self.sensobs.remove(sensob)

    def _active_behaviours(self):
        return list(filter(lambda b: b.active, self.behaviours))


if __name__ == '__main__':
    arbitrator = Arbitrator()
    bbcon = BBCON(arbitrator=arbitrator)
    ZumoButton().wait_for_press()  # Start calibration after first button press
    line_sensob = LineSensob()
    proximity_sensob = ProximitySensob()
    color_sensob = ColorSensob('green')
    bbcon.add_behaviour(CrashPreventionBehaviour(proximity=proximity_sensob))
    bbcon.add_behaviour(GoalBehaviour(proximity=proximity_sensob, color=color_sensob))
    bbcon.add_behaviour(LineBehaviour(line=line_sensob))
    bbcon.add_behaviour(ExploreBehaviour())
    ZumoButton().wait_for_press()  # Start acting after second button press
    while True:
        if bbcon.run_one_timestep():
            break
