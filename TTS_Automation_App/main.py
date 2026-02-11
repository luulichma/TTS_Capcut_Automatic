"""
TTS Automation Tool
==================
Ứng dụng tự động hóa Text-to-Speech với 2 chế độ:
- CapCut Automation: Tự động hóa flow TTS trên CapCut Desktop
- API Export: Xuất trực tiếp audio qua Edge TTS (miễn phí)

Sử dụng: python main.py
"""
import sys
import os

# Thêm project root vào path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.gui.main_window import MainWindow


def main():
    try:
        app = MainWindow()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Đã thoát.")
    except Exception as e:
        print(f"❌ Lỗi khởi động: {e}")
        import traceback
        traceback.print_exc()
        input("Nhấn Enter để đóng...")


if __name__ == "__main__":
    main()
