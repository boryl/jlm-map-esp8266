import paho.mqtt.client as mqtt
import asyncio
from gpiozero import Button, LED
import json
from time import sleep


mqtt_topic = "status"
mqtt_broker_ip = "localhost"
mqtt_port = 1883

mqtt_pub_topic_direction = "direction"
mqtt_pub_topic_map = "map"

client = mqtt.Client()

# GPIO setup
btn_run = Button(10, bounce_time=0.1)
btn_map1 = Button(17, bounce_time=0.1)
btn_map2 = Button(27, bounce_time=0.1)
btn_map3 = Button(22, bounce_time=0.1)
input_ipad = Button(24, bounce_time=0.2)
output_pause = LED(18)
output_powercontrol = LED(23)
# output_sleep = LED(23)
# output_wake = LED(25)


direction_states = [
    (Button(19), Button(26)),
    (Button(6), Button(13)),

    (Button(20), Button(21)),
    (Button(12), Button(16)),
]

# To check input state
# print(direction_states[0][0].is_active)

# Read and send direction values

# Activate pause

# Activate reset

# Resume esp

# Wake esp

# Send map

# Reset if ipad is removed
sleeping = True
map_choice = False
pause_input = True
reset = False


def send_error():
    client.publish(mqtt_topic, 3, qos=1)


async def main():
    global sleeping
    global map_choice
    global pause_input
    global reset

    directions = ["N", "E", "S", "W"]

    # output_wake.on()
    # await asyncio.sleep(3)
    # output_sleep.on()
    # await asyncio.sleep(0.5)
    # output_sleep.off()
    # await asyncio.sleep(3)

    while True:
        if input_ipad.is_active:
            # Ipad connected, wake gui and esp
            if sleeping:
                # Wake gui
                sleeping = False
                output_powercontrol.on()
                await asyncio.sleep(3)
                # Send wake to gui
                client.publish(mqtt_pub_topic_map, "0", qos=1)
                print("waking")

            if pause_input or not map_choice:
                output_pause.on()
            else:
                output_pause.off()

            # Chosing map
            if not map_choice and (
                btn_map1.is_active or btn_map2.is_active or btn_map3.is_active
            ):
                # Send map to gui
                if btn_map1.is_active:
                    chosen_map = "1"
                elif btn_map2.is_active:
                    chosen_map = "2"
                elif btn_map3.is_active:
                    chosen_map = "3"

                try:
                    client.publish(mqtt_pub_topic_map, chosen_map, qos=1)
                    map_choice = True
                    print("map chosen")
                except Exception as e:
                    send_error()
                    print(e)

            # Sending directions
            elif map_choice and btn_run.is_active and not pause_input:
                # send directions to gui
                print("send")
                data_out = []
                for direction in direction_states:
                    try:
                        if direction[0].is_active and direction[1].is_active:
                            data_out.append(directions[0])
                        elif direction[0].is_active and not direction[1].is_active:
                            data_out.append(directions[1])
                        elif not direction[0].is_active and not direction[1].is_active:
                            data_out.append(directions[2])
                        elif not direction[0].is_active and direction[1].is_active:
                            data_out.append(directions[3])
                    except Exception as e:
                        send_error()
                        print(e)
                data_out = json.dumps(data_out)
                print(data_out)
                try:
                    pause_input = True
                    client.publish(mqtt_pub_topic_direction, data_out, qos=1)
                    print("sending directions")
                except Exception as e:
                    send_error()
                    print(e)

            await asyncio.sleep(0.2)
        else:
            # ipad not connected
            if not sleeping:
                # sleep esp
                # reset gui
                # reset map
                # Send mqtt to notify gui that ipad is removed
                client.publish(mqtt_pub_topic_map, "-1", qos=1)
                map_choice = False
                sleeping = True
                output_powercontrol.off()

                print("init sleep")
            print("sleeping")
            await asyncio.sleep(1)


def on_connect(client, userdata, flags, rc):
    # rc is the error code returned when connecting to the broker
    print("Connected!", str(rc))

    # Subscribe to status topic and add callback
    client.subscribe(mqtt_topic, qos=1)


def on_disconnect(client, userdata, rc):
    print("Client Got Disconnected")


def on_message(client, userdata, msg):
    print("callback")
    msg.payload = msg.payload.decode()
    print("Topic: ", msg.topic + "\nMessage: " + msg.payload)


def on_message_status(client, userdata, msg):
    global pause_input
    global sleeping

    print("callback")
    msg.payload = msg.payload.decode()
    status = int(msg.payload)

    if status == 0:
        # Resume
        pause_input = False
    elif status == 1:
        # Pause
        pause_input = True
    elif status == 2:
        # Sleep / reset
        pause_input = True
        # sleeping = True

    print("Status: ", msg.topic + "\nMessage: " + msg.payload)


# Here, we are telling the client which functions are to be run
# on connecting, and on receiving a message
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.message_callback_add(mqtt_topic, on_message_status)

client.connect(mqtt_broker_ip, mqtt_port)
client.loop_start()

# Set up async
loop = asyncio.get_event_loop()
# loop.create_task(heartbeat())

try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    print("Bye")
except Exception as e:
    import subprocess
    print(e)
    print("reboot")
    # subprocess.Popen(['sudo','shutdown','-r','now'])
finally:
    client.disconnect()
    output_powercontrol.off()
    # sleep(0.5)
    # output_sleep.off()
