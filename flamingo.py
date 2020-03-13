from machine import Pin, ADC, deepsleep
import uasyncio as asyncio
import ujson
import esp32


class Flamingo:

    def __init__(self, machine_config):
        self.battery_reader = ADC(Pin(35))
        self.battery_reader.atten(ADC.ATTN_11DB)
        self.battery_threshold = machine_config['battery_threshold']
        self.battery_led = Pin(machine_config['battery_led'], Pin.OUT)
        self.battery_level = self.batteryCheck()

        self.led_strip1 = Pin(machine_config['led_strip1'], Pin.OUT)
        self.led_strip2 = Pin(machine_config['led_strip2'], Pin.OUT)

        self.battery_led.value(1)

        self.power_switch = Pin(machine_config['power_switch'], Pin.IN)
        esp32.wake_on_ext0(pin=self.power_switch, level=esp32.WAKEUP_ANY_HIGH)

    def batteryCheck(self):
        battery_level = (self.battery_reader.read()/4095)*2*3.3*1.1
        return battery_level

    def toggleLed(self, led):
        led.value(not(led.value()))

    def putToSleep(self):
        deepsleep()

    async def flashLed(self, json):
        try:
            json = ujson.loads(json)
            on_for = int(json['on_for'])
        except Exception:
            on_for = 1000

        self.led_strip1.value(1)
        self.led_strip2.value(1)
        print("strips on")
        await asyncio.sleep_ms(on_for)
        self.led_strip1.value(0)
        self.led_strip2.value(0)
        print("strips off")
