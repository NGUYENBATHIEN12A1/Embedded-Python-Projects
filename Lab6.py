# import necessary libraries
import time
import socket

try:
    import urequests as requests
except:
    import requests

try:
    import ujson as json
except:
    import json

import network
import esp
esp.osdebug(None)
import gc
gc.collect()

# Điền thông tin mạng Wi-Fi của bạn
ssid = 'Xom nha la'
password = 'hoivuongdi'

# Thông tin cấu hình API
API_KEY = "8dc336c68d99b90a4d1dea3bb456a7d9"
API_URL = "http://api.openweathermap.org/data/2.5/weather"

CITIES = {
    "Hue": "Hue,VN",
    "Hanoi": "Hanoi,VN",
    "Ho Chi Minh City": "Ho Chi Minh,VN",
    "Tokyo": "Tokyo,JP",
    "London": "London,GB",
    "New York": "New York,US"
}

# 1. Hàm tạo giao diện HTML (Web Page)
def web_page(city, temp, feels_like, humidity, wind, desc):
    html = f"""<!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>ESP32 Weather Station</title>
        <style>
            body {{ background-color: #8fa0c0; color: white; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .card {{ background-color: rgba(255, 255, 255, 0.15); padding: 2rem; border-radius: 15px; text-align: center; width: 320px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }}
            select {{ width: 100%; padding: 10px; margin: 15px 0; border-radius: 5px; border: none; font-size: 16px; background-color: #f8f9fa; color: #333; }}
            .temp {{ font-size: 3.5rem; font-weight: bold; margin: 15px 0; }}
            .desc {{ font-size: 1.2rem; margin-bottom: 20px; text-transform: capitalize; }}
            .details {{ display: flex; justify-content: space-between; font-size: 0.85rem; background: rgba(0,0,0,0.1); padding: 15px; border-radius: 10px; }}
            h2 {{ margin-top: 0; font-size: 1.5rem; }}
            p {{ margin: 5px 0; color: #e0e0e0; font-size: 0.9rem; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>ESP32 Weather Station</h2>
            <p>OpenWeatherMap Current Weather</p>
            <form action="/" method="GET">
                <select name="city" onchange="this.form.submit()">
                    <option value="Hue" {'selected' if city=='Hue' else ''}>Hue</option>
                    <option value="Hanoi" {'selected' if city=='Hanoi' else ''}>Hanoi</option>
                    <option value="Ho Chi Minh City" {'selected' if city=='Ho Chi Minh City' else ''}>Ho Chi Minh City</option>
                    <option value="Tokyo" {'selected' if city=='Tokyo' else ''}>Tokyo</option>
                    <option value="London" {'selected' if city=='London' else ''}>London</option>
                    <option value="New York" {'selected' if city=='New York' else ''}>New York</option>
                </select>
            </form>
            <h3 style="margin-top: 10px;">{city}</h3>
            <div class="temp">{temp} &deg;C</div>
            <div class="desc">{desc}</div>
            <div class="details">
                <div>Feels Like<br><b>{feels_like} &deg;C</b></div>
                <div>Humidity<br><b>{humidity} %</b></div>
                <div>Wind<br><b>{wind} m/s</b></div>
            </div>
        </div>
    </body>
    </html>"""
    return html

# 2. Thiết lập và kết nối Wi-Fi
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(ssid, password)

print("Đang kết nối Wi-Fi...")
while station.isconnected() == False:
    pass
ip_address = station.ifconfig()[0]
print("Kết nối thành công! Mở trình duyệt và truy cập IP:", ip_address)

# 3. Thiết lập Web Server lắng nghe ở Port 80
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

# 4. Vòng lặp chính xử lý Web Server
while True:
    conn = None
    try:
        # Giải phóng bộ nhớ trước mỗi lần nhận kết nối mới
        if gc.mem_free() < 102000:
            gc.collect()
            
        conn, addr = s.accept()
        print('Có kết nối từ:', addr)
        
        # Đọc dữ liệu request với timeout 3s để tránh bị treo
        conn.settimeout(3.0) 
        request = conn.recv(1024).decode('utf-8')
        
        # Bỏ qua các request rỗng
        if not request:
            continue
            
        # Mặc định là Tokyo
        selected_city = "Tokyo" 
        
        # Tách URL để tìm thành phố người dùng chọn
        if "/?city=" in request:
            try:
                start = request.find("/?city=") + 7
                end = request.find(" ", start)
                raw_city = request[start:end]
                # Xử lý dấu cách bị mã hóa thành dấu + hoặc %20
                selected_city = raw_city.replace("+", " ").replace("%20", " ")
            except Exception as e:
                print("Lỗi phân tích URL:", e)
                
        # Bỏ qua các request tải biểu tượng icon của trình duyệt
        if "favicon.ico" in request:
             conn.send('HTTP/1.1 404 Not Found\r\n\r\n'.encode('utf-8'))
             continue
             
        # Gọi API OpenWeatherMap
        query = CITIES.get(selected_city, "Tokyo,JP")
        
        # Xử lý các thành phố có khoảng trắng (như Ho Chi Minh, New York)
        query_encoded = query.replace(" ", "%20")
        
        # Tạo link API hoàn chỉnh
        url = f"{API_URL}?q={query_encoded}&APPID={API_KEY}&units=metric"
        
        temp = feels_like = humidity = wind = 0
        desc = "No data"
        
        try:
            print(f"Đang lấy dữ liệu thời tiết cho {selected_city}...")
            response = requests.get(url)
            weather_data = response.json()
            response.close() # Rất quan trọng, phải đóng response để tiết kiệm RAM
            
            if weather_data.get("cod") == 200:
                main_data = weather_data.get("main")
                temp = main_data.get('temp')
                feels_like = main_data.get('feels_like')
                humidity = main_data.get('humidity')
                wind = weather_data.get("wind").get('speed')
                desc = weather_data.get("weather")[0].get('description')
                print("-> Lấy dữ liệu thành công!")
            else:
                 print("-> Lỗi API:", weather_data.get("message"))
        except Exception as e:
            print("-> Lỗi kết nối API:", e)

        # Tạo file giao diện HTML
        response_html = web_page(selected_city, temp, feels_like, humidity, wind, desc)
        
        # Trả Header và Content cho trình duyệt
        conn.send('HTTP/1.1 200 OK\r\n'.encode('utf-8'))
        conn.send('Content-Type: text/html; charset=utf-8\r\n'.encode('utf-8'))
        conn.send('Connection: close\r\n\r\n'.encode('utf-8'))
        
        # Gửi toàn bộ trang HTML đi
        conn.sendall(response_html.encode('utf-8'))
        
    except OSError as e:
        print('Lỗi Socket:', e)
    except Exception as e:
        print('Lỗi:', e)
    finally:
        # BẮT BUỘC: Luôn đóng kết nối
        if conn:
            conn.close()
            print("Đã ngắt kết nối client.\n")
