import network
import socket
from machine import Pin
import time

SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"

# Khai báo LED (GPIO 2)
led = Pin(2, Pin.OUT)
led_mode = "OFF"
blink_last_time = time.ticks_ms()

# Kết nối Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)
print("Đang kết nối Wi-Fi...")
while not wlan.isconnected():
    time.sleep(0.5)

ip_address = wlan.ifconfig()[0]
print(f"Web Server đang chạy tại: http://{ip_address}")

def web_page():
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>ESP32 LED Controller</title>
    <style>
        body {{ font-family: Arial; text-align: center; margin-top: 50px; background-color: #f4f4f9; }}
        h1 {{ color: #333; }}
        .btn {{ display: inline-block; padding: 12px 24px; font-size: 18px; margin: 8px; text-decoration: none; border-radius: 5px; color: white; }}
        .btn-on {{ background-color: #28a745; }}
        .btn-off {{ background-color: #dc3545; }}
        .btn-blink {{ background-color: #ffc107; color: black; }}
        .status {{ font-size: 20px; font-weight: bold; margin: 20px; }}
    </style>
</head>
<body>
    <h1>ESP32 Web Server</h1>
    <p class="status">Trạng thái LED hiện tại: <span style="color: blue;">{led_mode}</span></p>
    <p>
        <a href="/?cmd=on"><button class="btn btn-on">ON</button></a>
        <a href="/?cmd=off"><button class="btn btn-off">OFF</button></a>
        <a href="/?cmd=blink"><button class="btn btn-blink">BLINK</button></a>
    </p>
</body>
</html>"""

# Khởi tạo Socket Server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(('', 80))
s.listen(5)
s.setblocking(False)

try:
    while True:
        # Xử lý chế độ Blink non-blocking
        if led_mode == "BLINK":
            if time.ticks_diff(time.ticks_ms(), blink_last_time) > 300:
                led.value(not led.value())
                blink_last_time = time.ticks_ms()

        # Nhận kết nối client
        try:
            conn, addr = s.accept()
        except OSError:
            time.sleep_ms(20)
            continue

        # Đọc dữ liệu request an toàn
        try:
            conn.settimeout(1.0)
            request = conn.recv(1024).decode('utf-8')
        except Exception:
            conn.close()
            continue

        # Xử lý lệnh từ URL request
        if "GET /?cmd=on" in request:
            led.value(1)
            led_mode = "ON"
        elif "GET /?cmd=off" in request:
            led.value(0)
            led_mode = "OFF"
        elif "GET /?cmd=blink" in request:
            led_mode = "BLINK"

        # Trả phản hồi HTTP
        try:
            response = web_page()
            conn.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n')
            conn.sendall(response)
        except Exception as e:
            print("Lỗi gửi dữ liệu:", e)
        finally:
            conn.close()

except KeyboardInterrupt:
    s.close()
    print("Server đã dừng.")