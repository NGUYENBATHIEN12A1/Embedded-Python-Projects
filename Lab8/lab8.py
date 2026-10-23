"""
Lab 8 - MQTT: Connect ESP32 to Node-RED
Board : ESP32 (MicroPython)

"""

import gc
import json
import network
import machine
import ubinascii
from machine import Pin
from time import sleep, sleep_ms, ticks_ms, ticks_diff

try:
    from umqtt.simple import MQTTClient
except ImportError:
    from umqttsimple import MQTTClient

gc.collect()

# ======================================================================
# 1. CAU HINH
# ======================================================================
SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"

MQTT_BROKER = "172.26.92.2"
MQTT_PORT = 1883
KEEPALIVE = 10

DEVICE_NAME = "ESP32 Lab 8"

TOPIC_SUB = b"output"
TOPIC_PUB = b"temp"
TOPIC_HUM = b"humidity"
TOPIC_STATUS = b"status"
TOPIC_INFO = b"info"

SENSOR = "DHT11"
SENSOR_PIN = 4
ONBOARD_LED_PIN = 2
ONBOARD_LED_ACTIVE_LOW = False

READINGS_INTERVAL_MS = 5000
PING_INTERVAL_MS = 5000
RECONNECT_S = 5
WIFI_TIMEOUT = 15

led = Pin(ONBOARD_LED_PIN, Pin.OUT)


def set_led(on):
    led.value((not on) if ONBOARD_LED_ACTIVE_LOW else on)


set_led(False)

if SENSOR == "DS18B20":
    import onewire
    import ds18x20
    ds_sensor = ds18x20.DS18X20(onewire.OneWire(Pin(SENSOR_PIN)))
    SENSOR_ERRORS = (onewire.OneWireError,)
else:
    import dht
    dht_sensor = dht.DHT11(Pin(SENSOR_PIN))
    SENSOR_ERRORS = ()

CLIENT_ID = b"esp32-nodered-" + ubinascii.hexlify(machine.unique_id())


# ======================================================================
# 2. KET NOI WI-FI
# ======================================================================
def connect_wifi():
    station = network.WLAN(network.STA_IF)
    station.active(True)

    if not station.isconnected():
        print("Connecting to Wi-Fi:", SSID)
        try:
            station.disconnect()
        except OSError:
            pass
        try:
            station.connect(SSID, PASSWORD)
        except OSError as e:
            print("Wi-Fi bi ket (%s), khoi dong lai Wi-Fi..." % e)
            station.active(False)
            sleep(1)
            station.active(True)
            station.connect(SSID, PASSWORD)

        waited = 0
        while not station.isconnected() and waited < WIFI_TIMEOUT:
            sleep(1)
            waited += 1
            print("  ...", waited, "s")

    if not station.isconnected():
        raise OSError("Wi-Fi connection failed")

    print("Connection successful")
    print(station.ifconfig())
    return station


# ======================================================================
# 3. DOC CAM BIEN
# ======================================================================
def read_ds_sensor():
    roms = ds_sensor.scan()
    if not roms:
        print("Khong tim thay DS18B20 tren GPIO", SENSOR_PIN)
        return None, None
    ds_sensor.convert_temp()
    sleep_ms(750)
    temp = ds_sensor.read_temp(roms[0])
    return (temp if isinstance(temp, float) else None), None


def read_dht_sensor():
    dht_sensor.measure()
    return float(dht_sensor.temperature()), float(dht_sensor.humidity())


def read_sensor():
    if SENSOR == "DS18B20":
        return read_ds_sensor()
    return read_dht_sensor()


# ======================================================================
# 4. MQTT
# ======================================================================
def sub_cb(topic, msg):
    print("<-", topic.decode(), msg.decode())
    if msg == b"on":
        set_led(True)
        print("LED onboard -> ON")
    elif msg == b"off":
        set_led(False)
        print("LED onboard -> OFF")


def device_info(station):
    return json.dumps({
        "name": DEVICE_NAME,
        "ip": station.ifconfig()[0],
        "mac": ubinascii.hexlify(station.config("mac"), ":").decode(),
        "broker": "%s:%d" % (MQTT_BROKER, MQTT_PORT),
        "client_id": CLIENT_ID.decode(),
        "sensor": "%s (GPIO%d)" % (SENSOR, SENSOR_PIN),
    }).encode()


def connect_and_subscribe(station):
    client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=MQTT_PORT,
                        keepalive=KEEPALIVE)
    client.set_callback(sub_cb)
    client.set_last_will(TOPIC_STATUS, b"offline", retain=True, qos=1)
    client.connect()
    client.subscribe(TOPIC_SUB)
    print("Connected to %s MQTT broker, subscribed to %s topic"
          % (MQTT_BROKER, TOPIC_SUB.decode()))

    client.publish(TOPIC_STATUS, b"online", retain=True, qos=1)
    client.publish(TOPIC_INFO, device_info(station), retain=True, qos=1)
    print("->", TOPIC_STATUS.decode(), "online")
    return client


def go_offline(client):
    try:
        client.publish(TOPIC_STATUS, b"offline", retain=True, qos=1)
        client.disconnect()
        print("->", TOPIC_STATUS.decode(), "offline")
    except OSError:
        pass


def publish_value(client, topic, value):
    if value is None:
        return
    msg = ("%.1f" % value).encode()
    client.publish(topic, msg)
    print("->", topic.decode(), msg.decode())


def publish_readings(client):
    try:
        temp, hum = read_sensor()
    except SENSOR_ERRORS + (OSError,) as e:
        print("Failed to read sensor:", e)
        return

    publish_value(client, TOPIC_PUB, temp)
    publish_value(client, TOPIC_HUM, hum)


def run(client):
    last_reading = ticks_ms() - READINGS_INTERVAL_MS
    last_ping = ticks_ms()

    while True:
        client.check_msg()

        now = ticks_ms()
        if ticks_diff(now, last_reading) >= READINGS_INTERVAL_MS:
            last_reading = now
            publish_readings(client)

        if ticks_diff(now, last_ping) >= PING_INTERVAL_MS:
            last_ping = now
            client.ping()

        sleep_ms(50)


# ======================================================================
# 5. CHUONG TRINH CHINH
# ======================================================================
def main():
    station = connect_wifi()

    while True:
        client = None
        try:
            client = connect_and_subscribe(station)
            run(client)
        except OSError as e:
            print("MQTT error:", e)
            print("Reconnecting in", RECONNECT_S, "s")
            sleep(RECONNECT_S)
        except KeyboardInterrupt:
            if client:
                go_offline(client)
            raise


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        set_led(False)
        print("Stopped by user.")

