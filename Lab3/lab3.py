from machine import Pin, PWM, Timer
import utime

# ==================== CẤU HÌNH PHẦN CỨNG ====================
# Nút nhấn cấu hình ngắt cạnh xuống với điện trở kéo lên nội
BUTTON_PIN = 4
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)

# Chân LED đơn
LED_PIN = 18
single_led = Pin(LED_PIN, Pin.OUT)
pwm_led = None

# Chân RGB LED (Common Cathode)
red_pwm = PWM(Pin(19), freq=1000)
green_pwm = PWM(Pin(5), freq=1000)
blue_pwm = PWM(Pin(2), freq=1000)

# Khởi tạo Hardware Timer
timer = Timer(0)

# Biến trạng thái hệ thống
current_mode = 1
last_interrupt_time = 0
mode_changed = True

# ==================== CÁC HÀM HỖ TRỢ HIỆU ỨNG ====================
def set_rgb_duty(r_duty, g_duty, b_duty):
    """Cập nhật duty cycle (0 - 1023) cho 3 kênh LED RGB."""
    red_pwm.duty(r_duty)
    green_pwm.duty(g_duty)
    blue_pwm.duty(b_duty)

def reset_all_outputs():
    """Tắt toàn bộ LED và giải phóng/tái lập ngoại vi khi đổi Mode."""
    global timer, pwm_led, single_led
    
    # Dừng Timer nếu đang chạy
    timer.deinit()
    
    # Huỷ cấu hình PWM của LED đơn nếu tồn tại
    if pwm_led is not None:
        pwm_led.deinit()
        pwm_led = None
        single_led = Pin(LED_PIN, Pin.OUT)
        
    single_led.value(0)
    set_rgb_duty(0, 0, 0)

# ==================== CALLBACKS VÀ ISR ====================
def timer_blink_callback(t):
    """Callback cho Mode 1: Đảo trạng thái LED đơn."""
    single_led.value(not single_led.value())

def button_isr(pin):
    """Interrupt Service Routine: Chuyển mode kèm Software Debounce."""
    global current_mode, last_interrupt_time, mode_changed
    
    current_time = utime.ticks_ms()
    # Chống dội phím bằng ngưỡng thời gian 250ms
    if utime.ticks_diff(current_time, last_interrupt_time) > 250:
        current_mode = (current_mode % 3) + 1
        mode_changed = True
        last_interrupt_time = current_time

# Gắn ngắt ngoài vào chân nút nhấn
button.irq(trigger=Pin.IRQ_FALLING, handler=button_isr)

# ==================== VÒNG LẶP CHÍNH ====================
fade_val = 0
fade_step = 15
rgb_step = 0

print("System Started. Initializing Mode 1...")

while True:
    # Xử lý khi có sự kiện đổi Mode từ ngắt ngoài
    if mode_changed:
        reset_all_outputs()
        mode_changed = False
        
        if current_mode == 1:
            print("Current Mode: 1 - Blinking LED (Hardware Timer)")
            timer.init(period=1000, mode=Timer.PERIODIC, callback=timer_blink_callback)
            
        elif current_mode == 2:
            print("Current Mode: 2 - PWM Brightness Control (Fading)")
            pwm_led = PWM(Pin(LED_PIN), freq=1000)
            fade_val = 0
            fade_step = 15
            
        elif current_mode == 3:
            print("Current Mode: 3 - RGB Color Cycle (PWM)")
            rgb_step = 0

    # Thực thi các tác vụ theo chế độ hiện tại
    if current_mode == 1:
        # Tác vụ chớp LED được Timer xử lý ngầm trong phần cứng
        utime.sleep_ms(50)

    elif current_mode == 2:
        # Fading LED đơn qua PWM từ 0 -> 1023 -> 0
        if pwm_led is not None:
            pwm_led.duty(fade_val)
            fade_val += fade_step
            if fade_val >= 1023:
                fade_val = 1023
                fade_step = -fade_step
            elif fade_val <= 0:
                fade_val = 0
                fade_step = -fade_step
        utime.sleep_ms(20)

    elif current_mode == 3:
        # Tuần tự chuyển màu LED RGB (Đỏ -> Xanh lá -> Xanh dương -> Vàng -> Tím -> Cyan)
        colors = [
            (1023, 0, 0),      # Đỏ
            (0, 1023, 0),      # Xanh lá
            (0, 0, 1023),      # Xanh dương
            (1023, 1023, 0),   # Vàng
            (1023, 0, 1023),   # Tím
            (0, 1023, 1023)    # Cyan
        ]
        r, g, b = colors[rgb_step]
        set_rgb_duty(r, g, b)
        
        # Kiểm tra theo từng chu kỳ ngắn để nút bấm phản hồi tức thì
        for _ in range(50):
            if mode_changed:
                break
            utime.sleep_ms(20)
            
        rgb_step = (rgb_step + 1) % len(colors)
