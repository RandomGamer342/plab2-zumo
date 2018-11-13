from random import choice, randint
import time

from bbcon import BBCON


class Behaviour:
    def __init__(self, priority):
        self.controller = None
        self.sensobs = []
        self.deactivated_sensobs = []
        self.motor_recommendation = None
        self.active = False
        self.halt_request = False
        self.priority = priority
        self.match_degree = None
        self.weight = None

    # Split out of update to let activities activate in the same time unit
    def update_activity(self):
        if not self.active:
            self.consider_activation()
        else:
            self.consider_deactivation()

    def update(self):
        self.sense_and_act()
        self.weight = self.match_degree * self.priority

    def consider_activation(self):
        raise NotImplementedError()

    def consider_deactivation(self):
        raise NotImplementedError()

    def sense_and_act(self):
        raise NotImplementedError()


class CrashPreventionBehaviour(Behaviour):
    def __init__(self, proximity, *args, **kwargs):
        super(CrashPreventionBehaviour, self).__init__(*args, **kwargs)
        self.deactivated_sensobs.append(proximity)
        self.far = 30
        self.close = 10

    def consider_activation(self):
        self.active = True
        self.sensobs.append(self.deactivated_sensobs.pop())
        self.controller.activate(self)

    # The behaviour itself is never going to want to allow collisions by disabling itself
    def consider_deactivation(self):
        pass

    # Assume single, forward facing sensob
    def sense_and_act(self):
        dist = self.sensobs[0].get_value()
        if dist < self.close:
            self.match_degree = 1.
        elif dist > self.far:
            self.match_degree = 0.
        else:
            self.match_degree = (self.far - dist) / self.far * 2
        self.motor_recommendation = (choice('l', 'r'), 90)


class GoalBehaviour(Behaviour):
    def __init__(self, proximity, color, *args, **kwargs):
        super(GoalBehaviour, self).__init__(*args, **kwargs)
        self.sensobs.append(proximity)
        self.deactivated_sensobs.append(color)
        self.trigger = 10
        self.goal = 2
        self.threshold = 0.2
        self.goal_threshold = 0.9

    # Keep proximity sensor active, but save time by disabling the camera
    def consider_activation(self):
        if self.sensobs[0].get_value() < self.trigger:
            self.active = True
            self.sensobs.append(self.deactivated_sensobs.pop())
            self.controller.activate(self)

    def consider_deactivation(self):
        if self.sensobs[0].get_value() > self.trigger:
            self.active = False
            self.deactivated_sensobs.append(self.sensobs.pop())
            self.controller.deactivate(self)

    def sense_and_act(self):
        dist = self.sensobs[0].get_value()
        match = self.sensobs[1].get_value()
        if max(match) < self.threshold:
            self.match_degree = 0
        elif dist <= self.goal and match[1] >= self.goal_threshold:
            self.halt_request = True
        elif match[0] - match[1] > 0.05:
            self.match_degree = match[0]
            self.motor_recommendation = ('l', 10 * (dist / self.trigger))
        elif match[2] - match[1] > 0.05:
            self.match_degree = match[2]
            self.motor_recommendation = ('r', 10 * (dist / self.trigger))
        else:
            self.match_degree = match[1]
            self.motor_recommendation = ('f', 0.5 - (dist / self.trigger) / 4)


class LineBehaviour(Behaviour):
    def __init__(self, line, *args, **kwargs):
        super(LineBehaviour, self).__init__(*args, **kwargs)
        self.deactivated_sensobs.append(line)
        self.followed_time = 0

    def consider_activation(self):
        self.active = True
        self.sensobs.append(self.deactivated_sensobs.pop())
        self.controller.activate(self)

    # No reason to turn this off
    def consider_deactivation(self):
        pass

    def sense_and_act(self):
        vals = self.sensobs[0].get_value()
        if vals is not None:
            min_ = vals[0]
            max_ = vals[1]
            max_diff = self.sensobs[0].sensor_count - 1 - max_
            self.match_degree = 1
            if self.followed_time and self.followed_time - time.time() > 15:  # Avoid circles/loops
                if min_ > max_diff:
                    self.motor_recommendation = ('lf', 0.6)
                else:
                    self.motor_recommendation = ('rf', 0.6)
            else:
                if not self.followed_time:
                    self.followed_time = time.time()
                if min_ == 0 and max_ == 6:
                    self.motor_recommendation = (choice('r', 'l'), 90)
                elif min_ > max_diff:
                    self.motor_recommendation = ('l', 5 * (max_diff - min_))
                elif max_diff > min_:
                    self.motor_recommendation = ('r', 5 * (min_ - max_diff))
                else:
                    self.motor_recommendation = ('f', 0.3)
        else:
            self.match_degree = 0
            self.followed_time = 0


class ExploreBehaviour(Behaviour):
    def __init__(self, *args, **kwargs):
        super(ExploreBehaviour, self).__init__(*args, **kwargs)
        self.match_degree = 1

    def consider_activation(self):
        self.active = True
        self.controller.activate()

    # This has no sensors. No reason to disable.
    def consider_deactivation(self):
        pass

    def sense_and_act(self):
        actions = ((choice('l', 'r'), randint(1, 90)), (choice('lf', 'lr', 'bf', 'br'), 0.5), (choice('f', 'b'), 0.5))
        self.motor_recommendation = choice(actions)
