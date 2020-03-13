from machine import Pin
from encoder import Encoder


class Compass:

    def __init__(self, enc, north, east, south, west):

        self.max_val = 48

        self.enc = Encoder(*enc, min_val=0, max_val=self.max_val)

        self.leds = [
            Pin(north, Pin.OUT),
            Pin(east, Pin.OUT),
            Pin(south, Pin.OUT),
            Pin(west, Pin.OUT)
        ]

        for led in self.leds:
            led.value(0)

        self.direction = 0
        self.last_val = 0

        self.setDirection(self.direction)

    def checkDirection(self):
        val = self.enc.value
        if(val != self.last_val):
            if val >= 0 and val <= 12:
                # North
                if(self.direction != 0):
                    self.setDirection(0)
            elif val >= 13 and val <= 24:
                # East
                if(self.direction != 1):
                    self.setDirection(1)
            elif val >= 25 and val <= 36:
                # South
                if(self.direction != 2):
                    self.setDirection(2)
            elif val >= 37 and val <= 48:
                # West
                if(self.direction != 3):
                    self.setDirection(3)

            # Check max value, set last value and reset if needed
            if val == self.max_val:
                self.enc.reset()
                self.last_val = 0
            elif val == 0:
                self.enc._value = self.max_val
                self.last_val = self.max_val
            else:
                self.last_val = val

    def setDirection(self, direction):
        for led in self.leds:
            led.value(0)
        self.leds[direction].value(1)
        self.direction = direction
