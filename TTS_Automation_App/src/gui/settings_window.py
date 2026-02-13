"""
Settings Window - Cửa sổ cài đặt ứng dụng
"""
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk


class SettingsWindow(tk.Toplevel):
    """Cửa sổ cài đặt ứng dụng với nhiều tab"""

    AVAILABLE_THEMES = [
        'darkly', 'superhero', 'cyborg', 'solar',  # Dark themes
        'cosmo', 'flatly', 'litera', 'minty', 'journal',  # Light themes
    ]

    def __init__(self, parent, config_manager, on_settings_changed=None):
        super().__init__(parent)
        self.title("⚙️ Cài đặt")
        self.geometry("520x480")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.config_manager = config_manager
        self.on_settings_changed = on_settings_changed
        self._original_settings = config_manager.get_all_settings()

        self._build_ui()
        self._load_current_settings()

    def _build_ui(self):
        # Notebook (tabs)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        # Tab 1: General
        self._build_general_tab()
        # Tab 2: Performance
        self._build_performance_tab()
        # Tab 3: Notifications
        self._build_notifications_tab()
        # Tab 4: Advanced
        self._build_advanced_tab()

        # Action buttons
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="💾 Lưu", command=self._save, bootstyle="success",
                   width=12).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(btn_frame, text="❌ Hủy", command=self.destroy, bootstyle="secondary",
                   width=12).pack(side=tk.RIGHT)
        ttk.Button(btn_frame, text="🔄 Mặc định", command=self._reset_defaults,
                   bootstyle="warning-outline", width=12).pack(side=tk.LEFT)

    def _build_general_tab(self):
        tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab, text="  🎨 Giao diện  ")

        # Theme
        theme_frame = ttk.Labelframe(tab, text="Theme", bootstyle="info", padding=10)
        theme_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(theme_frame, text="Giao diện:").pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value='darkly')
        theme_combo = ttk.Combobox(theme_frame, textvariable=self.theme_var,
                                   values=self.AVAILABLE_THEMES,
                                   state="readonly", width=20)
        theme_combo.pack(side=tk.LEFT, padx=10)

        # Auto save
        save_frame = ttk.Labelframe(tab, text="Tự động lưu", bootstyle="info", padding=10)
        save_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(save_frame, text="Lưu mỗi (giây):").pack(side=tk.LEFT)
        self.auto_save_var = tk.IntVar(value=300)
        ttk.Spinbox(save_frame, from_=60, to=3600, increment=60,
                    textvariable=self.auto_save_var, width=8).pack(side=tk.LEFT, padx=10)

    def _build_performance_tab(self):
        tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab, text="  ⚡ Hiệu suất  ")

        # Concurrent exports
        conc_frame = ttk.Labelframe(tab, text="API Export", bootstyle="warning", padding=10)
        conc_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(conc_frame, text="Max concurrent exports:").pack(anchor=tk.W)
        self.max_concurrent_var = tk.IntVar(value=3)
        ttk.Scale(conc_frame, from_=1, to=10, variable=self.max_concurrent_var,
                  bootstyle="warning").pack(fill=tk.X, pady=5)
        self.conc_label = ttk.Label(conc_frame, text="3")
        self.conc_label.pack(anchor=tk.E)
        self.max_concurrent_var.trace_add('write', self._update_conc_label)

        # Retry
        retry_frame = ttk.Labelframe(tab, text="Retry khi lỗi", bootstyle="warning", padding=10)
        retry_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(retry_frame, text="Số lần retry:").pack(side=tk.LEFT)
        self.retry_var = tk.IntVar(value=2)
        ttk.Spinbox(retry_frame, from_=0, to=5, textvariable=self.retry_var,
                    width=5).pack(side=tk.LEFT, padx=10)
        ttk.Label(retry_frame, text="(0 = không retry)", foreground="gray").pack(side=tk.LEFT)

    def _build_notifications_tab(self):
        tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab, text="  🔔 Thông báo  ")

        notif_frame = ttk.Labelframe(tab, text="Khi hoàn tất batch", bootstyle="info", padding=10)
        notif_frame.pack(fill=tk.X, pady=(0, 10))

        self.sound_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(notif_frame, text="🔊 Phát âm thanh khi hoàn tất",
                        variable=self.sound_var, bootstyle="round-toggle").pack(anchor=tk.W, pady=3)

        self.toast_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(notif_frame, text="📱 Hiện thông báo Windows",
                        variable=self.toast_var, bootstyle="round-toggle").pack(anchor=tk.W, pady=3)

        # Error handling
        error_frame = ttk.Labelframe(tab, text="Xử lý lỗi", bootstyle="danger", padding=10)
        error_frame.pack(fill=tk.X, pady=(0, 10))

        self.error_popup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(error_frame, text="💬 Hiện popup khi có lỗi",
                        variable=self.error_popup_var, bootstyle="round-toggle").pack(anchor=tk.W, pady=3)

    def _build_advanced_tab(self):
        tab = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(tab, text="  🔧 Nâng cao  ")

        # Debug
        debug_frame = ttk.Labelframe(tab, text="Debug", bootstyle="secondary", padding=10)
        debug_frame.pack(fill=tk.X, pady=(0, 10))

        self.debug_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(debug_frame, text="🐛 Chế độ Debug (log chi tiết)",
                        variable=self.debug_var, bootstyle="round-toggle").pack(anchor=tk.W, pady=3)

        ttk.Label(debug_frame, text="Log level:").pack(side=tk.LEFT, pady=(10, 0))
        self.log_level_var = tk.StringVar(value='INFO')
        ttk.Combobox(debug_frame, textvariable=self.log_level_var,
                     values=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                     state="readonly", width=12).pack(side=tk.LEFT, padx=10, pady=(10, 0))

        # Backup
        backup_frame = ttk.Labelframe(tab, text="Backup", bootstyle="secondary", padding=10)
        backup_frame.pack(fill=tk.X, pady=(0, 10))

        self.backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(backup_frame, text="💾 Tự động backup file trước khi overwrite",
                        variable=self.backup_var, bootstyle="round-toggle").pack(anchor=tk.W, pady=3)

    def _update_conc_label(self, *args):
        try:
            self.conc_label.config(text=str(int(self.max_concurrent_var.get())))
        except Exception:
            pass

    def _load_current_settings(self):
        """Load settings hiện tại vào UI"""
        s = self.config_manager.get_all_settings()

        self.theme_var.set(s.get('general', {}).get('theme', 'darkly'))
        self.auto_save_var.set(s.get('general', {}).get('auto_save_interval', 300))
        self.max_concurrent_var.set(s.get('performance', {}).get('max_concurrent_exports', 3))
        self.retry_var.set(s.get('advanced', {}).get('retry_attempts', 2))
        self.sound_var.set(s.get('notifications', {}).get('sound_on_complete', True))
        self.toast_var.set(s.get('notifications', {}).get('windows_notification', True))
        self.error_popup_var.set(s.get('notifications', {}).get('error_popup', True))
        self.debug_var.set(s.get('advanced', {}).get('debug_mode', False))
        self.log_level_var.set(s.get('advanced', {}).get('log_level', 'INFO'))
        self.backup_var.set(s.get('advanced', {}).get('auto_backup', True))

    def _save(self):
        """Lưu settings"""
        new_settings = {
            'general': {
                'theme': self.theme_var.get(),
                'auto_save_interval': self.auto_save_var.get(),
            },
            'performance': {
                'max_concurrent_exports': int(self.max_concurrent_var.get()),
            },
            'notifications': {
                'sound_on_complete': self.sound_var.get(),
                'windows_notification': self.toast_var.get(),
                'error_popup': self.error_popup_var.get(),
            },
            'advanced': {
                'debug_mode': self.debug_var.get(),
                'log_level': self.log_level_var.get(),
                'auto_backup': self.backup_var.get(),
                'retry_attempts': self.retry_var.get(),
            },
        }

        self.config_manager.update_settings(new_settings)
        self.config_manager.save()

        if self.on_settings_changed:
            self.on_settings_changed(new_settings)

        messagebox.showinfo("Đã lưu", "✅ Cài đặt đã được lưu!", parent=self)
        self.destroy()

    def _reset_defaults(self):
        """Reset về mặc định"""
        if messagebox.askyesno("Xác nhận", "Khôi phục tất cả cài đặt về mặc định?", parent=self):
            from src.core.config_manager import DEFAULT_SETTINGS
            for section, defaults in DEFAULT_SETTINGS.items():
                for key, value in defaults.items():
                    self.config_manager.set_setting(f"{section}.{key}", value)
            self._load_current_settings()
