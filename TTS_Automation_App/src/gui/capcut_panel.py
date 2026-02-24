"""
CapCut Panel - Sequence Editor và Runner cho CapCut Automation
"""
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import ttkbootstrap as ttk
import json
import os
import threading

from src.gui.coordinate_tool import CoordinateTool
from src.gui.level_selector import LevelSelector


class CapCutPanel(ttk.Frame):
    """Panel chỉnh sửa và chạy chuỗi tương tác CapCut — enhanced UX"""

    ACTION_TYPES = ['click', 'double_click', 'key', 'hotkey', 'paste_text', 'type_text', 'wait']
    TEMPLATE_VARS = ['{{CURRENT_TEXT}}', '{{DIALOG_ID}}', '{{EXPORT_DIR}}', '{{LEVEL}}']

    def __init__(self, parent, config_manager, sequence_engine, data_manager=None):
        super().__init__(parent, padding=10)
        self.config_manager = config_manager
        self.engine = sequence_engine
        self.data_manager = data_manager
        self.current_template = None
        self.steps = []
        self._editing_step_index = None
        self._build_ui()
        self._load_default_template()

    def _build_ui(self):
        # === Top: Template controls ===
        tpl_frame = ttk.Labelframe(self, text="📋 Template", bootstyle="info")
        tpl_frame.pack(fill=tk.X, pady=(0, 5))

        tpl_row = ttk.Frame(tpl_frame)
        tpl_row.pack(fill=tk.X)

        ttk.Label(tpl_row, text="Template:").pack(side=tk.LEFT)
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(tpl_row, textvariable=self.template_var, state="readonly", width=30)
        self.template_combo.pack(side=tk.LEFT, padx=5)
        self.template_combo.bind("<<ComboboxSelected>>", self._on_template_selected)
        self._refresh_template_list()

        ttk.Button(tpl_row, text="📂 Load", command=self._load_template_file, bootstyle="outline", width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(tpl_row, text="💾 Save", command=self._save_template, bootstyle="outline-success", width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(tpl_row, text="📝 Save As", command=self._save_template_as, bootstyle="outline-warning", width=8).pack(side=tk.LEFT, padx=2)

        # Undo/Redo (Template Editor)
        ttk.Separator(tpl_row, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=5)
        self.undo_btn = ttk.Button(tpl_row, text="↩️", command=self._undo, bootstyle="outline-secondary", width=3)
        self.undo_btn.pack(side=tk.LEFT, padx=1)
        self.redo_btn = ttk.Button(tpl_row, text="↪️", command=self._redo, bootstyle="outline-secondary", width=3)
        self.redo_btn.pack(side=tk.LEFT, padx=1)

        # === Timing & Mode Options ===
        options_frame = ttk.Frame(self)
        options_frame.pack(fill=tk.X, pady=(0, 5))

        # Timing preset
        ttk.Label(options_frame, text="⏱️ Tốc độ:").pack(side=tk.LEFT)
        self.timing_var = tk.StringVar(value='normal')
        for preset in ['slow', 'normal', 'fast']:
            label = {'slow': '🐌 Slow', 'normal': '⚡ Normal', 'fast': '🚀 Fast'}[preset]
            ttk.Radiobutton(options_frame, text=label, variable=self.timing_var,
                           value=preset, command=self._on_timing_changed).pack(side=tk.LEFT, padx=5)

        ttk.Separator(options_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)

        # Dry-run toggle
        self.dry_run_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="🔍 Dry Run (mô phỏng, không thực thi)",
                        variable=self.dry_run_var, command=self._on_dry_run_changed,
                        bootstyle="round-toggle-warning").pack(side=tk.LEFT)

        # === Middle: Step Editor ===
        editor_frame = ttk.Labelframe(self, text="🔧 Chuỗi tương tác", bootstyle="primary")
        editor_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        # Steps list
        list_frame = ttk.Frame(editor_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "action", "target", "label", "wait")
        self.steps_tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        self.steps_tree.heading("id", text="#")
        self.steps_tree.heading("action", text="Action")
        self.steps_tree.heading("target", text="Target")
        self.steps_tree.heading("label", text="Mô tả")
        self.steps_tree.heading("wait", text="Wait (s)")

        self.steps_tree.column("id", width=30, minwidth=30)
        self.steps_tree.column("action", width=90, minwidth=70)
        self.steps_tree.column("target", width=120, minwidth=80)
        self.steps_tree.column("label", width=200, minwidth=100)
        self.steps_tree.column("wait", width=60, minwidth=50)

        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.steps_tree.yview)
        self.steps_tree.configure(yscrollcommand=vsb.set)
        self.steps_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.steps_tree.bind("<Double-1>", self._edit_step)

        # Step action buttons
        btn_frame = ttk.Frame(editor_frame)
        btn_frame.pack(fill=tk.X, pady=5)

        ttk.Button(btn_frame, text="➕ Thêm", command=self._add_step, bootstyle="success", width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="✏️ Sửa", command=self._edit_selected, bootstyle="warning", width=7).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="📋 Clone", command=self._clone_step, bootstyle="info", width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🗑️ Xóa", command=self._delete_step, bootstyle="danger", width=7).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="⬆️", command=lambda: self._move_step(-1), width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="⬇️", command=lambda: self._move_step(1), width=3).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🎯 Pick Coords", command=self._pick_coordinate, bootstyle="info", width=12).pack(side=tk.RIGHT, padx=2)

        # === Bottom: Output Config ===
        output_frame = ttk.Labelframe(self, text="📁 Cấu hình xuất", bootstyle="secondary")
        output_frame.pack(fill=tk.X)

        # Language selector
        lang_row = ttk.Frame(output_frame)
        lang_row.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(lang_row, text="🌐 Ngôn ngữ:").pack(side=tk.LEFT)
        self.language_var = tk.StringVar(value="English")
        self.lang_combo = ttk.Combobox(lang_row, textvariable=self.language_var,
                                       values=["English", "Vietnamese", "Japanese", "Korean", "Chinese"],
                                       state="readonly", width=20)
        self.lang_combo.pack(side=tk.LEFT, padx=5)

        out_row = ttk.Frame(output_frame)
        out_row.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(out_row, text="Thư mục gốc:").pack(side=tk.LEFT)
        self.output_dir_var = tk.StringVar(value=self.config_manager.get('general.base_output_path', ''))
        ttk.Entry(out_row, textvariable=self.output_dir_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(out_row, text="📁", command=self._browse_output, width=3, bootstyle="outline").pack(side=tk.LEFT)

        # Level selector widget
        self.level_selector = LevelSelector(output_frame, config_manager=self.config_manager,
                                             data_manager=self.data_manager)
        self.level_selector.pack(fill=tk.X, pady=(5, 0))

        # Countdown
        cd_row = ttk.Frame(output_frame)
        cd_row.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(cd_row, text="⏱️ Đếm ngược:").pack(side=tk.LEFT)
        self.countdown_var = tk.IntVar(value=5)
        ttk.Spinbox(cd_row, from_=1, to=30, textvariable=self.countdown_var, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(cd_row, text="giây").pack(side=tk.LEFT)

    # --- Timing & Dry Run ---

    def _on_timing_changed(self):
        self.engine.set_timing_preset(self.timing_var.get())

    def _on_dry_run_changed(self):
        self.engine.set_dry_run(self.dry_run_var.get())

    # --- Undo/Redo ---

    def _undo(self):
        if self.engine.can_undo():
            self.engine.undo_template()
            if self.engine.template:
                self.steps = self.engine.template.get('steps', [])
                self._refresh_steps_tree()

    def _redo(self):
        if self.engine.can_redo():
            self.engine.redo_template()
            if self.engine.template:
                self.steps = self.engine.template.get('steps', [])
                self._refresh_steps_tree()

    # --- Template Methods ---

    def _refresh_template_list(self):
        templates = self.config_manager.list_templates()
        self.template_combo['values'] = templates

    def _load_default_template(self):
        templates = self.config_manager.list_templates()
        if 'capcut_tts_default.json' in templates:
            self.template_var.set('capcut_tts_default.json')
            self._on_template_selected(None)

    def _on_template_selected(self, event):
        filename = self.template_var.get()
        if filename:
            data = self.config_manager.load_template(filename)
            if data:
                self.current_template = data
                self.steps = data.get('steps', [])
                self._refresh_steps_tree()

    def _load_template_file(self):
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.current_template = data
                self.steps = data.get('steps', [])
                self._refresh_steps_tree()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể load template:\n{e}")

    def _save_template(self):
        filename = self.template_var.get()
        if not filename:
            self._save_template_as()
            return
        self._do_save(filename)

    def _save_template_as(self):
        name = simpledialog.askstring("Lưu Template", "Tên template (không cần .json):")
        if name:
            filename = f"{name}.json" if not name.endswith('.json') else name
            self._do_save(filename)
            self._refresh_template_list()
            self.template_var.set(filename)

    def _do_save(self, filename):
        template_data = {
            "name": os.path.splitext(filename)[0],
            "description": "Custom template",
            "version": "1.0",
            "steps": self.steps
        }
        try:
            self.config_manager.save_template(filename, template_data)
            messagebox.showinfo("Thành công", f"Đã lưu: {filename}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu:\n{e}")

    # --- Step Editor ---

    def _refresh_steps_tree(self):
        self.steps_tree.delete(*self.steps_tree.get_children())
        for i, step in enumerate(self.steps):
            target = step.get('target', '')
            if isinstance(target, list):
                target = f"({target[0]}, {target[1]})"
            source = step.get('source', '')
            if source:
                target = f"{target} ← {source}" if target else source
            self.steps_tree.insert("", tk.END, iid=str(i), values=(
                step.get('id', i + 1),
                step.get('action', ''),
                target,
                step.get('label', ''),
                step.get('wait_after', 0.5)
            ))

    def _add_step(self):
        dialog = StepEditorDialog(self, title="Thêm bước mới")
        self.wait_window(dialog)
        if dialog.result:
            dialog.result['id'] = len(self.steps) + 1
            self.steps.append(dialog.result)
            self._refresh_steps_tree()

    def _edit_step(self, event=None):
        self._edit_selected()

    def _edit_selected(self):
        sel = self.steps_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        dialog = StepEditorDialog(self, title="Sửa bước", step_data=self.steps[idx])
        self.wait_window(dialog)
        if dialog.result:
            dialog.result['id'] = self.steps[idx].get('id', idx + 1)
            self.steps[idx] = dialog.result
            self._refresh_steps_tree()

    def _clone_step(self):
        """Clone selected step"""
        sel = self.steps_tree.selection()
        if not sel:
            messagebox.showinfo("Thông báo", "Chọn 1 bước để clone")
            return
        idx = int(sel[0])
        import copy
        cloned = copy.deepcopy(self.steps[idx])
        cloned['id'] = len(self.steps) + 1
        cloned['label'] = cloned.get('label', '') + ' (Copy)'
        self.steps.insert(idx + 1, cloned)
        # Re-number
        for i, s in enumerate(self.steps):
            s['id'] = i + 1
        self._refresh_steps_tree()

    def _delete_step(self):
        sel = self.steps_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        if messagebox.askyesno("Xác nhận", f"Xóa bước {idx + 1}?"):
            self.steps.pop(idx)
            for i, s in enumerate(self.steps):
                s['id'] = i + 1
            self._refresh_steps_tree()

    def _move_step(self, direction):
        sel = self.steps_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        new_idx = idx + direction
        if 0 <= new_idx < len(self.steps):
            self.steps[idx], self.steps[new_idx] = self.steps[new_idx], self.steps[idx]
            for i, s in enumerate(self.steps):
                s['id'] = i + 1
            self._refresh_steps_tree()
            self.steps_tree.selection_set(str(new_idx))

    def _pick_coordinate(self):
        """Mở coordinate picker"""
        sel = self.steps_tree.selection()

        def on_picked(coord):
            if sel:
                idx = int(sel[0])
                self.steps[idx]['target'] = list(coord)
                self._refresh_steps_tree()

        CoordinateTool(self, on_coordinate_picked=on_picked)

    def _browse_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir_var.set(path)

    def set_data_manager(self, data_manager):
        """Update data manager reference"""
        self.data_manager = data_manager
        self.level_selector.set_data_manager(data_manager)

    def get_run_config(self):
        """Lấy config để chạy automation"""
        return {
            'template': {"name": "current", "steps": self.steps},
            'output_dir': self.output_dir_var.get(),
            'levels': self.level_selector.get_levels(),
            'countdown': self.countdown_var.get(),
            'timing_preset': self.timing_var.get(),
            'dry_run': self.dry_run_var.get(),
            'language': self.language_var.get(),
        }


class StepEditorDialog(tk.Toplevel):
    """Dialog chỉnh sửa 1 bước trong sequence"""

    ACTION_TYPES = CapCutPanel.ACTION_TYPES

    def __init__(self, parent, title="Step Editor", step_data=None):
        super().__init__(parent)
        self.title(title)
        self.geometry("420x380")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.result = None
        self.step_data = step_data or {}
        self._build_ui()

    def _build_ui(self):
        main = ttk.Frame(self, padding=15)
        main.pack(fill=tk.BOTH, expand=True)

        # Action type
        ttk.Label(main, text="Loại action:").grid(row=0, column=0, sticky=tk.W, pady=3)
        self.action_var = tk.StringVar(value=self.step_data.get('action', 'click'))
        action_combo = ttk.Combobox(main, textvariable=self.action_var, values=self.ACTION_TYPES, state="readonly", width=20)
        action_combo.grid(row=0, column=1, pady=3, sticky=tk.W)
        action_combo.bind("<<ComboboxSelected>>", self._on_action_changed)

        # Target
        ttk.Label(main, text="Target:").grid(row=1, column=0, sticky=tk.W, pady=3)
        target_frame = ttk.Frame(main)
        target_frame.grid(row=1, column=1, sticky=tk.W, pady=3)

        target = self.step_data.get('target', '')

        self.target_x_var = tk.StringVar(value=str(target[0]) if isinstance(target, list) and len(target) > 0 else '')
        self.target_y_var = tk.StringVar(value=str(target[1]) if isinstance(target, list) and len(target) > 1 else '')
        self.target_str_var = tk.StringVar(value=str(target) if not isinstance(target, list) else '')

        ttk.Label(target_frame, text="X:").pack(side=tk.LEFT)
        self.x_entry = ttk.Entry(target_frame, textvariable=self.target_x_var, width=6)
        self.x_entry.pack(side=tk.LEFT, padx=2)
        ttk.Label(target_frame, text="Y:").pack(side=tk.LEFT)
        self.y_entry = ttk.Entry(target_frame, textvariable=self.target_y_var, width=6)
        self.y_entry.pack(side=tk.LEFT, padx=2)

        ttk.Button(target_frame, text="🎯", command=self._pick, width=3, bootstyle="info-outline").pack(side=tk.LEFT, padx=3)

        ttk.Label(main, text="Hoặc phím/text:").grid(row=2, column=0, sticky=tk.W, pady=3)
        ttk.Entry(main, textvariable=self.target_str_var, width=25).grid(row=2, column=1, sticky=tk.W, pady=3)

        # Source (for paste_text)
        ttk.Label(main, text="Source:").grid(row=3, column=0, sticky=tk.W, pady=3)
        self.source_var = tk.StringVar(value=self.step_data.get('source', ''))
        source_combo = ttk.Combobox(main, textvariable=self.source_var, width=25,
                                    values=['{{CURRENT_TEXT}}', '{{DIALOG_ID}}', '{{EXPORT_DIR}}', '{{LEVEL}}'])
        source_combo.grid(row=3, column=1, sticky=tk.W, pady=3)

        # Label
        ttk.Label(main, text="Mô tả:").grid(row=4, column=0, sticky=tk.W, pady=3)
        self.label_var = tk.StringVar(value=self.step_data.get('label', ''))
        ttk.Entry(main, textvariable=self.label_var, width=30).grid(row=4, column=1, sticky=tk.W, pady=3)

        # Wait after
        ttk.Label(main, text="Chờ sau (s):").grid(row=5, column=0, sticky=tk.W, pady=3)
        self.wait_var = tk.DoubleVar(value=self.step_data.get('wait_after', 0.5))
        ttk.Entry(main, textvariable=self.wait_var, width=8).grid(row=5, column=1, sticky=tk.W, pady=3)

        # Description
        ttk.Label(main, text="Ghi chú:").grid(row=6, column=0, sticky=tk.NW, pady=3)
        self.desc_var = tk.StringVar(value=self.step_data.get('description', ''))
        ttk.Entry(main, textvariable=self.desc_var, width=30).grid(row=6, column=1, sticky=tk.W, pady=3)

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=15)
        ttk.Button(btn_frame, text="✅ Lưu", command=self._save, bootstyle="success", width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Hủy", command=self.destroy, bootstyle="danger-outline", width=10).pack(side=tk.LEFT, padx=5)

    def _on_action_changed(self, event=None):
        action = self.action_var.get()
        is_coords = action in ('click', 'double_click')
        state = tk.NORMAL if is_coords else tk.DISABLED
        self.x_entry.config(state=state)
        self.y_entry.config(state=state)

    def _pick(self):
        def on_picked(coord):
            self.target_x_var.set(str(coord[0]))
            self.target_y_var.set(str(coord[1]))
        CoordinateTool(self, on_coordinate_picked=on_picked)

    def _save(self):
        action = self.action_var.get()
        target = None

        if action in ('click', 'double_click'):
            try:
                x = int(self.target_x_var.get())
                y = int(self.target_y_var.get())
                target = [x, y]
            except ValueError:
                messagebox.showwarning("Lỗi", "Tọa độ X, Y phải là số nguyên!")
                return
        else:
            target = self.target_str_var.get() or None

        self.result = {
            'action': action,
            'target': target,
            'label': self.label_var.get(),
            'wait_after': self.wait_var.get(),
            'description': self.desc_var.get(),
        }

        source = self.source_var.get()
        if source:
            self.result['source'] = source

        self.destroy()
