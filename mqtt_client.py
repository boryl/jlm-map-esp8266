from mqtt_as import MQTTClient, config
from config import app_config, machine_config
import uasyncio as asyncio
from flamingo import Flamingo
from machine import reset


# Subscription callback
def sub_cb(topic, msg):
    loop.create_task(
        flamingo.flashLed(msg.decode('utf-8'))
        )


async def heartbeat():
    while True:
        await asyncio.sleep_ms(25)
        if not flamingo.power_switch.value():
            flamingo.putToSleep()
        await asyncio.sleep_ms(900)


async def batteryProcess():
    while True:
        if(flamingo.battery_level < flamingo.battery_threshold):
            print("battery warning, on")
            await asyncio.sleep_ms(150)
            flamingo.toggleLed(flamingo.battery_led)
            await asyncio.sleep_ms(1500)
            print("battery warning, off")
        else:
            print("battery ok!")
            await asyncio.sleep(60)
            flamingo.battery_level = flamingo.batteryCheck()


async def wifi_han(state):
    global wifi_attempts
    global wifi_max_attempts
    machine_config['wifi_led'](not state)
    print('Wifi is ', 'up' if state else 'down')

    # Restart after x attempts
    if not state:
        if (wifi_attempts >= wifi_max_attempts):
            reset()
        wifi_attempts += 1
    await asyncio.sleep(3)


async def conn_han(client):
    await client.subscribe(app_config['sub_topic'], 1)


async def main(client):
    try:
        await client.connect()
    except OSError:
        print('Connection failed.')
        reset()
        return
    while True:
        await asyncio.sleep(5)

# Define configuration
config['subs_cb'] = sub_cb
config['wifi_coro'] = wifi_han
config['connect_coro'] = conn_han
config['clean'] = True

# Set up client
MQTTClient.DEBUG = False  # Optional
client = MQTTClient(config)

# Set up Flamingo
flamingo = Flamingo(machine_config)

# Set up async
loop = asyncio.get_event_loop()
loop.create_task(heartbeat())
loop.create_task(batteryProcess())

wifi_attempts = 0
wifi_max_attempts = 3

try:
    loop.run_until_complete(main(client))
except KeyboardInterrupt:
    client.close()
    print("Bye")
except OSError as e:
    print(e)
    reset()
finally:
    client.close()
