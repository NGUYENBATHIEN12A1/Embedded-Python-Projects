from machine import Pin, SPI
import time

# Khởi tạo Hardware SPI (MOSI = GPIO23, SCK = GPIO18, CS = GPIO22)
spi = SPI(2, baudrate=1000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(23))
cs = Pin(22, Pin.OUT)

def send_command(address, data):
    cs.value(0)
    spi.write(bytearray([address, data]))
    cs.value(1)

def clear_matrix():
    send_command(0x09, 0x00) # Tắt BCD Decode
    for r in range(1, 9):
        send_command(r, 0x00)

def init_max7219():
    send_command(0x09, 0x00) # No decode
    send_command(0x0B, 0x07) # Scan limit 8 rows
    send_command(0x0A, 0x03) # Độ sáng vừa phải (3/15)
    send_command(0x0C, 0x01) # Bật màn hình
    send_command(0x0F, 0x00) # Display test OFF
    clear_matrix()

def display_frame(frame):
    for i in range(8):
        # FIX: Gửi dữ liệu theo thứ tự ngược lại (8 - i) để lật chữ lộn lại
        send_command(8 - i, frame[i])

# --- Dữ liệu Font chữ và số (Mỗi ký tự rộng 5 cột + 1 cột trống) ---
FONT_DICT = {
    '0': [0x3E, 0x51, 0x49, 0x45, 0x3E, 0x00],
    '2': [0x42, 0x61, 0x51, 0x49, 0x46, 0x00],
    '3': [0x21, 0x41, 0x45, 0x4B, 0x31, 0x00],
    '6': [0x3C, 0x4A, 0x49, 0x49, 0x30, 0x00],
    '7': [0x01, 0x71, 0x09, 0x05, 0x03, 0x00],
    'I': [0x00, 0x41, 0x7F, 0x41, 0x00, 0x00],
    'C': [0x3E, 0x41, 0x41, 0x41, 0x22, 0x00],
    'E': [0x7F, 0x49, 0x49, 0x49, 0x41, 0x00],
    ' ': [0x00, 0x00, 0x00, 0x00, 0x00, 0x00] # Khoảng trắng
}

def scroll_string(text, delay_ms=80):
    # Tạo dải dữ liệu nối liền các chữ cái dựa trên chuỗi đầu vào
    buffer = []
    for char in text:
        char_upper = char.upper() # Chuyển thành chữ hoa để dễ map
        if char_upper in FONT_DICT:
            buffer.extend(FONT_DICT[char_upper])
        else:
            buffer.extend([0x00] * 6) # Nếu không có ký tự thì để trống
    
    # Cuộn chữ
    for shift in range(len(buffer) + 8):
        frame = [0] * 8
        for col in range(8):
            buf_idx = shift - 8 + col
            if 0 <= buf_idx < len(buffer):
                frame[col] = buffer[buf_idx]
            else:
                frame[col] = 0x00
        display_frame(frame)
        time.sleep_ms(delay_ms)

# Khởi tạo ma trận
init_max7219()

while True:
    print("Scrolling text: 23IC 23CE076...")
    scroll_string("23IC 23CE076", delay_ms=60)
    time.sleep(1)
