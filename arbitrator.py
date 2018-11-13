class Arbitrator:
    def __init__(self):
        self.halt = False
        self.recommendation = None

    def choose_action(self, behaviours):
        if not behaviours:
            self.recommendation = None
            return
        if any(b.halt_request for b in behaviours):
            self.halt = True
        self.recommendation = max(behaviours, key=lambda b: b.weight).motor_recommendation
