import network #WIFI
import socket
import urequests #HTTP
import time
from machine import Pin

SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"

# Cấu hình thiết bị
led = Pin(2, Pin.OUT)
led_status = "OFF"
latest_data = "Đang cập nhật..."
last_fetch_time = 0
FETCH_INTERVAL_MS = 30000  # Cập nhật thời tiết mỗi 30 giây

wlan = network.WLAN(network.STA_IF)
#network.AP_IF
def ensure_wifi():
    """Kiểm tra và tự động kết nối lại Wi-Fi nếu bị rớt"""
    if not wlan.isconnected():
        wlan.active(True)
        wlan.connect(SSID, PASSWORD)
        print("Đang kết nối lại Wi-Fi...")
        t = 0
        while not wlan.isconnected() and t < 10:
            time.sleep(0.5)
            t += 1
        if wlan.isconnected():
            print("Đã kết nối Wi-Fi! IP:", wlan.ifconfig()[0])
            return True
        return False
    return True

def fetch_weather():
    """HTTP Client: Lấy Nhiệt độ, Độ ẩm, Tốc độ gió từ Open-Meteo"""
    global latest_data
    # Link API lấy cả 3 thông số ở thời điểm hiện tại (current)
    url = "https://api.open-meteo.com/v1/forecast?latitude=21.0285&longitude=105.8542&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
    try:
        print("[HTTP Client] Đang tải dữ liệu từ web service...")
        res = urequests.get(url)
        if res.status_code == 200:
            data = res.json()
            curr = data.get("current", {})
            
            temp = curr.get("temperature_2m")
            humidity = curr.get("relative_humidity_2m")
            wind = curr.get("wind_speed_10m")
            
            latest_data = f"Nhiệt độ: {temp} °C | Độ ẩm: {humidity} % | Gió: {wind} km/h"
            print(f"[HTTP Client] Dữ liệu mới: {latest_data}")
        else:
            latest_data = f"Lỗi Server: Mã {res.status_code}"
        res.close()
    except Exception as e:
        print("[HTTP Client] Lỗi kết nối:", e)
        latest_data = "Lỗi kết nối khi lấy dữ liệu"

def html_template():
    """Tạo giao diện HTML Dashboard"""
    ip = wlan.ifconfig()[0] if wlan.isconnected() else "Không khả dụng"
    wifi_st = "Đã kết nối (Connected)" if wlan.isconnected() else "Mất kết nối (Disconnected)"
    
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>ESP32 IoT Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; text-align: center; background-color: #eef2f3; padding: 20px; }}
        .card {{ background: white; border-radius: 8px; max-width: 480px; margin: 0 auto; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }}
        h2 {{ color: #2c3e50; }}
        .info {{ text-align: left; background: #fafafa; padding: 12px; border-radius: 6px; margin: 15px 0; }}
        .info p {{ margin: 6px 0; }}
        .btn {{ display: inline-block; padding: 10px 25px; font-size: 16px; margin: 10px; text-decoration: none; border-radius: 5px; color: white; border: none; cursor: pointer; }}
        .btn-on {{ background-color: #27ae60; }}
        .btn-off {{ background-color: #e74c3c; }}
    </style>
</head>
<body>
    <div class="card">
        <h2>Hệ Thống IoT ESP32</h2>
        <div class="info">
            <p><b>Địa chỉ IP:</b> {ip}</p>
            <p><b>Trạng thái Wi-Fi:</b> {wifi_st}</p>
            <p><b>Trạng thái LED:</b> <span style="color: blue;">{led_status}</span></p>
            <p><b>Thời tiết hiện tại:</b> <br><span style="color: #d35400;">{latest_data}</span></p>
        </div>
        <div>
            <a href="/?cmd=on"><button class="btn btn-on">BẬT LED (ON)</button></a>
            <a href="/?cmd=off"><button class="btn btn-off">TẮT LED (OFF)</button></a>
        </div>
    </div>
</body>
</html>"""

# Khởi động kết nối ban đầu
ensure_wifi()
if wlan.isconnected():
    fetch_weather()
    last_fetch_time = time.ticks_ms()

# Cấu hình Server Socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', 80))
server.listen(5)
server.setblocking(False)

print(f"\n[Web Server] Khởi chạy thành công tại: http://{wlan.ifconfig()[0]}")

try:
    while True:
        ensure_wifi()

        # Kiểm tra chu kỳ 30 giây để cập nhật thời tiết
        if time.ticks_diff(time.ticks_ms(), last_fetch_time) >= FETCH_INTERVAL_MS:
            fetch_weather()
            last_fetch_time = time.ticks_ms()

        # Nhận kết nối từ Web Browser
        try:
            conn, addr = server.accept()
        except OSError:
            time.sleep_ms(20)
            continue

        try:
            conn.settimeout(1.0)
            request = conn.recv(1024).decode('utf-8')

            if "GET /?cmd=on" in request:
                led.value(1)
                led_status = "ON"
            elif "GET /?cmd=off" in request:
                led.value(0)
                led_status = "OFF"

            response = html_template()
            conn.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\nConnection: close\r\n\r\n')
            conn.sendall(response)
        except Exception as e:
            print("Lỗi xử lý client:", e)
        finally:
            conn.close()

except KeyboardInterrupt:
    server.close()
    print("Hệ thống đã dừng.")