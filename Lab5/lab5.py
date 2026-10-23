import usocket as socket
import network
from machine import Pin
import dht
import esp
import gc
import time

esp.osdebug(None)
gc.collect()

# ================= 1. CẤU HÌNH WIFI =================
# Thay đổi SSID và Mật khẩu WiFi của bạn tại đây
SSID = 'YOUR_WIFI_SSID'
PASSWORD = 'YOUR_WIFI_PASSWORD'

# Kết nối WiFi
station = network.WLAN(network.STA_IF)
station.active(True)
station.connect(SSID, PASSWORD)

print('Đang kết nối WiFi...')
while not station.isconnected():
    time.sleep(0.5)

ip_address = station.ifconfig()[0]
print('-----------------------------------------')
print('Kết nối WiFi thành công!')
print(f'Mở trình duyệt truy cập IP: http://{ip_address}')
print('-----------------------------------------')

# ================= 2. CẤU HÌNH CẢM BIẾN DHT11 =================
# Cảm biến DHT11 nối chân Out (Data) vào GPIO14 (D5 trên ESP8266)
sensor = dht.DHT11(Pin(14))

def read_sensor():
    """Hàm đọc giá trị nhiệt độ và độ ẩm từ DHT11"""
    try:
        sensor.measure()
        temp = sensor.temperature()
        hum = sensor.humidity()
        return temp, hum
    except OSError as e:
        print("Lỗi đọc cảm biến:", e)
        return 0, 0

# ================= 3. GIAO DIỆN WEB (HTML + CHART.JS) =================
def web_page():
    html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>ESP MicroPython - Giám Sát DHT11</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: Arial, sans-serif; text-align: center; background: #f4f4f9; padding: 20px; margin: 0; }
        .chart-box { width: 90%; max-width: 800px; margin: 20px auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
        h2 { color: #333; }
    </style>
</head>
<body>
    <h2>Hệ Thống Giám Sát Nhiệt Độ & Độ Ẩm Realtime</h2>
    <div class="chart-box">
        <canvas id="dhtChart"></canvas>
    </div>

    <script>
        const ctx = document.getElementById('dhtChart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    { label: 'Nhiệt độ (°C)', borderColor: '#ff6384', backgroundColor: '#ff6384', data: [], fill: false, tension: 0.3 },
                    { label: 'Độ ẩm (%)', borderColor: '#36a2eb', backgroundColor: '#36a2eb', data: [], fill: false, tension: 0.3 }
                ]
            },
            options: { 
                responsive: true,
                scales: { y: { beginAtZero: false } } 
            }
        });

        function updateData() {
            fetch('/data')
                .then(response => response.json())
                .then(data => {
                    const now = new Date().toLocaleTimeString();
                    if (chart.data.labels.length >= 10) {
                        chart.data.labels.shift();
                        chart.data.datasets[0].data.shift();
                        chart.data.datasets[1].data.shift();
                    }
                    chart.data.labels.push(now);
                    chart.data.datasets[0].data.push(data.temperature);
                    chart.data.datasets[1].data.push(data.humidity);
                    chart.update();
                });
        }

        // Tự động cập nhật dữ liệu mỗi 5 giây (5000ms)
        setInterval(updateData, 5000);
        updateData();
    </script>
</body>
</html>"""
    return html

# ================= 4. KHỞI CHẠY WEB SERVER =================
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
    try:
        conn, addr = s.accept()
        request = conn.recv(1024).decode('utf-8')
        
        # Endpoint cung cấp dữ liệu JSON cho biểu đồ đường
        if 'GET /data ' in request:
            temp, hum = read_sensor()
            response = '{"temperature": ' + str(temp) + ', "humidity": ' + str(hum) + '}'
            conn.send('HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n\r\n')
            conn.sendall(response)
        # Endpoint tải giao diện trang Web chính
        else:
            response = web_page()
            conn.send('HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n')
            conn.sendall(response)
            
        conn.close()
    except Exception as e:
        pass