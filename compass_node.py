import uasyncio as asyncio
from compass import Compass
from machine import reset, Pin, ADC
from time import sleep


async def heartbeat():
    while True:
        await asyncio.sleep_ms(25)

        await asyncio.sleep_ms(900)


async def main(compass, input_pause):
    while True:
        if(input_pause.value() == 1):
            if not compass.pause_val:
                compass.pause_val = compass.enc._value
            print("pause")
            compass.enc._value = compass.pause_val
            await asyncio.sleep_ms(200)
        else:
            if compass.pause_val:
                compass.enc._value = compass.pause_val
                compass.pause_val = None
            compass.checkDirection()
            print(compass.getDirection())
            await asyncio.sleep_ms(100)


# Set up compass
compass = Compass(enc=(12, 13), north=2, south=0, west=14, east=4, output1=16, output2=15)

input_pause = Pin(5, Pin.IN)

# Set up async
loop = asyncio.get_event_loop()
sleep(1)

try:
    loop.run_until_complete(main(compass, input_pause))
except KeyboardInterrupt:
    print("Bye")
except OSError:
    reset()
finally:
    pass
