#!/usr/bin/env python3
from PIL import Image
from io import BytesIO
import shlex
import subprocess


class Camera():
    def __init__(self, img_width=128, img_height=96, img_rot=0):
        self.value = None
        self.img_width = img_width
        self.img_height = img_height
        self.img_rot = img_rot

    def get_value(self):
        if not self.value:
            return self.update()
        return self.value

    def update(self):
        self.sensor_get_value()
        return self.value

    def reset(self):
        self.value = None

    def sensor_get_value(self):
        # use raspicam to take an image, with JPG output stored as bytes
        image = subprocess.Popen(
            shlex.split("raspistill -t 1 -o - ") + list(map(str,[
                "-w", self.img_width,
                "-h", self.img_height,
                "-rot", self.img_rot,
            ])),
            stdout=subprocess.PIPE,
        ).communicate()[0]
        
        # Open the image just taken by raspicam
        self.value = Image.open(BytesIO(image)).convert('RGB')
    
    def show(self): # debug
        self.get_value().show() # fim, vx or imagemagic must be installed. x forwarding preferred

if __name__ == "__main__":
    c = Camera().update().show()
