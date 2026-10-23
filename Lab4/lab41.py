import network
import urequests
import json
import time

# Thông tin Wi-Fi phòng bạn
SSID = "YOUR_WIFI_SSID"
PASSWORD = "YOUR_WIFI_PASSWORD"

# 1. BƯỚC 1: KẾT NỐI WI-FI VÀ HIỂN THỊ IP
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    
    # Reset card mạng để tránh lỗi OSError
    try:
        wlan.active(False)
        time.sleep(1)
    except Exception:
        pass
        
    wlan.active(True)
    time.sleep(1)
    
    if not wlan.isconnected():
        print(f"Đang kết nối tới mạng {SSID}...")
        wlan.connect(SSID, PASSWORD)
        
        timeout = 15
        while not wlan.isconnected() and timeout > 0:
            print(".", end="")
            time.sleep(1)
            timeout -= 1

    if wlan.isconnected():
        print("\n[Thành công] Đã kết nối Wi-Fi!")
        print("Địa chỉ IP của ESP32:", wlan.ifconfig()[0])
        return True
    else:
        print("\n[Thất bại] Không thể kết nối Wi-Fi.")
        return False

# 2. BƯỚC 2: GỬI HTTP GET LẤY DỮ LIỆU THỜI TIẾT
def http_get_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=21.0285&longitude=105.8542&current_weather=true"
    print("\n--- Đang gửi yêu cầu HTTP GET ---")
    
    try:
        res = urequests.get(url)
        print("Mã phản hồi (Status Code):", res.status_code)
        
        if res.status_code == 200:
            data = res.json()
            weather = data.get("current_weather", {})
            print("=> Lấy dữ liệu thành công!")
            print(f"   + Nhiệt độ hiện tại: {weather.get('temperature')} °C")
            print(f"   + Tốc độ gió: {weather.get('windspeed')} km/h")
        else:
            print("Lỗi từ Server!")
        res.close()
    except Exception as e:
        print("Lỗi khi gửi HTTP GET:", e)

# 3. BƯỚC 3: GỬI HTTP POST DỮ LIỆU LÊN SERVER (MỞ RỘNG)
def http_post_data():
    url = "http://httpbin.org/post"
    payload = {"device": "ESP32", "status": "Ready", "lab": 4}
    headers = {'Content-Type': 'application/json'}
    
    print("\n--- Đang gửi yêu cầu HTTP POST ---")
    try:
        res = urequests.post(url, data=json.dumps(payload), headers=headers)
        print("Mã phản hồi (Status Code):", res.status_code)
        
        if res.status_code == 200:
            result = res.json()
            print("=> Server đã nhận dữ liệu JSON:")
            print("   +", result.get("json"))
        res.close()
    except Exception as e:
        print("Lỗi khi gửi HTTP POST:", e)

# CHƯƠNG TRÌNH CHÍNH
if connect_wifi():
    http_get_weather()
    http_post_data()