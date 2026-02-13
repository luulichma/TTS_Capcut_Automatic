"""
Level Selector Widget - Widget chọn level linh hoạt
"""
import tkinter as tk
import ttkbootstrap as ttk


class LevelSelector(ttk.Frame):
    """
    Widget chọn level linh hoạt:
    - All levels
    - Range (start → end)
    - Custom (8,10,12-15,20)

    Gọi on_change callback khi level thay đổi.
    """

    def __init__(self, parent, config_manager=None, data_manager=None,
                 on_change=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.config_manager = config_manager
        self.data_manager = data_manager
        self.on_change = on_change

        self._build_ui()

    def _build_ui(self):
        frame = ttk.Labelframe(self, text="📊 Level Selection", bootstyle="primary", padding=10)
        frame.pack(fill=tk.X)

        # Mode selection
        self.mode_var = tk.StringVar(value='range')
        modes_frame = ttk.Frame(frame)
        modes_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Radiobutton(modes_frame, text="Tất cả", variable=self.mode_var,
                        value='all', command=self._on_mode_changed).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(modes_frame, text="Khoảng", variable=self.mode_var,
                        value='range', command=self._on_mode_changed).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Radiobutton(modes_frame, text="Tùy chọn", variable=self.mode_var,
                        value='custom', command=self._on_mode_changed).pack(side=tk.LEFT)

        # Range input
        self.range_frame = ttk.Frame(frame)
        self.range_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(self.range_frame, text="Từ:").pack(side=tk.LEFT)
        default_start = 8
        default_end = 16
        if self.config_manager:
            default_start = self.config_manager.get('levels.start', 8)
            default_end = self.config_manager.get('levels.end', 16)

        self.start_var = tk.IntVar(value=default_start)
        self.start_spin = ttk.Spinbox(self.range_frame, from_=1, to=999,
                                       textvariable=self.start_var, width=5,
                                       command=self._on_value_changed)
        self.start_spin.pack(side=tk.LEFT, padx=5)
        self.start_spin.bind('<KeyRelease>', lambda e: self._on_value_changed())

        ttk.Label(self.range_frame, text="đến:").pack(side=tk.LEFT)
        self.end_var = tk.IntVar(value=default_end)
        self.end_spin = ttk.Spinbox(self.range_frame, from_=1, to=999,
                                     textvariable=self.end_var, width=5,
                                     command=self._on_value_changed)
        self.end_spin.pack(side=tk.LEFT, padx=5)
        self.end_spin.bind('<KeyRelease>', lambda e: self._on_value_changed())

        # Custom input
        self.custom_frame = ttk.Frame(frame)

        ttk.Label(self.custom_frame, text="Levels:").pack(side=tk.LEFT)
        self.custom_var = tk.StringVar(value="")
        self.custom_entry = ttk.Entry(self.custom_frame, textvariable=self.custom_var, width=25)
        self.custom_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.custom_entry.bind('<KeyRelease>', lambda e: self._on_value_changed())

        ttk.Label(self.custom_frame, text="(VD: 8,10,12-15)",
                  foreground="gray", font=("", 8)).pack(side=tk.LEFT)

        # Info row
        self.info_frame = ttk.Frame(frame)
        self.info_frame.pack(fill=tk.X, pady=(5, 0))

        self.info_label = ttk.Label(self.info_frame, text="📊 —", foreground="gray")
        self.info_label.pack(side=tk.LEFT)

        self.preview_btn = ttk.Button(self.info_frame, text="👁 Preview",
                                       command=self._show_preview,
                                       bootstyle="outline-info", width=10)
        self.preview_btn.pack(side=tk.RIGHT)

        # Preview listbox (hidden by default)
        self.preview_frame = ttk.Frame(frame)
        self.preview_listbox = tk.Listbox(self.preview_frame, height=6,
                                           font=("Consolas", 9))
        self.preview_listbox.pack(fill=tk.BOTH, expand=True)
        self.preview_visible = False

        self._on_mode_changed()

    def _on_mode_changed(self):
        """Khi mode thay đổi"""
        mode = self.mode_var.get()

        # Hide/show frames
        self.range_frame.pack_forget()
        self.custom_frame.pack_forget()

        if mode == 'range':
            self.range_frame.pack(fill=tk.X, pady=(0, 5),
                                  before=self.info_frame)
        elif mode == 'custom':
            self.custom_frame.pack(fill=tk.X, pady=(0, 5),
                                   before=self.info_frame)

        self._on_value_changed()

    def _on_value_changed(self):
        """Khi giá trị level thay đổi"""
        levels = self.get_levels()
        self._update_info(levels)

        if self.on_change:
            self.on_change(levels)

    def get_levels(self):
        """
        Lấy danh sách levels đã chọn.
        Returns: list of int, hoặc None (tất cả)
        """
        from src.core.data_manager import DataManager

        mode = self.mode_var.get()
        if mode == 'all':
            return None
        elif mode == 'range':
            try:
                start = self.start_var.get()
                end = self.end_var.get()
                if start > end:
                    start, end = end, start
                return list(range(start, end + 1))
            except (tk.TclError, ValueError):
                return None
        elif mode == 'custom':
            text = self.custom_var.get()
            return DataManager.parse_level_selection(text)
        return None

    def get_level_string(self):
        """Trả về chuỗi level dạng human-readable"""
        mode = self.mode_var.get()
        if mode == 'all':
            return "all"
        elif mode == 'range':
            try:
                return f"{self.start_var.get()}-{self.end_var.get()}"
            except (tk.TclError, ValueError):
                return ""
        elif mode == 'custom':
            return self.custom_var.get()
        return ""

    def _update_info(self, levels):
        """Cập nhật thông tin số dòng"""
        if not self.data_manager or self.data_manager.df is None:
            self.info_label.config(text="📊 Chưa load dữ liệu")
            return

        try:
            preview = self.data_manager.get_level_preview(levels=levels)
            count = preview['total_count']
            if levels is None:
                self.info_label.config(
                    text=f"📊 Tất cả: {count} dòng sẽ được xử lý",
                    foreground="green" if count > 0 else "red"
                )
            else:
                levels_str = self._format_levels(levels)
                self.info_label.config(
                    text=f"📊 Level {levels_str}: {count} dòng sẽ được xử lý",
                    foreground="green" if count > 0 else "red"
                )
        except Exception:
            self.info_label.config(text="📊 —", foreground="gray")

    def _format_levels(self, levels):
        """Format danh sách levels thành chuỗi ngắn gọn"""
        if not levels:
            return "—"
        if len(levels) <= 5:
            return ", ".join(str(l) for l in levels)
        return f"{levels[0]}-{levels[-1]} ({len(levels)} levels)"

    def _show_preview(self):
        """Toggle preview danh sách dialog IDs"""
        if self.preview_visible:
            self.preview_frame.pack_forget()
            self.preview_visible = False
            self.preview_btn.config(text="👁 Preview")
            return

        if not self.data_manager or self.data_manager.df is None:
            return

        levels = self.get_levels()
        try:
            preview = self.data_manager.get_level_preview(levels=levels, max_items=50)

            self.preview_listbox.delete(0, tk.END)
            for dialog_id in preview['preview_ids']:
                self.preview_listbox.insert(tk.END, f"  {dialog_id}")
            if preview['has_more']:
                self.preview_listbox.insert(tk.END,
                    f"  ... và {preview['total_count'] - len(preview['preview_ids'])} items khác")

            self.preview_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
            self.preview_visible = True
            self.preview_btn.config(text="🔽 Ẩn")
        except Exception:
            pass

    def set_data_manager(self, data_manager):
        """Update data manager reference"""
        self.data_manager = data_manager
        self._on_value_changed()
