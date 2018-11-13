from reflectance_sensors import ReflectanceSensors
from camera import Camera
from imager2 import Imager
from ultrasonic import Ultrasonic


class Sensob:
    def __init__(self, sensor):
        self.sensor = sensor  # No usecase for multiple sensors

    def update(self):
        if self.sensor.get_value() is None:
            self.sensor.update()
        return self.get_value()

    def get_value(self):
        return self.sensor.get_value()

    def reset(self):
        self.sensor.reset()


class LineSensob(Sensob):
    def __init__(self):
        super(LineSensob, self).__init__(ReflectanceSensors(auto_calibrate=True))
        self.sensor_count = 6

    def update(self):
        if self.sensor.get_value() == [-1.0] * self.sensor_count:
            self.sensor.update()
        return self.get_value()

    # Return a tuple representing at which sensor the line starts/ends
    def get_value(self):
        min_, max_ = None, None
        val = self.sensor.get_value()
        for i, v in enumerate(val):
            print(v)
            if min_ is None:
                if v <= 0.5:
                    min_ = i
            else:
                if v >= 0.5:
                    break
                max_ = i
        if min_ is not None and max_ is None:
            max_ = self.sensor_count - 1
        return min_, max_


class ColorSensob(Sensob):
    def __init__(self, color):
        super(ColorSensob, self).__init__(Camera())
        self.imager = Imager()
        self.color = None
        self.set_color(color)

    def set_color(self, color):
        try:
            self.color = Imager().get_color_rgb(color)
        except KeyError as ex:
            raise ValueError("Invalid color name") from ex

    def get_value(self):
        # TODO: Support white/black
        imager = Imager(image=self.sensor.get_value()).map_color_wta()
        left = 0
        middle = 0
        right = 0
        for x in range(int(imager.xmax * 0.4)):
            for y in range(imager.ymax):
                if imager.get_pixel(x, y) == self.color:
                    left += 1
        for x in range(int(imager.xmax * 0.4), int(imager.xmax * 0.6)):
            for y in range(imager.ymax):
                if imager.get_pixel(x, y) == self.color:
                    middle += 1
        for x in range(int(imager.xmax * 0.6), imager.xmax):
            for y in range(imager.ymax):
                if imager.get_pixel(x, y) == self.color:
                    right += 1
        left /= (imager.xmax * imager.ymax) * 0.4  # Normalize
        middle /= (imager.xmax * imager.ymax) * 0.2  # Normalize
        right /= (imager.xmax * imager.ymax) * 0.4  # Normalize
        return left, middle, right


class ProximitySensob(Sensob):
    def __init__(self):
        super(ProximitySensob, self).__init__(Ultrasonic())
