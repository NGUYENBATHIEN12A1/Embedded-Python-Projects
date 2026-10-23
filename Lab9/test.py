import network

# Khởi tạo Wi-Fi ở chế độ Station (STA)[cite: 1]
wlan = network.WLAN(network.STA_IF)
wlan.active(True)

# Lấy địa chỉ MAC gốc (dạng bytes)
mac_bytes = wlan.config('mac')

# Chuyển sang dạng chuỗi Hex dễ đọc (ví dụ: a0:b7:65:29:25:9c)
mac_str = ':'.join(['%02x' % b for b in mac_bytes])

print("1. MAC dạng bytes (dùng cho code ESP-NOW):", mac_bytes)
print("2. MAC dạng chuẩn (dễ nhìn):", mac_str)