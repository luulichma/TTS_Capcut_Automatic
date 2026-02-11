"""
Data Panel - Panel nhập liệu và preview data
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.tableview import Tableview


class DataPanel(ttk.Frame):
    """Panel quản lý input data và column mapping"""

    def __init__(self, parent, data_manager, on_data_loaded=None):
        super().__init__(parent, padding=10)
        self.data_manager = data_manager
        self.on_data_loaded = on_data_loaded
        self.column_combos = {}
        self._build_ui()

    def _build_ui(self):
        # === Source Input ===
        source_frame = ttk.Labelframe(self, text="📂 Nguồn dữ liệu", bootstyle="info")
        source_frame.pack(fill=tk.X, pady=(0, 5))

        input_row = ttk.Frame(source_frame)
        input_row.pack(fill=tk.X, padx=5, pady=3)

        self.source_var = tk.StringVar()
        ttk.Label(input_row, text="File / URL:").pack(side=tk.LEFT)
        self.source_entry = ttk.Entry(input_row, textvariable=self.source_var, width=50)
        self.source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))

        ttk.Button(input_row, text="📁", command=self._browse_file, width=3, bootstyle="outline").pack(side=tk.LEFT, padx=2)

        # Skip rows + Load button
        skip_row = ttk.Frame(source_frame)
        skip_row.pack(fill=tk.X, padx=5, pady=(0, 5))

        ttk.Label(skip_row, text="Bỏ qua dòng đầu:").pack(side=tk.LEFT)
        self.skip_rows_var = tk.IntVar(value=2)
        ttk.Spinbox(skip_row, from_=0, to=20, textvariable=self.skip_rows_var, width=5).pack(side=tk.LEFT, padx=5)

        ttk.Button(skip_row, text="⬇️ Tải dữ liệu", command=self._load_data, bootstyle="success").pack(side=tk.RIGHT)

        # === Column Mapping (compact horizontal) ===
        self.mapping_frame = ttk.Labelframe(self, text="🔤 Gán ngôn ngữ cho cột", bootstyle="warning")
        self.mapping_frame.pack(fill=tk.X, pady=(0, 5))

        self.mapping_inner = ttk.Frame(self.mapping_frame)
        self.mapping_inner.pack(fill=tk.X, padx=5, pady=3)

        ttk.Label(self.mapping_inner, text="(Tải dữ liệu trước để hiển thị các cột)", foreground="gray").pack()

        # === Data Preview (collapsible, compact) ===
        preview_header = ttk.Frame(self)
        preview_header.pack(fill=tk.X)

        self._preview_visible = tk.BooleanVar(value=False)
        self.toggle_preview_btn = ttk.Checkbutton(
            preview_header, text="👁️ Xem trước dữ liệu", variable=self._preview_visible,
            command=self._toggle_preview, bootstyle="round-toggle"
        )
        self.toggle_preview_btn.pack(side=tk.LEFT)

        self.status_label = ttk.Label(preview_header, text="Chưa có dữ liệu", foreground="gray")
        self.status_label.pack(side=tk.RIGHT, padx=10)

        # Preview container (hidden by default)
        self.preview_container = ttk.Frame(self)
        self.tree_frame = ttk.Frame(self.preview_container)
        self.tree_frame.pack(fill=tk.X, pady=(2, 5))

        self.preview_tree = None

    def _browse_file(self):
        filetypes = [
            ("Excel files", "*.xlsx *.xls"),
            ("CSV files", "*.csv"),
            ("All files", "*.*")
        ]
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            self.source_var.set(path)

    def _load_data(self):
        source = self.source_var.get().strip()
        if not source:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đường dẫn file hoặc URL Google Sheet.")
            return

        try:
            skip_rows = self.skip_rows_var.get()
            self.data_manager.auto_detect_source(source, skip_rows=skip_rows)
            self._update_column_mapping()
            self._update_preview()
            self.status_label.config(
                text=f"✅ Đã tải {self.data_manager.get_total_rows()} dòng | Nguồn: {self.data_manager.source_type}",
                foreground="green"
            )
            if self.on_data_loaded:
                self.on_data_loaded()
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể tải dữ liệu:\n{e}")

    def _update_column_mapping(self):
        """Cập nhật UI column mapping — hiển thị dạng grid ngang"""
        for widget in self.mapping_inner.winfo_children():
            widget.destroy()
        self.column_combos = {}

        columns = self.data_manager.column_names
        languages = ["(Key/ID)", "English", "Vietnamese", "Japanese", "Korean", "Chinese", "French",
                      "German", "Spanish", "Portuguese", "Thai", "Indonesian", "(Bỏ qua)"]

        # Default: col 0 = Key, col 1 = English, col 2 = Vietnamese
        defaults = {0: "(Key/ID)", 1: "English", 2: "Vietnamese"}

        COLS_PER_ROW = 3
        for i, col_name in enumerate(columns):
            r = i // COLS_PER_ROW
            c = i % COLS_PER_ROW

            cell = ttk.Frame(self.mapping_inner)
            cell.grid(row=r, column=c, padx=5, pady=2, sticky=tk.W)

            short_name = col_name[:15] + ".." if len(str(col_name)) > 15 else col_name
            ttk.Label(cell, text=f"C{i}({short_name}):", width=18, anchor=tk.W).pack(side=tk.LEFT)

            combo_var = tk.StringVar(value=defaults.get(i, "(Bỏ qua)"))
            combo = ttk.Combobox(cell, textvariable=combo_var, values=languages, state="readonly", width=14)
            combo.pack(side=tk.LEFT, padx=2)
            self.column_combos[i] = combo_var

            # Auto-set language mapping
            lang = defaults.get(i)
            if lang and lang != "(Key/ID)" and lang != "(Bỏ qua)":
                self.data_manager.set_column_language(i, lang)

            combo_var.trace_add('write', lambda *args, idx=i, var=combo_var: self._on_language_changed(idx, var))

    def _on_language_changed(self, col_index, var):
        lang = var.get()
        if lang not in ("(Key/ID)", "(Bỏ qua)"):
            self.data_manager.set_column_language(col_index, lang)
        elif col_index in self.data_manager.column_language_map:
            del self.data_manager.column_language_map[col_index]

    def _toggle_preview(self):
        """Ẩn/hiện bảng preview"""
        if self._preview_visible.get():
            self.preview_container.pack(fill=tk.X, pady=(0, 5))
        else:
            self.preview_container.pack_forget()

    def _update_preview(self):
        """Cập nhật bảng preview"""
        for widget in self.tree_frame.winfo_children():
            widget.destroy()
        self.preview_tree = None

        headers, rows = self.data_manager.get_preview_data(max_rows=20)
        if not headers:
            return

        # Create Treeview — compact height
        self.preview_tree = ttk.Treeview(self.tree_frame, columns=headers, show="headings", height=5)

        for col in headers:
            self.preview_tree.heading(col, text=col)
            self.preview_tree.column(col, width=120, minwidth=80)

        for row in rows:
            display_row = [str(v)[:50] if v is not None else "" for v in row]
            self.preview_tree.insert("", tk.END, values=display_row)

        # Scrollbars
        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.preview_tree.yview)
        hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.preview_tree.xview)
        self.preview_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        hsb.pack(side=tk.BOTTOM, fill=tk.X)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.preview_tree.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Auto-show preview
        self._preview_visible.set(True)
        self.preview_container.pack(fill=tk.X, pady=(0, 5))

    def get_key_column_index(self):
        """Lấy index của cột Key"""
        for idx, var in self.column_combos.items():
            if var.get() == "(Key/ID)":
                return idx
        return 0

    def get_selected_language_columns(self):
        """Lấy dict {col_index: language_name} cho các cột đã gán"""
        result = {}
        for idx, var in self.column_combos.items():
            lang = var.get()
            if lang not in ("(Key/ID)", "(Bỏ qua)"):
                result[idx] = lang
        return result
