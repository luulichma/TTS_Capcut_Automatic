"""
Coordinate Tool - Công cụ lấy tọa độ chuột tích hợp
"""
import tkinter as tk
import ttkbootstrap as ttk
import pyautogui
import keyboard
import time
import threading


class CoordinateTool(tk.Toplevel):
    """Popup window cho phép người dùng capture tọa độ bằng hotkey"""

    def __init__(self, parent, on_coordinate_picked=None):
        super().__init__(parent)
        self.title("🎯 Coordinate Picker")
        self.geometry("400x350")
        self.resizable(False, False)
        self.attributes('-topmost', True)

        self.on_coordinate_picked = on_coordinate_picked
        self.coords_list = []
        self.is_capturing = False
        self._hotkey_id = None

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self):
        ttk.Label(self, text="🎯 Tool Lấy Tọa Độ", font=("", 14, "bold")).pack(pady=10)

        info_frame = ttk.Frame(self, padding=10)
        info_frame.pack(fill=tk.X)
        ttk.Label(info_frame, text="1. Nhấn 'Bắt đầu' rồi di chuột đến vị trí cần lấy").pack(anchor=tk.W)
        ttk.Label(info_frame, text="2. Nhấn F8 để lưu tọa độ tại vị trí chuột").pack(anchor=tk.W)
        ttk.Label(info_frame, text="3. Nhấn 'Dừng' hoặc ESC khi hoàn tất").pack(anchor=tk.W)

        # Controls
        ctrl_frame = ttk.Frame(self, padding=5)
        ctrl_frame.pack(fill=tk.X)

        self.start_btn = ttk.Button(ctrl_frame, text="▶️ Bắt đầu", command=self._start_capture, bootstyle="success")
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(ctrl_frame, text="⏹ Dừng", command=self._stop_capture, bootstyle="danger",
                                   state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(ctrl_frame, text="🗑️ Xóa hết", command=self._clear, bootstyle="warning-outline").pack(side=tk.LEFT, padx=5)

        ttk.Button(ctrl_frame, text="✅ Sử dụng", command=self._use_selected, bootstyle="info").pack(side=tk.RIGHT, padx=5)

        # Live position
        self.live_label = ttk.Label(self, text="X: —  Y: —", font=("Consolas", 12))
        self.live_label.pack(pady=5)

        # Coordinates list
        list_frame = ttk.Frame(self, padding=5)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.coords_listbox = tk.Listbox(list_frame, font=("Consolas", 10), height=8)
        self.coords_listbox.pack(fill=tk.BOTH, expand=True)

        # Status
        self.status_label = ttk.Label(self, text="Sẵn sàng", foreground="gray")
        self.status_label.pack(pady=5)

    def _start_capture(self):
        self.is_capturing = True
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.status_label.config(text="🔴 Đang capture... Nhấn F8 để lưu", foreground="red")

        # Start hotkey listener
        self._hotkey_id = keyboard.add_hotkey('f8', self._capture_position)

        # Start live position update
        self._update_live_position()

    def _stop_capture(self):
        self.is_capturing = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.status_label.config(text="✅ Đã dừng capture", foreground="green")

        if self._hotkey_id is not None:
            try:
                keyboard.remove_hotkey(self._hotkey_id)
            except Exception:
                pass
            self._hotkey_id = None

    def _capture_position(self):
        x, y = pyautogui.position()
        self.coords_list.append((x, y))
        idx = len(self.coords_list)
        self.coords_listbox.insert(tk.END, f"  Điểm {idx}:  X={x}, Y={y}")
        self.coords_listbox.see(tk.END)
        time.sleep(0.3)

    def _update_live_position(self):
        if self.is_capturing:
            x, y = pyautogui.position()
            self.live_label.config(text=f"X: {x}  Y: {y}")
            self.after(50, self._update_live_position)

    def _clear(self):
        self.coords_list.clear()
        self.coords_listbox.delete(0, tk.END)

    def _use_selected(self):
        """Trả về tọa độ đã chọn (hoặc tọa độ cuối cùng) cho phần gọi"""
        sel = self.coords_listbox.curselection()
        if sel:
            coord = self.coords_list[sel[0]]
        elif self.coords_list:
            coord = self.coords_list[-1]
        else:
            return

        if self.on_coordinate_picked:
            self.on_coordinate_picked(coord)
        self._on_close()

    def _on_close(self):
        self._stop_capture()
        self.destroy()
