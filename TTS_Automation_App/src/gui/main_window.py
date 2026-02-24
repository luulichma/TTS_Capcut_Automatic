"""
Main Window - Cửa sổ chính của ứng dụng TTS Automation (Enhanced UX)
"""
import tkinter as tk
from tkinter import messagebox, filedialog
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
from src.utils.notification_manager import NotificationManager
from src.utils.session_manager import SessionManager
from src.utils.export_reporter import ExportReporter

from src.gui.data_panel import DataPanel
from src.gui.capcut_panel import CapCutPanel
from src.gui.api_panel import APIPanel
from src.gui.settings_window import SettingsWindow
from src.gui.error_summary_panel import ErrorSummaryPanel


class MainWindow:
    """Cửa sổ chính của ứng dụng — Enhanced UX"""

    def __init__(self):
        # Initialize core
        self.config = ConfigManager()
        self.data_manager = DataManager()
        self.sequence_engine = SequenceEngine()
        self.api_engine = APIEngine()
        self.logger = AppLogger()
        self.session_manager = SessionManager()
        self.export_reporter = ExportReporter()

        # Build UI
        theme = self.config.get_setting('general.theme', 'darkly')
        self.root = ttk.Window(
            title="🔊 TTS Automation Tool",
            themename=theme,
            size=(1100, 780),
            minsize=(900, 650),
        )
        self.root.place_window_center()

        self._running_thread = None
        self._build_ui()
        self._setup_callbacks()
        self._setup_keyboard_shortcuts()
        self._check_saved_session()

    def _build_ui(self):
        # === Bottom Control Bar (FIXED - pack first with side=BOTTOM) ===
        control_bar = ttk.Frame(self.root, padding=(10, 8))
        control_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Progress - Enhanced with ETA, elapsed, speed
        progress_frame = ttk.Frame(control_bar)
        progress_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 8))

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                            maximum=100, bootstyle="success-striped")
        self.progress_bar.pack(fill=tk.X, expand=True, side=tk.LEFT)

        self.progress_label = ttk.Label(progress_frame, text="0 / 0", width=12, anchor=tk.CENTER)
        self.progress_label.pack(side=tk.RIGHT, padx=(10, 0))

        # Enhanced progress info row
        info_frame = ttk.Frame(control_bar)
        info_frame.pack(fill=tk.X, side=tk.TOP, pady=(0, 5))

        self.current_id_label = ttk.Label(info_frame, text="", foreground="cyan", font=("Consolas", 9))
        self.current_id_label.pack(side=tk.LEFT)

        self.eta_label = ttk.Label(info_frame, text="", foreground="gray", font=("", 9))
        self.eta_label.pack(side=tk.RIGHT)

        self.elapsed_label = ttk.Label(info_frame, text="", foreground="gray", font=("", 9))
        self.elapsed_label.pack(side=tk.RIGHT, padx=15)

        self.speed_label = ttk.Label(info_frame, text="", foreground="gray", font=("", 9))
        self.speed_label.pack(side=tk.RIGHT, padx=15)

        # Buttons
        btn_frame = ttk.Frame(control_bar)
        btn_frame.pack(fill=tk.X)

        self.start_btn = ttk.Button(btn_frame, text="▶️  Bắt đầu (Ctrl+Enter)", command=self._start,
                                    bootstyle="success", width=20)
        self.start_btn.pack(side=tk.LEFT, padx=3)

        self.pause_btn = ttk.Button(btn_frame, text="⏸  Tạm dừng (Space)", command=self._pause,
                                    bootstyle="warning", width=18, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=3)

        self.stop_btn = ttk.Button(btn_frame, text="⏹  Dừng (Esc)", command=self._stop,
                                   bootstyle="danger", width=14, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=3)

        # Extra buttons
        ttk.Separator(btn_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)

        self.error_btn = ttk.Button(btn_frame, text="❌ Lỗi (0)", command=self._show_errors,
                                    bootstyle="outline-danger", width=10, state=tk.DISABLED)
        self.error_btn.pack(side=tk.LEFT, padx=3)

        self.retry_btn = ttk.Button(btn_frame, text="🔄 Retry", command=self._retry_failed,
                                    bootstyle="outline-warning", width=8, state=tk.DISABLED)
        self.retry_btn.pack(side=tk.LEFT, padx=3)

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
        ttk.Label(header, text="v2.0 — Enhanced UX",
                  font=("", 10), foreground="gray").pack(side=tk.LEFT, padx=15)

        # Header buttons - right side
        header_btns = ttk.Frame(header)
        header_btns.pack(side=tk.RIGHT)

        ttk.Button(header_btns, text="⚙️ Cài đặt", command=self._open_settings,
                   bootstyle="outline-secondary", width=10).pack(side=tk.LEFT, padx=3)

        # Profile selector
        ttk.Label(header_btns, text="📋 Profile:").pack(side=tk.LEFT, padx=(10, 3))
        self.profile_var = tk.StringVar(value="(none)")
        self.profile_combo = ttk.Combobox(header_btns, textvariable=self.profile_var,
                                           width=15, state="readonly")
        self.profile_combo.pack(side=tk.LEFT, padx=3)
        self.profile_combo.bind("<<ComboboxSelected>>", self._on_profile_selected)
        self._refresh_profiles()

        ttk.Button(header_btns, text="💾", command=self._save_profile,
                   bootstyle="outline-success", width=3).pack(side=tk.LEFT, padx=2)

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

        self.capcut_panel = CapCutPanel(self.mode_notebook, self.config, self.sequence_engine,
                                         data_manager=self.data_manager)
        self.api_panel = APIPanel(self.mode_notebook, self.config, self.api_engine,
                                   data_manager=self.data_manager)

        self.mode_notebook.add(self.capcut_panel, text="  🖥️ CapCut Automation  ")
        self.mode_notebook.add(self.api_panel, text="  🌐 API Export  ")

        # Right: Log panel
        log_outer = ttk.Frame(bottom_frame)
        log_outer.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False)
        log_outer.config(width=340)

        log_frame = ttk.Labelframe(log_outer, text="📋 Log", bootstyle="dark")
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_frame, wrap=tk.WORD, font=("Consolas", 9),
                                bg="#1a1a2e", fg="#e0e0e0", insertbackground="white",
                                state=tk.DISABLED, width=40, height=15)
        log_vsb = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_vsb.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure log text tags for color-coded entries
        self.log_text.tag_configure("success", foreground="#4caf50")
        self.log_text.tag_configure("error", foreground="#f44336")
        self.log_text.tag_configure("warning", foreground="#ff9800")
        self.log_text.tag_configure("info", foreground="#2196f3")
        self.log_text.tag_configure("skip", foreground="#9e9e9e")

        # Log action buttons
        log_btn_frame = ttk.Frame(log_outer)
        log_btn_frame.pack(fill=tk.X, pady=(3, 0))

        ttk.Button(log_btn_frame, text="🗑 Xóa log", command=self._clear_log,
                   bootstyle="outline-secondary", width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(log_btn_frame, text="📂 Mở output", command=self._open_output_folder,
                   bootstyle="outline-info", width=12).pack(side=tk.RIGHT, padx=2)

    def _on_content_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # ==================== Callbacks ====================

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

                    # Update ETA and speed
                    stats = self.export_reporter.get_statistics()
                    if stats['elapsed_seconds'] > 0:
                        self.elapsed_label.config(
                            text=f"⏱ {self.export_reporter.format_elapsed_time(stats['elapsed_seconds'])}")
                        self.speed_label.config(text=f"⚡ {stats['speed_per_min']} files/min")
                        eta = self.export_reporter.estimate_eta(current, total)
                        self.eta_label.config(text=f"🏁 ETA: {eta}")
            self.root.after(0, update)

        def gui_dialog_start(dialog_index, dialog_id):
            self.root.after(0, lambda: self.current_id_label.config(text=f"📝 {dialog_id}"))

        def gui_batch_complete(success, errors, skipped):
            def update():
                # Notify
                settings = self.config.get_all_settings()
                notif_settings = settings.get('notifications', {})
                NotificationManager.notify_completion(
                    "TTS Automation",
                    success, errors,
                    sound_enabled=notif_settings.get('sound_on_complete', True),
                    toast_enabled=notif_settings.get('windows_notification', True),
                )

                # Update error button
                if errors > 0:
                    self.error_btn.config(text=f"❌ Lỗi ({errors})", state=tk.NORMAL)
                    self.retry_btn.config(state=tk.NORMAL)
            self.root.after(0, update)

        # Sequence engine callbacks
        self.sequence_engine.callbacks = {
            'on_log': gui_log,
            'on_progress': gui_progress,
            'on_dialog_start': gui_dialog_start,
            'on_batch_complete': gui_batch_complete,
        }

        # API engine callbacks
        self.api_engine.callbacks = {
            'on_log': gui_log,
            'on_progress': gui_progress,
            'on_start': lambda did: gui_dialog_start(0, did),
            'on_batch_complete': gui_batch_complete,
        }

        # Logger to GUI
        self.logger.set_gui_callback(lambda msg: self.root.after(0, self._append_log, msg))

    # ==================== Keyboard Shortcuts ====================

    def _setup_keyboard_shortcuts(self):
        """Setup global keyboard shortcuts"""
        self.root.bind("<Control-Return>", lambda e: self._start())
        self.root.bind("<Control-l>", lambda e: self._focus_load())
        self.root.bind("<space>", self._on_space_key)
        self.root.bind("<Escape>", lambda e: self._stop())

    def _focus_load(self):
        """Focus to data source entry"""
        self.data_panel.source_entry.focus_set()

    def _on_space_key(self, event):
        """Space = pause/resume khi đang chạy"""
        # Chỉ xử lý khi đang chạy và focus không trong text entry
        if self.sequence_engine.is_running or self.api_engine.is_running:
            focus = self.root.focus_get()
            if not isinstance(focus, (tk.Entry, ttk.Entry, tk.Text)):
                self._pause()
                return "break"

    # ==================== Log ====================

    def _append_log(self, message):
        """Thêm message vào log widget — color-coded"""
        self.log_text.config(state=tk.NORMAL)

        # Determine tag
        tag = None
        if "✅" in message or "thành công" in message.lower():
            tag = "success"
        elif "❌" in message or "lỗi" in message.lower():
            tag = "error"
        elif "⚠️" in message:
            tag = "warning"
        elif "⏭️" in message or "bỏ qua" in message.lower():
            tag = "skip"
        elif "🚀" in message or "🏁" in message:
            tag = "info"

        if tag:
            self.log_text.insert(tk.END, message + "\n", tag)
        else:
            self.log_text.insert(tk.END, message + "\n")

        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _clear_log(self):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _open_output_folder(self):
        """Mở thư mục output"""
        mode = self.mode_notebook.index(self.mode_notebook.select())
        if mode == 0:
            path = self.capcut_panel.output_dir_var.get()
        else:
            path = self.api_panel.output_dir_var.get()

        if path and os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showinfo("Thông báo", "Thư mục output chưa tồn tại.")

    def _on_data_loaded(self):
        """Callback khi data được load thành công"""
        total = self.data_manager.get_total_rows()
        self._append_log(f"✅ Đã tải {total} dòng dữ liệu")
        # Update level selectors
        self.capcut_panel.set_data_manager(self.data_manager)
        self.api_panel.set_data_manager(self.data_manager)

    # ==================== Settings ====================

    def _open_settings(self):
        SettingsWindow(self.root, self.config, on_settings_changed=self._on_settings_changed)

    def _on_settings_changed(self, new_settings):
        """Handle settings changes"""
        # Apply theme
        theme = new_settings.get('general', {}).get('theme')
        if theme:
            try:
                self.root.style.theme_use(theme)
            except Exception:
                pass

        # Apply retry settings
        retry = new_settings.get('advanced', {}).get('retry_attempts', 2)
        self.sequence_engine.set_retry_attempts(retry)
        self.api_engine.set_retry_attempts(retry)

        # Apply auto backup
        backup = new_settings.get('advanced', {}).get('auto_backup', True)
        self.api_engine.set_auto_backup(backup)

    # ==================== Profiles ====================

    def _refresh_profiles(self):
        profiles = self.config.list_profiles()
        self.profile_combo['values'] = ["(none)"] + profiles

    def _save_profile(self):
        from tkinter import simpledialog
        name = simpledialog.askstring("Lưu Profile", "Tên profile:", parent=self.root)
        if not name:
            return

        # Collect current config
        mode = self.mode_notebook.index(self.mode_notebook.select())
        if mode == 0:
            run_config = self.capcut_panel.get_run_config()
        else:
            run_config = self.api_panel.get_run_config()

        profile_data = {
            'mode': 'capcut' if mode == 0 else 'api',
            'data_source': self.data_panel.source_var.get(),
            'skip_rows': self.data_panel.skip_rows_var.get(),
            'run_config': run_config,
        }

        self.config.save_profile(name, profile_data)
        self._refresh_profiles()
        self.profile_var.set(name)
        self._append_log(f"💾 Profile '{name}' đã được lưu")

    def _on_profile_selected(self, event=None):
        name = self.profile_var.get()
        if name == "(none)":
            return

        profile = self.config.load_profile(name)
        if not profile:
            return

        # Apply profile
        if profile.get('data_source'):
            self.data_panel.source_var.set(profile['data_source'])
        if profile.get('skip_rows') is not None:
            self.data_panel.skip_rows_var.set(profile['skip_rows'])

        # Switch mode tab
        if profile.get('mode') == 'api':
            self.mode_notebook.select(1)
        else:
            self.mode_notebook.select(0)

        self._append_log(f"📋 Profile '{name}' đã được tải")

    # ==================== Session ====================

    def _check_saved_session(self):
        """Kiểm tra và cung cấp option resume session"""
        if self.session_manager.has_saved_session():
            info = self.session_manager.get_session_info()
            if info and info['remaining'] > 0:
                resume = messagebox.askyesno(
                    "Phiên trước chưa hoàn tất",
                    f"Phát hiện session chưa hoàn tất:\n"
                    f"  • Mode: {info['mode']}\n"
                    f"  • Đã xong: {info['completed']}/{info['total']}\n"
                    f"  • Còn lại: {info['remaining']}\n"
                    f"  • Thời gian: {info['timestamp']}\n\n"
                    f"Bạn có muốn tiếp tục không?"
                )
                if not resume:
                    self.session_manager.clear_session()

    def _save_current_session(self, mode, completed_indices, total, config):
        """Lưu session hiện tại"""
        self.session_manager.save_session({
            'mode': mode,
            'completed_indices': completed_indices,
            'total': total,
            'config': config,
        })

    # ==================== Errors ====================

    def _show_errors(self):
        """Show error summary panel"""
        mode = self.mode_notebook.index(self.mode_notebook.select())
        if mode == 0:
            failed = self.sequence_engine.failed_items
        else:
            failed = self.api_engine.failed_items

        if not failed:
            messagebox.showinfo("Không có lỗi", "✅ Không có items bị lỗi!")
            return

        ErrorSummaryPanel(
            self.root, failed,
            on_retry=self._retry_failed,
        )

    def _retry_failed(self):
        """Retry failed items"""
        mode = self.mode_notebook.index(self.mode_notebook.select())
        if mode == 0:
            if not self.sequence_engine.failed_items:
                return
            config = self.capcut_panel.get_run_config()
            self._set_running_state(True)
            self._append_log("🔄 Retrying failed items...")

            def run():
                try:
                    self.sequence_engine.retry_failed(config['output_dir'])
                except Exception as e:
                    self.root.after(0, self._append_log, f"❌ Lỗi retry: {e}")
                finally:
                    self.root.after(0, self._set_running_state, False)

            threading.Thread(target=run, daemon=True).start()
        else:
            if not self.api_engine.failed_items:
                return
            config = self.api_panel.get_run_config()
            self._set_running_state(True)
            self._append_log("🔄 Retrying failed items...")

            def run():
                try:
                    self.api_engine.retry_failed(config['output_dir'], voice=config.get('voice_id'))
                except Exception as e:
                    self.root.after(0, self._append_log, f"❌ Lỗi retry: {e}")
                finally:
                    self.root.after(0, self._set_running_state, False)

            threading.Thread(target=run, daemon=True).start()

    # ==================== Control Methods ====================

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

        key_col_idx = self.data_panel.get_key_column_index()
        lang_cols = self.data_panel.get_selected_language_columns()

        if not lang_cols:
            messagebox.showwarning("Chưa chọn ngôn ngữ", "Vui lòng gán ngôn ngữ cho ít nhất 1 cột!")
            return

        # Get selected language from CapCut panel
        selected_language = config.get('language', 'English')
        
        # Find the column index for the selected language
        text_col_idx = None
        for col_idx, lang_name in lang_cols.items():
            if lang_name == selected_language:
                text_col_idx = col_idx
                break
        
        # Fallback to first language if selected one not found
        if text_col_idx is None:
            text_col_idx = list(lang_cols.keys())[0]
            selected_language = lang_cols[text_col_idx]

        lang_name = selected_language
        key_col = self.data_manager.column_names[key_col_idx]
        text_col = self.data_manager.column_names[text_col_idx]

        # Apply settings
        self.sequence_engine.load_template(config['template'])
        self.sequence_engine.set_timing_preset(config.get('timing_preset', 'normal'))
        self.sequence_engine.set_dry_run(config.get('dry_run', False))
        retry = self.config.get_setting('advanced.retry_attempts', 2)
        self.sequence_engine.set_retry_attempts(retry)

        # Check session resume
        levels = config['levels']
        resume_from = None
        if self.session_manager.has_saved_session():
            session = self.session_manager.load_session()
            if session and session.get('mode') == 'capcut':
                resume_from = set(session.get('completed_indices', []))

        self._set_running_state(True)
        self.export_reporter.start_tracking()
        self._append_log(f"🚀 Bắt đầu CapCut Automation — {lang_name}")

        if config.get('dry_run'):
            self._append_log("🔍 DRY RUN MODE — không thực thi thật")

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

                # Determine levels to process
                if levels is None:
                    # All levels - get from data
                    all_data = self.data_manager.filter_by_levels(key_col_idx, None)
                    rows = all_data.to_dict('records')
                    export_dir = os.path.join(config['output_dir'], lang_name.lower()[:2])
                    os.makedirs(export_dir, exist_ok=True)
                    self.sequence_engine.run_batch(rows, key_col, text_col, export_dir, resume_from=resume_from)
                else:
                    for lv in levels:
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
                        self.sequence_engine.run_batch(rows, key_col, text_col, export_dir, resume_from=resume_from)

                # Save session
                self._save_current_session('capcut',
                    self.sequence_engine.completed_indices,
                    self.data_manager.get_total_rows(), config)

                self.export_reporter.stop_tracking()
                stats = self.export_reporter.get_statistics()
                self.root.after(0, self._append_log,
                    f"🎉 Hoàn tất! ⏱ {self.export_reporter.format_elapsed_time(stats['elapsed_seconds'])}")

                # Clear session if fully done
                if not self.sequence_engine.failed_items:
                    self.session_manager.clear_session()

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
        self.api_engine.set_auto_backup(config.get('auto_backup', False))
        retry = self.config.get_setting('advanced.retry_attempts', 2)
        self.api_engine.set_retry_attempts(retry)

        # Check session resume
        levels = config['levels']
        resume_from = None
        if self.session_manager.has_saved_session():
            session = self.session_manager.load_session()
            if session and session.get('mode') == 'api':
                resume_from = set(session.get('completed_indices', []))

        self._set_running_state(True)
        self.export_reporter.start_tracking()
        self._append_log(f"🚀 Bắt đầu API Export — {lang_name} — {config['voice_id']}")

        def run():
            try:
                if levels is None:
                    # All levels
                    all_data = self.data_manager.filter_by_levels(key_col_idx, None)
                    rows = all_data.to_dict('records')
                    export_dir = os.path.join(config['output_dir'], lang_name.lower()[:2])
                    os.makedirs(export_dir, exist_ok=True)
                    self.api_engine.export_batch(rows, key_col, text_col, export_dir,
                                                 voice=config['voice_id'], resume_from=resume_from)
                else:
                    for lv in levels:
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
                                                     voice=config['voice_id'], resume_from=resume_from)

                # Save session
                self._save_current_session('api',
                    self.api_engine.completed_indices,
                    self.data_manager.get_total_rows(), config)

                self.export_reporter.stop_tracking()

                # Generate manifest
                output_dir = config['output_dir']
                if output_dir:
                    try:
                        manifest_path = os.path.join(output_dir, 'manifest.json')
                        self.export_reporter.generate_manifest(manifest_path)
                        self.root.after(0, self._append_log, f"📄 Manifest: {manifest_path}")
                    except Exception:
                        pass

                stats = self.export_reporter.get_statistics()
                self.root.after(0, self._append_log,
                    f"🎉 API Export hoàn tất! ⏱ {self.export_reporter.format_elapsed_time(stats['elapsed_seconds'])}")

                # Clear session if fully done
                if not self.api_engine.failed_items:
                    self.session_manager.clear_session()

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
        if not (self.sequence_engine.is_running or self.api_engine.is_running):
            return
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn dừng?\nSession sẽ được lưu để tiếp tục sau."):
            self.sequence_engine.stop()
            self.api_engine.stop()
            self._set_running_state(False)

    def _set_running_state(self, is_running):
        """Cập nhật trạng thái UI khi bắt đầu/kết thúc chạy"""
        if is_running:
            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
            self.error_btn.config(state=tk.DISABLED, text="❌ Lỗi (0)")
            self.retry_btn.config(state=tk.DISABLED)
            self.status_label.config(text="▶️ Đang chạy...", foreground="green")
        else:
            self.start_btn.config(state=tk.NORMAL)
            self.pause_btn.config(state=tk.DISABLED, text="⏸  Tạm dừng")
            self.stop_btn.config(state=tk.DISABLED)
            self.status_label.config(text="⏳ Sẵn sàng", foreground="gray")
            self.progress_var.set(0)
            self.current_id_label.config(text="")
            self.eta_label.config(text="")
            self.elapsed_label.config(text="")
            self.speed_label.config(text="")

    def run(self):
        """Start the application"""
        self.root.mainloop()
