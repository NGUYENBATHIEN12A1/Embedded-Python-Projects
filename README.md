# 🐍 Ex_Embedded-_Python

![Python](https://img.shields.io/badge/Python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![MicroPython](https://img.shields.io/badge/MicroPython-2B2728?style=for-the-badge&logo=python&logoColor=white)
![ESP32](https://img.shields.io/badge/ESP32-E7352C?style=for-the-badge&logo=espressif&logoColor=white)
![HTML/CSS](https://img.shields.io/badge/HTML5_&_CSS3-E34F26?style=for-the-badge&logo=html5&logoColor=white)

Repository tổng hợp các bài thực hành môn **Embedded Python**.

---

## 📚 Labs (Danh sách bài thực hành)

### Lab 1: OOP
Thực hành lập trình hướng đối tượng (Object-Oriented Programming) bằng Python.
* **Nội dung kiến thức:**
  * Class và Object
  * Constructor
  * Attribute và Method
  * Inheritance (Kế thừa)
  * Encapsulation (Đóng gói)

### Lab 2: LED Matrix
Điều khiển LED Matrix bằng Python/MicroPython thông qua giao tiếp SPI.
* **Chức năng hiển thị:**
  * Cuộn chữ hiển thị thông tin Lớp (VD: `23IC`)
  * Cuộn chữ hiển thị Mã sinh viên (VD: `23CE076`)
* **Thiết bị sử dụng:**
  * Vi điều khiển (ESP32)
  * Module LED Matrix 8x8 (sử dụng IC MAX7219)
* **Kiến thức sử dụng:** `GPIO`, `Hardware SPI`, `MAX7219 Register Control`, `Hexadecimal Font Mapping`, `String Scrolling Algorithm`.

### Lab 3: Interrupt, Timer, PWM & RGB LED
Thực hành điều khiển LED bằng Interrupt, Hardware Timer và PWM trên MicroPython.
* **Chức năng chính:**
  * Sử dụng nút nhấn để chuyển đổi giữa 3 chế độ (Mode).
  * **Mode 1:** LED đơn nhấp nháy sử dụng Hardware Timer.
  * **Mode 2:** Điều khiển độ sáng LED bằng PWM với hiệu ứng Fading.
  * **Mode 3:** Điều khiển LED RGB chuyển đổi tuần tự nhiều màu.
  * Sử dụng Software Debounce để chống dội nút nhấn.
* **Kiến thức sử dụng:** `GPIO`, `Interrupt`, `Hardware Timer`, `PWM`, `RGB LED`, `Software Debounce`.

### Lab 4: ESP32 IoT Web Server
Xây dựng hệ thống IoT sử dụng ESP32, kết nối Wi-Fi và điều khiển thiết bị thông qua giao diện Web.
* **Chức năng chính:**
  * Kết nối ESP32 với Wi-Fi (Tự động kiểm tra và kết nối lại khi mất mạng).
  * Xây dựng Web Server trên ESP32.
  * Điều khiển LED từ trình duyệt Web.
  * Gửi HTTP Request đến Open-Meteo API để lấy thông tin thời tiết: **Nhiệt độ**, **Độ ẩm**, **Tốc độ gió**.
  * Hiển thị địa chỉ IP và trạng thái Wi-Fi trên Web.
  * Tự động cập nhật dữ liệu thời tiết mỗi 30 giây.
* **Kiến thức sử dụng:** `ESP32`, `Wi-Fi`, `HTTP`, `Socket`, `REST API`, `JSON`, `HTML/CSS`, `Web Server`.

### Lab 5: DHT11 Web Monitoring
Xây dựng hệ thống giám sát nhiệt độ và độ ẩm realtime sử dụng ESP8266 và cảm biến DHT11.
* **Chức năng chính:**
  * Kết nối ESP8266 với Wi-Fi.
  * Đọc nhiệt độ và độ ẩm từ cảm biến DHT11 (Chân kết nối: `DHT11 DATA` → `GPIO14`).
  * Xây dựng Web Server trên ESP8266.
  * Cung cấp dữ liệu cảm biến thông qua HTTP Endpoint `/data` dưới dạng JSON.
  * Hiển thị nhiệt độ và độ ẩm trên biểu đồ realtime bằng Chart.js.
  * Tự động cập nhật dữ liệu mỗi 5 giây.
* **Kiến thức sử dụng:** `ESP8266`, `DHT11`, `Wi-Fi`, `HTTP`, `Socket`, `JSON`, `HTML/CSS`, `JavaScript`, `Chart.js`.

### Lab 6: ESP32 OpenWeatherMap Station
Xây dựng trạm thời tiết thông minh trên ESP32, cho phép tra cứu trạng thái thời tiết của nhiều thành phố trên thế giới thông qua giao diện Web.
* **Chức năng chính:**
  * Kết nối ESP32 với Wi-Fi mạng cục bộ.
  * Xây dựng giao diện Web Server bằng HTML/CSS với Form Dropdown cho phép chọn các thành phố (Huế, Hà Nội, TP.HCM, Tokyo, London, New York).
  * Gửi HTTP GET Request đến OpenWeatherMap API để lấy thông tin thời tiết (Nhiệt độ, Nhiệt độ cảm nhận, Độ ẩm, Sức gió, Mô tả thời tiết).
  * Parse (phân tích) dữ liệu JSON trả về từ API và hiển thị trực quan lên Web.
  * Tối ưu hóa và giải phóng bộ nhớ RAM liên tục cho ESP32 bằng thư viện `gc` (Garbage Collector) để tránh treo thiết bị.
* **Kiến thức sử dụng:** `ESP32`, `Wi-Fi`, `Socket`, `REST API`, `JSON`, `urequests`, `Garbage Collection (gc)`, `HTML/CSS`.

---

## 🛠️ Technologies (Công nghệ & Thiết bị)

- **Ngôn ngữ & Nền tảng:** Python, MicroPython, HTML/CSS, JavaScript.
- **Phần cứng (Embedded Systems):** ESP32, ESP8266, Module LED Matrix 8x8 (MAX7219), RGB LED, DHT11.
- **Giao thức & Kỹ thuật vi điều khiển:** GPIO, SPI, PWM, Interrupt, Hardware Timer.
- **Mạng & API:** Wi-Fi, HTTP, REST API, Socket, JSON.
- **Thư viện bên thứ 3:** Chart.js, Open-Meteo API.

---

## 📂 Repository Structure

```text
Ex_Embedded-_Python/
│
├── Lab1/
│   └── OOP/
│
├── Lab2/
│   └── LED_Matrix/
│
├── Lab3/
│   └── Interrupt_Timer_PWM_RGB/
│
├── Lab4/
│   └── ESP32_IoT_WebServer/
│
├── Lab5/
│   └── ESP8266_DHT11/
│
├── Lab6/
│   └── ESP32_OpenWeatherMap/
|
└── README.md
