from config import machine_config
import uasyncio as asyncio
from compass import Compass
from machine import reset, Pin


async def heartbeat():
    while True:
        await asyncio.sleep_ms(25)

        await asyncio.sleep_ms(900)


async def main(compass1, btn_send):
    directions = [
        "north",
        "east",
        "south",
        "west"
    ]
    while True:
        compass1.checkDirection()
        if(btn_send.value() == 0):
            print("sending")
            await asyncio.sleep_ms(5000)
        await asyncio.sleep_ms(50)


# Set up compass
compass1 = Compass(enc=(19, 23), north=13, south=12, west=14, east=27)
btn_send = Pin(4, Pin.IN, Pin.PULL_UP)

# Set up async
loop = asyncio.get_event_loop()
# loop.create_task(heartbeat())


try:
    loop.run_until_complete(main(compass1, btn_send))
except KeyboardInterrupt:
    print("Bye")
except OSError:
    reset()
finally:
    pass
