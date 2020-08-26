import paho.mqtt.client as mqtt
import asyncio
from gpiozero import Button, LED
from time import sleep
import subprocess


class HardwareInterface:
    def __init__(self):
        self.mqtt_client = None
        self.maps_leds_pulse = None

        self.btn_run = Button(10, bounce_time=0.1)
        self.btn_map1 = Button(17, bounce_time=0.1, hold_time=5)
        self.btn_map2 = Button(27, bounce_time=0.1, hold_time=5)
        self.btn_map3 = Button(22, bounce_time=0.1, hold_time=5)
        self.input_ipad = Button(25, bounce_time=2)
        self.output_pause = LED(18)
        self.output_powerswitch = LED(23)

        self.led_go = LED(4)

        self.map_leds = [
            LED(5),
            LED(9),
            LED(11)
        ]

        self.direction_states = [
            (Button(19), Button(26)),
            (Button(6), Button(13)),
            (Button(20), Button(21)),
            (Button(12), Button(16)),
        ]

        self.directions = ["N", "E", "S", "W"]
        self.sleeping = True
        self.map_choice = False
        self.pause_input = True
        self.device_switch = False

        self.mqtt_pub_topic_direction = "directions"
        self.mqtt_pub_topic_map = "map"

    def add_client(self, client):
        self.client = client

    def set_map(self, chosen_map):
        self.map_choice = int(chosen_map)
        # self.maps_leds_pulse = False
        # sleep(2)

        self.send_msg(self.mqtt_pub_topic_map, chosen_map, qos=1)
        # Turn on hw-controller
        self.output_powerswitch.on()
        print("map chosen")

    def pause(self):
        self.pause_input = True
        self.output_pause.on()
        self.led_go.off()
        sleep(0.1)
        print("pause hardware input")

    def resume(self):
        self.pause_input = False
        self.output_pause.off()
        self.led_go.on()
        sleep(0.1)
        print("resume hardware input")

    def sleep(self):
        self.send_msg(self.mqtt_pub_topic_map, "-1", qos=1)
        self.sleeping = True
        for led in self.map_leds:
            led.off()
        self.output_powerswitch.off()
        self.pause()
        # self.maps_leds_pulse = False
        # self.map_leds[self.map_choice-1].off()
        sleep(0.1)
        print("put to sleep")

    async def rotateMapLed(self):
        while not self.map_choice and not self.sleeping:
            for led in self.map_leds:
                led.toggle()
            await asyncio.sleep(1)

        for led in self.map_leds:
            led.off()
        if not self.sleeping:
            self.map_leds[self.map_choice-1].on()

    def wake(self):
        self.sleeping = False
        self.map_choice = False
        # self.maps_leds_pulse = True
        asyncio.ensure_future(self.rotateMapLed())
        # for led in self.map_leds:
        #     led.on()
        #     sleep(0.5)
        #     led.off()
        #     sleep(0.5)
        # Wait for hardware boot
        sleep(0.1)
        # Send wake to gui
        self.send_msg(self.mqtt_pub_topic_map, "0", qos=1)
        print("waking")

    def send_directions(self):
        self.pause()
        data_out = []
        for direction in self.direction_states:
            try:
                if direction[0].is_active and direction[1].is_active:
                    data_out.append(self.directions[0])
                elif direction[0].is_active and not direction[1].is_active:
                    data_out.append(self.directions[1])
                elif not direction[0].is_active and not direction[1].is_active:
                    data_out.append(self.directions[2])
                elif not direction[0].is_active and direction[1].is_active:
                    data_out.append(self.directions[3])
            except Exception as e:
                data_out = False
                print(e)

        if data_out:
            data_out = ','.join(data_out)
            # data_out = json.dumps(data_out)
        else:
            data_out = 'error'

        print(self.mqtt_pub_topic_direction + ': ' + data_out)
        self.send_msg(self.mqtt_pub_topic_direction, data_out, qos=1)

    def send_msg(self, topic, msg, qos=1):
        try:
            self.client.publish(topic, msg, qos=qos)
        except Exception as e:
            print(e)

    def on_message_status(self, client, userdata, msg):
        msg.payload = msg.payload.decode()
        try:
            status = int(msg.payload)
        except Exception:
            print("not valid status message")
            status = None

        if status == 0:
            # Resume
            hardwareInterface.resume()
        elif status == 1:
            # Pause
            hardwareInterface.pause()
        elif status == 2:
            # Sleep / reset
            hardwareInterface.pause()

        print("Topic: ", msg.topic + "\nMessage: " + msg.payload)


# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    # rc is the error code returned when connecting to the broker
    print("Connected!", str(rc))

    # Subscribe to status topic
    client.subscribe(mqtt_topic, qos=1)


def on_disconnect(client, userdata, rc):
    print("Client Got Disconnected")


def on_message(client, userdata, msg):
    msg.payload = msg.payload.decode()
    print("Topic: ", msg.topic + "\nMessage: " + msg.payload)


# MAIN LOOP
async def main():
    while True:
        if (
            hardwareInterface.btn_map1.is_held and
            hardwareInterface.btn_map3.is_held and not
            hardwareInterface.input_ipad.is_active
        ):
            if hardwareInterface.btn_run.is_active:
                # Restart
                subprocess.Popen(['sudo', 'shutdown', '-r', 'now'])
            else:
                # Shutdown
                subprocess.Popen(['sudo', 'shutdown', '-h', 'now'])

        if hardwareInterface.input_ipad.is_active:
            # Ipad connected, wake gui and esp
            if hardwareInterface.sleeping:
                hardwareInterface.wake()

            # Map not chosen, wait for input
            if not hardwareInterface.map_choice:
                if hardwareInterface.btn_map1.is_active:
                    hardwareInterface.set_map("1")
                elif hardwareInterface.btn_map2.is_active:
                    hardwareInterface.set_map("2")
                elif hardwareInterface.btn_map3.is_active:
                    hardwareInterface.set_map("3")

            # Sending directions
            elif (
                hardwareInterface.map_choice and
                hardwareInterface.btn_run.is_active and
                not hardwareInterface.pause_input
            ):
                # send directions to gui
                print("sending")
                hardwareInterface.send_directions()

            await asyncio.sleep(0.2)
        else:
            # ipad not connected
            if not hardwareInterface.sleeping:
                # Put to sleep and reset state
                hardwareInterface.sleep()

            print("sleeping")
            await asyncio.sleep(1)


# MQTT SETTINGS
mqtt_topic = "status"
mqtt_broker_ip = "localhost"
mqtt_port = 1883

client = mqtt.Client()
hardwareInterface = HardwareInterface()

client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
client.message_callback_add(mqtt_topic, hardwareInterface.on_message_status)

client.connect(mqtt_broker_ip, mqtt_port)
client.loop_start()

hardwareInterface.add_client(client)

# Set up async
loop = asyncio.get_event_loop()

hardwareInterface.wake()
sleep(4)

try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    print("Bye")
except Exception as e:
    print(e)
finally:
    hardwareInterface.sleep()
    sleep(1)
