import network, espnow
from machine import Pin

# ===== CẤU HÌNH =====
CHANNEL = 6
PEER = bytes.fromhex('5c013b9cf730')   # MAC của esp_1 (gửi)
LED_PIN = 2

# ===== PHẦN CỨNG =====
led = Pin(LED_PIN, Pin.OUT, value=0)

# ===== WI-FI & ESP-NOW =====
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.disconnect()
wlan.config(channel=CHANNEL)

e = espnow.ESPNow()
e.active(True)

print("=== ESP 2 (esp_2): ĐANG ĐỢI DỮ LIỆU TỪ ESP 1 ===")

while True:
    host, msg = e.irecv(500)   # (None, None) nếu timeout
    if msg is None or host != PEER:
        continue

    try:
        text = msg.decode('utf-8')
    except UnicodeError:
        continue

    if text == "LED:ON":
        led.value(1)
        print(">>> [ĐIỀU KHIỂN] LED BẬT")

    elif text == "LED:OFF":
        led.value(0)
        print(">>> [ĐIỀU KHIỂN] LED TẮT")

    elif text.startswith("DHT:"):
        parts = text[4:].split(",")
        if len(parts) == 2:
            print("[CẢM BIẾN ESP 1] Nhiệt độ: {} °C | Độ ẩm: {} %".format(parts[0], parts[1]))