"""
Main Window - Cửa sổ chính của ứng dụng TTS Automation
"""
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import threading
import time
import sys
import os

from src.core.config_manager import ConfigManager
from src.core.data_manager import DataManager
from src.core.sequence_engine import SequenceEngine
from src.core.api_engine import APIEngine
from src.utils.logger import AppLogger

from src.gui.data_panel import DataPanel
from src.gui.capcut_panel import CapCutPanel
from src.gui.api_panel import APIPanel


class MainWindow:
    """Cửa sổ chính của ứng dụng"""

    def __init__(self):
        # Initialize core
        self.config = ConfigManager()
        self.data_manager = DataManager()
        self.sequence_engine = SequenceEngine()
        self.api_engine = APIEngine()
        self.logger = AppLogger()

        # Build UI
        self.root = ttk.Window(
            title="🔊 TTS Automation Tool",
            themename="darkly",
            size=(1100, 780),
            minsize=(900, 650),
        )
        self.root.place_window_center()

        self._running_thread = None
        self._build_ui()
        self._setup_callbacks()

    def _build_ui(self):
        # === Bottom Control Bar (FIXED - pack first with side=BOTTOM) ===
        control_bar = ttk.Frame(self.root, padding=(10, 8))
        control_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Progress
        progress_frame = ttk.Frame(control_bar)
        progress_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 8))

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                            maximum=100, bootstyle="success-striped")
        self.progress_bar.pack(fill=tk.X, expand=True, side=tk.LEFT)

        self.progress_label = ttk.Label(progress_frame, text="0 / 0", width=12, anchor=tk.CENTER)
        self.progress_label.pack(side=tk.RIGHT, padx=(10, 0))

        # Buttons
        btn_frame = ttk.Frame(control_bar)
        btn_frame.pack(fill=tk.X)

        self.start_btn = ttk.Button(btn_frame, text="▶️  Bắt đầu", command=self._start,
                                    bootstyle="success", width=14)
        self.start_btn.pack(side=tk.LEFT, padx=3)

        self.pause_btn = ttk.Button(btn_frame, text="⏸  Tạm dừng", command=self._pause,
                                    bootstyle="warning", width=14, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=3)

        self.stop_btn = ttk.Button(btn_frame, text="⏹  Dừng", command=self._stop,
                                   bootstyle="danger", width=14, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=3)

        # Status
        self.status_label = ttk.Label(btn_frame, text="⏳ Sẵn sàng", foreground="gray")
        self.status_label.pack(side=tk.RIGHT, padx=10)

        # Separator
        ttk.Separator(self.root, orient=tk.HORIZONTAL).pack(fill=tk.X, side=tk.BOTTOM)

        # === Scrollable Content Area ===
        scroll_container = ttk.Frame(self.root)
        scroll_container.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(scroll_container, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(scroll_container, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Inner frame for all content
        self.content_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        # Bind resize events
        self.content_frame.bind("<Configure>", self._on_content_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # Mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # === Header ===
        header = ttk.Frame(self.content_frame, padding=(15, 10))
        header.pack(fill=tk.X)

        ttk.Label(header, text="🔊 TTS Automation Tool", font=("", 18, "bold")).pack(side=tk.LEFT)
        ttk.Label(header, text="v1.0 — CapCut Automation & API Export",
                  font=("", 10), foreground="gray").pack(side=tk.LEFT, padx=15)

        # === Data Panel ===
        self.data_panel = DataPanel(self.content_frame, self.data_manager, on_data_loaded=self._on_data_loaded)
        self.data_panel.pack(fill=tk.X, padx=10, pady=(0, 5))

        # === Bottom area: Mode tabs (left) + Log (right) ===
        bottom_frame = ttk.Frame(self.content_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))

        # Left: Mode tabs
        mode_frame = ttk.Frame(bottom_frame)
        mode_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.mode_notebook = ttk.Notebook(mode_frame, bootstyle="dark")
        self.mode_notebook.pack(fill=tk.BOTH, expand=True)

        self.capcut_panel = CapCutPanel(self.mode_notebook, self.config, self.sequence_engine)
        self.api_panel = APIPanel(self.mode_notebook, self.config, self.api_engine)

        self.mode_notebook.add(self.capcut_panel, text="  🖥️ CapCut Automation  ")
        self.mode_notebook.add(self.api_panel, text="  🌐 API Export  ")

        # Right: Log panel
        log_frame = ttk.Labelframe(bottom_frame, text="📋 Log", bootstyle="dark")
        log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        log_frame.config(width=320)

        self.log_text = tk.Text(log_frame, wrap=tk.WORD, font=("Consolas", 9),
                                bg="#1a1a2e", fg="#e0e0e0", insertbackground="white",
                                state=tk.DISABLED, width=38, height=15)
        log_vsb = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_vsb.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_vsb.pack(side=tk.RIGHT, fill=tk.Y)

    def _on_content_configure(self, event):
        """Cập nhật scroll region khi nội dung thay đổi kích thước"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Đảm bảo content frame luôn rộng bằng canvas"""
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        """Cuộn bằng chuột"""
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _setup_callbacks(self):
        """Kết nối callbacks từ engine lên GUI"""

        def gui_log(msg):
            self.root.after(0, self._append_log, msg)

        def gui_progress(current, total):
            def update():
                if total > 0:
                    pct = (current / total) * 100
                    self.progress_var.set(pct)
                    self.progress_label.config(text=f"{current} / {total}")
            self.root.after(0, update)

        # Sequence engine callbacks
        self.sequence_engine.callbacks = {
            'on_log': gui_log,
            'on_progress': gui_progress,
        }

        # API engine callbacks
        self.api_engine.callbacks = {
            'on_log': gui_log,
            'on_progress': gui_progress,
        }

        # Logger to GUI
        self.logger.set_gui_callback(lambda msg: self.root.after(0, self._append_log, msg))

    def _append_log(self, message):
        """Thêm message vào log widget"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _on_data_loaded(self):
        """Callback khi data được load thành công"""
        total = self.data_manager.get_total_rows()
        self._append_log(f"✅ Đã tải {total} dòng dữ liệu")

    # --- Control Methods ---

    def _start(self):
        """Bắt đầu chạy automation"""
        if self.data_manager.df is None:
            messagebox.showwarning("Chưa có dữ liệu", "Vui lòng tải dữ liệu trước!")
            return

        current_mode = self.mode_notebook.index(self.mode_notebook.select())

        if current_mode == 0:
            self._start_capcut_mode()
        else:
            self._start_api_mode()

    def _start_capcut_mode(self):
        """Chạy CapCut automation mode"""
        config = self.capcut_panel.get_run_config()

        if not config['template']['steps']:
            messagebox.showwarning("Thiếu template", "Vui lòng tạo hoặc load một template!")
            return

        # Get data config
        key_col_idx = self.data_panel.get_key_column_index()
        lang_cols = self.data_panel.get_selected_language_columns()

        if not lang_cols:
            messagebox.showwarning("Chưa chọn ngôn ngữ", "Vui lòng gán ngôn ngữ cho ít nhất 1 cột!")
            return

        # Use first language column
        text_col_idx = list(lang_cols.keys())[0]
        lang_name = lang_cols[text_col_idx]

        key_col = self.data_manager.column_names[key_col_idx]
        text_col = self.data_manager.column_names[text_col_idx]

        # Load template
        self.sequence_engine.load_template(config['template'])

        self._set_running_state(True)
        self._append_log(f"🚀 Bắt đầu CapCut Automation — {lang_name}")

        def run():
            try:
                # Countdown
                countdown = config['countdown']
                for i in range(countdown, 0, -1):
                    if not self.sequence_engine._check_controls():
                        break
                    self.root.after(0, self._append_log, f"🔥 Bắt đầu trong {i} giây...")
                    try:
                        if sys.platform == "win32":
                            import winsound
                            winsound.Beep(1000, 200)
                    except Exception:
                        pass
                    time.sleep(1)

                for lv in range(config['level_start'], config['level_end']):
                    if not self.sequence_engine._check_controls():
                        break

                    self.root.after(0, self._append_log, f"\n{'='*40}\n🏁 LEVEL {lv}\n{'='*40}")

                    export_dir = os.path.join(config['output_dir'], f"Level_{lv}",
                                              lang_name.lower()[:2])
                    os.makedirs(export_dir, exist_ok=True)

                    level_data = self.data_manager.filter_by_level(key_col_idx, lv)
                    if level_data.empty:
                        self.root.after(0, self._append_log, f"⚠️ Level {lv} trống, bỏ qua...")
                        continue

                    rows = level_data.to_dict('records')
                    self.sequence_engine.run_batch(rows, key_col, text_col, export_dir)

                self.root.after(0, self._append_log, "🎉 Hoàn tất toàn bộ!")
            except Exception as e:
                self.root.after(0, self._append_log, f"❌ Lỗi: {e}")
            finally:
                self.root.after(0, self._set_running_state, False)

        self._running_thread = threading.Thread(target=run, daemon=True)
        self._running_thread.start()

    def _start_api_mode(self):
        """Chạy API export mode"""
        config = self.api_panel.get_run_config()

        if not config['voice_id']:
            messagebox.showwarning("Chưa chọn giọng", "Vui lòng chọn giọng đọc!")
            return

        key_col_idx = self.data_panel.get_key_column_index()
        lang_cols = self.data_panel.get_selected_language_columns()

        if not lang_cols:
            messagebox.showwarning("Chưa chọn ngôn ngữ", "Vui lòng gán ngôn ngữ cho ít nhất 1 cột!")
            return

        text_col_idx = list(lang_cols.keys())[0]
        lang_name = lang_cols[text_col_idx]

        key_col = self.data_manager.column_names[key_col_idx]
        text_col = self.data_manager.column_names[text_col_idx]

        self.api_engine.set_voice(config['voice_id'])
        self.api_engine.set_format(config['format'])

        self._set_running_state(True)
        self._append_log(f"🚀 Bắt đầu API Export — {lang_name} — {config['voice_id']}")

        def run():
            try:
                for lv in range(config['level_start'], config['level_end']):
                    if self.api_engine._stop_event.is_set():
                        break

                    subfolder = config['subfolder_pattern'].format(
                        level=lv, lang=lang_name.lower()[:2]
                    )
                    export_dir = os.path.join(config['output_dir'], subfolder)
                    os.makedirs(export_dir, exist_ok=True)

                    self.root.after(0, self._append_log, f"\n🏁 LEVEL {lv} → {export_dir}")

                    level_data = self.data_manager.filter_by_level(key_col_idx, lv)
                    if level_data.empty:
                        self.root.after(0, self._append_log, f"⚠️ Level {lv} trống")
                        continue

                    rows = level_data.to_dict('records')
                    self.api_engine.export_batch(rows, key_col, text_col, export_dir,
                                                 voice=config['voice_id'])

                self.root.after(0, self._append_log, "🎉 API Export hoàn tất!")
            except Exception as e:
                self.root.after(0, self._append_log, f"❌ Lỗi: {e}")
            finally:
                self.root.after(0, self._set_running_state, False)

        self._running_thread = threading.Thread(target=run, daemon=True)
        self._running_thread.start()

    def _pause(self):
        """Toggle pause/resume"""
        if self.sequence_engine.is_paused:
            self.sequence_engine.resume()
            self.pause_btn.config(text="⏸  Tạm dừng")
            self.status_label.config(text="▶️ Đang chạy...", foreground="green")
        else:
            self.sequence_engine.pause()
            self.pause_btn.config(text="▶️  Tiếp tục")
            self.status_label.config(text="⏸ Đã tạm dừng", foreground="orange")

    def _stop(self):
        """Dừng hoàn toàn"""
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn dừng?"):
            self.sequence_engine.stop()
            self.api_engine.stop()
            self._set_running_state(False)

    def _set_running_state(self, is_running):
        """Cập nhật trạng thái UI khi bắt đầu/kết thúc chạy"""
        if is_running:
            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_label.config(text="▶️ Đang chạy...", foreground="green")
        else:
            self.start_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED, text="⏸  Tạm dừng")
            self.stop_btn.config(state=tk.DISABLED)
            self.status_label.config(text="⏳ Sẵn sàng", foreground="gray")
            self.progress_var.set(0)

    def run(self):
        """Start the application"""
        self.root.mainloop()
