import pyautogui
import keyboard
import time

print("--- TOOL LẤY TỌA ĐỘ CHUYÊN NGHIỆP ---")
print("1. Di chuột đến vị trí cần lấy trên CapCut.")
print("2. Nhấn phím F8 để lưu tọa độ.")
print("3. Nhấn phím ESC để kết thúc và xem danh sách.")
print("-" * 35)

coords_list = []

def save_position():
    x, y = pyautogui.position()
    coords_list.append((x, y))
    print(f"Đã lưu điểm thứ {len(coords_list)}: X={x}, Y={y}")
    # Tránh việc bấm một lần mà nó nhận diện nhiều lần
    time.sleep(0.3)

# Đăng ký phím tắt F8
keyboard.add_hotkey('f8', save_position)

# Chờ cho đến khi nhấn ESC
keyboard.wait('esc')

print("\n--- DANH SÁCH TỌA ĐỘ ĐÃ LẤY ---")
for i, pos in enumerate(coords_list):
    print(f"Nút {i+1}: {pos}")

print("\nGiờ bạn chỉ việc copy các bộ số này vào code chính thôi!")