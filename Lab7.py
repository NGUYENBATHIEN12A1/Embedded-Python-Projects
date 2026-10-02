import network
import time
import dht
from machine import Pin
from umqtt.simple import MQTTClient

# --- CẤU HÌNH WIFI & MQTT ---
WIFI_SSID = "Xom nha la"
WIFI_PASS = "hoivuongdi"

# ĐỔI SANG SERVER EMQX ĐỂ ỔN ĐỊNH HƠN
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
wlan.connect(WIFI_SSID, WIFI_PASS)

print("Đang kết nối Wi-Fi...")
while not wlan.isconnected():
    time.sleep(0.5)
print("Wi-Fi Connected! IP:", wlan.ifconfig()[0])

# THÊM DÒNG NÀY: Chờ 3 giây để hệ thống mạng ổn định trước khi gọi MQTT
print("Đang chờ ổn định mạng (3s)...")
time.sleep(3)

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
            time.sleep_ms(20) # Chống dội phím
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





import network
import time
from machine import Pin
from umqtt.simple import MQTTClient

# --- CẤU HÌNH WIFI & MQTT ---
WIFI_SSID = "Xom nha la"
WIFI_PASS = "hoivuongdi"

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
