import network
import time
import dht
from machine import Pin
from umqtt.simple import MQTTClient

# --- CẤU HÌNH WIFI & MQTT ---
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASS = "YOUR_WIFI_PASSWORD"

MQTT_BROKER = "broker.emqx.io"
CLIENT_ID = "ESP32_Thien_Sender_01"
TOPIC_DHT = b"vku/esp32/dht_data"
TOPIC_BUTTON = b"vku/esp32/button_status"

# --- CẤU HÌNH PHẦN CỨNG ---
sensor = dht.DHT11(Pin(4)) 
button = Pin(5, Pin.IN, Pin.PULL_UP)

# --- KẾT NỐI WIFI ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# BẮT BUỘC PHẢI CÓ 2 DÒNG NÀY ĐỂ XÓA TRẠNG THÁI LỖI CŨ
wlan.disconnect()
time.sleep(1)

wlan.connect(WIFI_SSID, WIFI_PASS)

print("Đang kết nối Wi-Fi...")
timeout = 15
while not wlan.isconnected() and timeout > 0:
    time.sleep(1)
    timeout -= 1
    print(".", end="")

if wlan.isconnected():
    print("\nWi-Fi Connected! IP:", wlan.ifconfig()[0])
    print("Đang chờ ổn định mạng (3s)...")
    time.sleep(3)
else:
    print("\nLỗi kết nối Wi-Fi! Vui lòng kiểm tra lại mạng.")

# --- KẾT NỐI MQTT BROKER ---
client = MQTTClient(CLIENT_ID, MQTT_BROKER, keepalive=60)
try:
    client.connect()
    print("Đã kết nối MQTT Broker thành công!")
except Exception as e:
    print("Lỗi kết nối MQTT:", e)

last_button_state = 1
last_dht_time = time.ticks_ms()

while True:
    try:
        current_button_state = button.value()
        if current_button_state != last_button_state:
            time.sleep_ms(20)
            if button.value() == current_button_state:
                if current_button_state == 0: 
                    client.publish(TOPIC_BUTTON, b"ON")
                    print("Đã Publish: Nút nhấn ON")
                else: 
                    client.publish(TOPIC_BUTTON, b"OFF")
                    print("Đã Publish: Nút nhấn OFF")
                last_button_state = current_button_state

        if time.ticks_diff(time.ticks_ms(), last_dht_time) > 2000:
            try:
                sensor.measure()
                t = sensor.temperature()
                h = sensor.humidity()
                payload = "Nhiet do: {}C - Do am: {}%".format(t, h)
                client.publish(TOPIC_DHT, payload.encode())
                print("Đã Publish:", payload)
            except OSError as e:
                print("Lỗi đọc cảm biến DHT")
            last_dht_time = time.ticks_ms()
        
        time.sleep_ms(50)
        
    except OSError as e:
        print("Mất kết nối, đang thử lại...")
        time.sleep(5)