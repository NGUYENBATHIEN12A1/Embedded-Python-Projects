import network, espnow, time, dht
from machine import Pin

# ===== CẤU HÌNH =====
CHANNEL = 6
PEER = bytes.fromhex('ece334232144')   # MAC của esp_2 (nhận)
DHT_PIN = 14
BTN_PIN = 19
SENSOR_INTERVAL_MS = 3000
DEBOUNCE_MS = 200

# ===== PHẦN CỨNG =====
sensor = dht.DHT11(Pin(DHT_PIN))
button = Pin(BTN_PIN, Pin.IN, Pin.PULL_UP)   # nhấn = 0

# ===== WI-FI & ESP-NOW =====
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.disconnect()
wlan.config(channel=CHANNEL)

e = espnow.ESPNow()
e.active(True)
try:
    e.add_peer(PEER)
except OSError:
    pass  # peer đã tồn tại

print("=== ESP 1 (esp_1): DHT11 & BUTTON SẴN SÀNG ===")

led_state = False
last_btn = 1
last_sensor = time.ticks_ms()

while True:
    now = time.ticks_ms()

    # A. Nút nhấn: phát hiện sườn xuống -> đảo trạng thái LED bên ESP 2
    cur_btn = button.value()
    if last_btn == 1 and cur_btn == 0:
        new_state = not led_state
        cmd = "LED:ON" if new_state else "LED:OFF"
        try:
            if e.send(PEER, cmd):
                led_state = new_state   # chỉ cập nhật khi ESP 2 đã ACK
                print("[Nút nhấn] Đã gửi ->", cmd)
            else:
                print("[Nút nhấn] Gửi thất bại (không có ACK), giữ nguyên trạng thái")
        except OSError as err:
            print("[Lỗi gửi nút nhấn]:", err)
        time.sleep_ms(DEBOUNCE_MS)
        cur_btn = button.value()
    last_btn = cur_btn

    # B. Định kỳ đọc DHT11 và gửi
    if time.ticks_diff(now, last_sensor) >= SENSOR_INTERVAL_MS:
        last_sensor = now
        try:
            sensor.measure()
            t = sensor.temperature()
            h = sensor.humidity()
            ok = e.send(PEER, "DHT:{},{}".format(t, h))
            print("[Cảm biến] {}°C | {}% | {}".format(t, h, "OK" if ok else "không có ACK"))
        except OSError as err:
            print("[Lỗi DHT11/gửi] Kiểm tra dây chân {}:".format(DHT_PIN), err)

    time.sleep_ms(20)