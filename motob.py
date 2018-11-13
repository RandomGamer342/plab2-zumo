from motors import Motors


class Motob:
    def __init__(self):
        self.motors = Motors()
        self.value = None

    def update(self, v):
        self.value = v
        self.operationalize()

    def operationalize(self):
        t = self.value[0]
        if t in ('l', 'r'):
            self.traverse()
        elif t in ('lf', 'rf', 'lb', 'rb'):
            self.turn()
        elif t in ('f', 'b'):
            self.drive()
        elif t == 's':
            self.motors.stop()
        else:
            raise ValueError("Command type invalid. {}".format(self.value))

    def traverse(self):
        dur = self.value[1] / 90 if self.value[1] else None
        if self.value[0].lower() == 'r':
            self.motors.right(0.4, dur)
        else:  # l
            self.motors.left(0.4, dur)

    def turn(self):
        t = self.value[0].lower()
        s = self.value[1]
        if t[1] == 'b':
            s = -s
        if t[0] == 'l':
            self.motors.set_value((s/5, s), 0.5)
        else:  # r
            self.motors.set_value((s, s/5), 0.5)

    def drive(self):
        t = self.value[0]
        s = self.value[1]
        if t == 'b':
            self.motors.backward(s, 0.5)
        else:
            self.motors.forward(s, 0.5)
