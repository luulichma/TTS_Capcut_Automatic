"""
Error Summary Panel - Hiển thị tóm tắt lỗi và cho phép retry
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
import csv
import os


class ErrorSummaryPanel(tk.Toplevel):
    """Popup hiển thị danh sách items bị lỗi"""

    def __init__(self, parent, failed_items, on_retry=None, on_retry_selected=None):
        """
        failed_items: list of dicts {index, dialog_id, text, error?}
        on_retry: callback khi retry all
        on_retry_selected: callback(selected_items) khi retry selected
        """
        super().__init__(parent)
        self.title("❌ Danh sách lỗi")
        self.geometry("650x450")
        self.transient(parent)

        self.failed_items = failed_items or []
        self.on_retry = on_retry
        self.on_retry_selected = on_retry_selected

        self._build_ui()
        self._populate()

    def _build_ui(self):
        # Header
        header = ttk.Frame(self, padding=10)
        header.pack(fill=tk.X)

        ttk.Label(header, text="❌ Items bị lỗi", font=("", 13, "bold")).pack(side=tk.LEFT)
        self.count_label = ttk.Label(header, text="0 items", foreground="gray")
        self.count_label.pack(side=tk.RIGHT)

        # Treeview
        tree_frame = ttk.Frame(self, padding=(10, 0))
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("dialog_id", "error")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings",
                                 selectmode="extended", height=12)
        self.tree.heading("dialog_id", text="Dialog ID")
        self.tree.heading("error", text="Lỗi")
        self.tree.column("dialog_id", width=200)
        self.tree.column("error", width=400)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Action buttons
        btn_frame = ttk.Frame(self, padding=10)
        btn_frame.pack(fill=tk.X)

        ttk.Button(btn_frame, text="🔄 Retry Tất cả", command=self._retry_all,
                   bootstyle="warning", width=15).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="🔄 Retry Đã chọn", command=self._retry_selected,
                   bootstyle="outline-warning", width=15).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="📄 Export CSV", command=self._export_csv,
                   bootstyle="outline-info", width=12).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(btn_frame, text="Đóng", command=self.destroy,
                   bootstyle="secondary", width=8).pack(side=tk.RIGHT)

    def _populate(self):
        """Điền dữ liệu vào tree"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for item in self.failed_items:
            self.tree.insert("", tk.END, values=(
                item.get('dialog_id', 'N/A'),
                item.get('error', 'Unknown error'),
            ))

        self.count_label.config(text=f"{len(self.failed_items)} items")

    def _retry_all(self):
        if self.on_retry:
            if messagebox.askyesno("Xác nhận", f"Retry {len(self.failed_items)} items?", parent=self):
                self.on_retry()
                self.destroy()

    def _retry_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Hãy chọn items để retry", parent=self)
            return

        if self.on_retry_selected:
            selected_indices = [self.tree.index(item) for item in selected]
            selected_items = [self.failed_items[i] for i in selected_indices]
            self.on_retry_selected(selected_items)
            self.destroy()

    def _export_csv(self):
        """Export danh sách lỗi ra CSV"""
        path = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="error_report.csv"
        )
        if not path:
            return

        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=['dialog_id', 'error'])
                writer.writeheader()
                for item in self.failed_items:
                    writer.writerow({
                        'dialog_id': item.get('dialog_id', ''),
                        'error': item.get('error', ''),
                    })
            messagebox.showinfo("Đã lưu", f"✅ Đã xuất {len(self.failed_items)} lỗi ra:\n{path}", parent=self)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu file:\n{e}", parent=self)

    def update_items(self, new_items):
        """Cập nhật danh sách items"""
        self.failed_items = new_items
        self._populate()
