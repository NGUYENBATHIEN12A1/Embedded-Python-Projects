import network
import time
from machine import Pin
from umqtt.simple import MQTTClient

# --- CẤU HÌNH WIFI & MQTT ---
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASS = "YOUR_WIFI_PASSWORD"

MQTT_BROKER = "broker.emqx.io" # Đã khớp với ESP1
CLIENT_ID = "ESP32_Thien_Receiver_01"
TOPIC_DHT = b"vku/esp32/dht_data"
TOPIC_BUTTON = b"vku/esp32/button_status"

# --- CẤU HÌNH PHẦN CỨNG ---
led = Pin(2, Pin.OUT) # Dùng đèn LED màu xanh dương có sẵn trên mạch

# --- HÀM XỬ LÝ DỮ LIỆU NHẬN ĐƯỢC ---
def sub_cb(topic, msg):
    # In ra Terminal
    print(f"[Đã nhận] Topic: {topic.decode()} | Message: {msg.decode()}")
    
    # Điều khiển LED
    if topic == TOPIC_BUTTON:
        if msg == b"ON":
            led.value(1) # Sáng LED
        elif msg == b"OFF":
            led.value(0) # Tắt LED

# --- KẾT NỐI WIFI ---
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(WIFI_SSID, WIFI_PASS)

print("Đang kết nối Wi-Fi...")
while not wlan.isconnected():
    time.sleep(0.5)
print("Wi-Fi Connected! IP:", wlan.ifconfig()[0])

print("Đang chờ ổn định mạng (3s)...")
time.sleep(3)

# --- KẾT NỐI VÀ SUBSCRIBE MQTT BROKER ---
client = MQTTClient(CLIENT_ID, MQTT_BROKER, keepalive=60)
client.set_callback(sub_cb)

try:
    client.connect()
    client.subscribe(TOPIC_DHT)
    client.subscribe(TOPIC_BUTTON)
    print("Đã kết nối và Subscribe MQTT Broker thành công!")
except Exception as e:
    print("Lỗi kết nối MQTT:", e)

# Vòng lặp chờ nhận dữ liệu
print("Đang chờ dữ liệu từ ESP1...")
while True:
    try:
        client.check_msg()
        time.sleep_ms(100)
    except OSError as e:
        print("Lỗi kết nối, kiểm tra lại...")
        time.sleep(5)