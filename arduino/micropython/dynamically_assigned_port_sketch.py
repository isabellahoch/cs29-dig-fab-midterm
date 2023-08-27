import time
import machine
import neopixel
from umqtt.simple import MQTTClient
import network
import ujson

# WiFi settings
WIFI_SSID = '<your_wifi_ssid>'
WIFI_PASSWORD = '<your_wifi_password>'

# WebSocket server settings
WEBSOCKET_SERVER_URI = 'ws://192.168.1.55:8080'

# LED settings
NUM_LEDS = 30
DATA_PIN = 2  # GPIO2 (D2) on ESP32

np = neopixel.NeoPixel(machine.Pin(DATA_PIN), NUM_LEDS)

mqtt_client = None
is_light_on = False
hue = 0

def connect_to_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            pass
    print('Connected to WiFi')
    print('IP address:', wlan.ifconfig()[0])

def on_message(topic, msg):
    global is_light_on
    print('Got Message:', msg)
    if msg == b'ON':
        is_light_on = True
    elif msg == b'OFF':
        is_light_on = False

def on_connect(client, userdata, flags, rc):
    print('Connected to MQTT broker')
    client.subscribe(b'light/status')

def setup():
    global mqtt_client

    print('Setting up...')
    connect_to_wifi()

    mqtt_client = MQTTClient('esp32', '192.168.1.55')
    mqtt_client.set_callback(on_message)
    mqtt_client.connect()
    mqtt_client.subscribe('light/status')
    print('Connected to MQTT broker')

    print('Connecting to WebSocket server...')
    # No equivalent library for synchronous WebSocket support in MicroPython

def loop():
    global is_light_on, hue

    try:
        while True:
            mqtt_client.check_msg()

            if is_light_on:
                print('if')
                for i in range(NUM_LEDS):
                    np[i] = neopixel.colorwheel((hue + i * 10) % 255)
                np.write()

                hue += 1
            else:
                np.fill((0, 0, 0))
                np.write()

            time.sleep_ms(500)

    except KeyboardInterrupt:
        print('Exiting...')
        np.fill((0, 0, 0))
        np.write()

if __name__ == '__main__':
    setup()
    loop()
