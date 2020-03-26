from machine import Pin
from encoder import Encoder
from time import sleep


class Compass:

    def __init__(self, enc, north, east, south, west, output1, output2):

        self.max_val = 48

        self.enc = Encoder(*enc, max_val=self.max_val+1, pin_mode=Pin.PULL_UP)
        self.enc._value = 6
        self.pause_val = None

        self.leds = [
            Pin(north, Pin.OUT),
            Pin(east, Pin.OUT),
            Pin(south, Pin.OUT),
            Pin(west, Pin.OUT)
        ]
        self.output_leds = [
            Pin(output1, Pin.OUT),
            Pin(output2, Pin.OUT),
        ]
        self.output_states = [[0, 0], [1, 0], [1, 1], [0, 1]]
        
        self.directions = [
            "N",
            "E",
            "S",
            "W"
        ]

        self.direction = 0
        self.last_val = 1
        
        self.turnOffLeds()
        self.rotateLeds()
        self.setDirection(self.direction)

    def checkDirection(self):
        val = self.enc.value
        if(val != self.last_val):
            if val >= 1 and val <= 12:
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
            if val > self.max_val:
                # self.enc.reset()
                self.enc._value = 1
                self.last_val = 1
            elif val < 1:
                self.enc._value = self.max_val
                self.last_val = self.max_val
            else:
                self.last_val = val

    def setDirection(self, direction):
        for led in self.leds:
            led.value(0)
        self.leds[direction].value(1)
        self.direction = direction
        output_state = self.output_states[direction]
        for x in range(len(self.output_leds)):
            self.output_leds[x].value(output_state[x])
    
    def getDirection(self):
        return self.directions[self.direction]
    
    def turnOffLeds(self):
        for led in self.leds:
            led.value(0)
        for led in self.output_leds:
            led.value(0)
    
    def rotateLeds(self):
        for led in self.leds:
            led.value(1)
            sleep(0.2)
            led.value(0)
            sleep(0.2)
            
            led.value(0)
