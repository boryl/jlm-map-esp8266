from machine import Pin

try:
    from mqtt_as import config
except Exception:
    config = {}


def ledfunc(pin):
    pin = pin

    def func(v):
        pin(not v)  # Active low on ESP8266
    return func


# MQTT config
config['server'] = ''
config['port'] = 1883
config['user'] = ''
config['password'] = ''

# Wifi config
config['ssid'] = ''
config['wifi_pw'] = ''

# Other config
app_config = {}
app_config['sub_topic'] = ''

machine_config = {}
machine_config['battery_led'] = 26
machine_config['led_strip1'] = 15
machine_config['led_strip2'] = 33
machine_config['power_switch'] = 14
machine_config['wifi_led'] = ledfunc(Pin(25, Pin.OUT, value=0))
machine_config['battery_threshold'] = 3.6
