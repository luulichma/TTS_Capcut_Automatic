"""
API Panel - Giao diện cho chế độ xuất trực tiếp qua TTS API
"""
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk

from src.core.api_engine import APIEngine


class APIPanel(ttk.Frame):
    """Panel cấu hình và chạy TTS API export"""

    def __init__(self, parent, config_manager, api_engine):
        super().__init__(parent, padding=10)
        self.config_manager = config_manager
        self.engine = api_engine
        self._build_ui()

    def _build_ui(self):
        # === API Provider ===
        api_frame = ttk.Labelframe(self, text="🔌 API Provider", bootstyle="info")
        api_frame.pack(fill=tk.X, pady=(0, 10))

        row1 = ttk.Frame(api_frame)
        row1.pack(fill=tk.X)

        ttk.Label(row1, text="Provider:").pack(side=tk.LEFT)
        self.provider_var = tk.StringVar(value="Edge TTS (Free)")
        ttk.Combobox(row1, textvariable=self.provider_var,
                     values=["Edge TTS (Free)"],
                     state="readonly", width=25).pack(side=tk.LEFT, padx=5)

        # === Voice Selection ===
        voice_frame = ttk.Labelframe(self, text="🎙️ Giọng đọc", bootstyle="warning")
        voice_frame.pack(fill=tk.X, pady=(0, 10))

        # Language filter
        lang_row = ttk.Frame(voice_frame)
        lang_row.pack(fill=tk.X)

        ttk.Label(lang_row, text="Ngôn ngữ:").pack(side=tk.LEFT)
        self.language_var = tk.StringVar(value="Vietnamese")
        self.lang_combo = ttk.Combobox(lang_row, textvariable=self.language_var,
                                       values=APIEngine.get_all_languages(),
                                       state="readonly", width=20)
        self.lang_combo.pack(side=tk.LEFT, padx=5)
        self.lang_combo.bind("<<ComboboxSelected>>", self._on_language_changed)

        # Voice selector
        voice_row = ttk.Frame(voice_frame)
        voice_row.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(voice_row, text="Giọng:").pack(side=tk.LEFT)
        self.voice_var = tk.StringVar()
        self.voice_combo = ttk.Combobox(voice_row, textvariable=self.voice_var, state="readonly", width=30)
        self.voice_combo.pack(side=tk.LEFT, padx=5)

        ttk.Button(voice_row, text="🔊 Thử", command=self._test_voice, bootstyle="outline-info", width=6).pack(side=tk.LEFT, padx=5)

        self._on_language_changed()  # Populate initial voices

        # === Output Settings ===
        output_frame = ttk.Labelframe(self, text="📁 Cấu hình xuất", bootstyle="secondary")
        output_frame.pack(fill=tk.X, pady=(0, 10))

        # Output dir
        dir_row = ttk.Frame(output_frame)
        dir_row.pack(fill=tk.X)

        ttk.Label(dir_row, text="Thư mục gốc:").pack(side=tk.LEFT)
        self.output_dir_var = tk.StringVar(value=self.config_manager.get('general.base_output_path', ''))
        ttk.Entry(dir_row, textvariable=self.output_dir_var, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(dir_row, text="📁", command=self._browse_output, width=3, bootstyle="outline").pack(side=tk.LEFT)

        # Format
        fmt_row = ttk.Frame(output_frame)
        fmt_row.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(fmt_row, text="Định dạng:").pack(side=tk.LEFT)
        self.format_var = tk.StringVar(value="mp3")
        ttk.Radiobutton(fmt_row, text="MP3", variable=self.format_var, value="mp3").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(fmt_row, text="WAV", variable=self.format_var, value="wav").pack(side=tk.LEFT, padx=10)

        # Level config
        lv_row = ttk.Frame(output_frame)
        lv_row.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(lv_row, text="Level:").pack(side=tk.LEFT)
        self.level_start_var = tk.IntVar(value=self.config_manager.get('levels.start', 8))
        self.level_end_var = tk.IntVar(value=self.config_manager.get('levels.end', 16))
        ttk.Spinbox(lv_row, from_=1, to=100, textvariable=self.level_start_var, width=5).pack(side=tk.LEFT, padx=5)
        ttk.Label(lv_row, text="đến").pack(side=tk.LEFT)
        ttk.Spinbox(lv_row, from_=1, to=100, textvariable=self.level_end_var, width=5).pack(side=tk.LEFT, padx=5)

        # Subfolder pattern
        subfolder_row = ttk.Frame(output_frame)
        subfolder_row.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(subfolder_row, text="Pattern thư mục:").pack(side=tk.LEFT)
        self.subfolder_var = tk.StringVar(value="Level_{level}/{lang}")
        ttk.Entry(subfolder_row, textvariable=self.subfolder_var, width=25).pack(side=tk.LEFT, padx=5)
        ttk.Label(subfolder_row, text="(Dùng {level} và {lang})", foreground="gray").pack(side=tk.LEFT)

        # === Info ===
        info_frame = ttk.Labelframe(self, text="ℹ️ Thông tin", bootstyle="light")
        info_frame.pack(fill=tk.X)

        info_text = (
            "Mode API sẽ gọi trực tiếp Edge TTS (miễn phí) để tạo file audio.\n"
            "• Không cần mở CapCut\n"
            "• Nhanh hơn nhiều so với automation\n"
            "• Chất lượng giọng đọc Neural AI\n"
            "• Hỗ trợ nhiều ngôn ngữ"
        )
        ttk.Label(info_frame, text=info_text, wraplength=400, justify=tk.LEFT, foreground="gray").pack(anchor=tk.W)

    def _on_language_changed(self, event=None):
        lang = self.language_var.get()
        voices = APIEngine.get_voices_for_language(lang)
        display = [f"{name} ({vid})" for vid, name in voices]
        self.voice_combo['values'] = display
        if display:
            self.voice_combo.current(0)

    def _get_selected_voice_id(self):
        """Trả về voice ID được chọn"""
        lang = self.language_var.get()
        voices = APIEngine.get_voices_for_language(lang)
        idx = self.voice_combo.current()
        if 0 <= idx < len(voices):
            return voices[idx][0]
        return None

    def _test_voice(self):
        """Thử phát 1 câu mẫu"""
        voice_id = self._get_selected_voice_id()
        if not voice_id:
            messagebox.showwarning("Chưa chọn giọng", "Hãy chọn giọng đọc trước.")
            return

        import tempfile
        import threading

        test_text = "Xin chào, đây là giọng đọc thử nghiệm." if "vi" in voice_id else "Hello, this is a test voice."

        def do_test():
            try:
                tmp = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                tmp.close()
                self.engine.set_voice(voice_id)
                self.engine.synthesize(test_text, tmp.name, voice_id)

                import os
                os.startfile(tmp.name)
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể phát thử:\n{e}")

        threading.Thread(target=do_test, daemon=True).start()

    def _browse_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir_var.set(path)

    def get_run_config(self):
        """Lấy config để chạy API export"""
        return {
            'voice_id': self._get_selected_voice_id(),
            'language': self.language_var.get(),
            'output_dir': self.output_dir_var.get(),
            'format': self.format_var.get(),
            'level_start': self.level_start_var.get(),
            'level_end': self.level_end_var.get(),
            'subfolder_pattern': self.subfolder_var.get(),
        }
