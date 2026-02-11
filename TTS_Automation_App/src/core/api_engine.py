"""
API Engine - Xuất âm thanh TTS trực tiếp qua Edge TTS (miễn phí)
"""
import asyncio
import os
import threading


class APIEngine:
    """TTS API Client sử dụng Edge TTS (miễn phí, chất lượng cao)"""

    # Giọng đọc phổ biến
    VOICE_PRESETS = {
        "Vietnamese": [
            ("vi-VN-HoaiMyNeural", "Hoài My (Nữ)"),
            ("vi-VN-NamMinhNeural", "Nam Minh (Nam)"),
        ],
        "English": [
            ("en-US-JennyNeural", "Jenny (Nữ, US)"),
            ("en-US-GuyNeural", "Guy (Nam, US)"),
            ("en-US-AriaNeural", "Aria (Nữ, US)"),
            ("en-GB-SoniaNeural", "Sonia (Nữ, UK)"),
            ("en-GB-RyanNeural", "Ryan (Nam, UK)"),
        ],
        "Japanese": [
            ("ja-JP-NanamiNeural", "Nanami (Nữ)"),
            ("ja-JP-KeitaNeural", "Keita (Nam)"),
        ],
        "Korean": [
            ("ko-KR-SunHiNeural", "Sun-Hi (Nữ)"),
            ("ko-KR-InJoonNeural", "InJoon (Nam)"),
        ],
        "Chinese": [
            ("zh-CN-XiaoxiaoNeural", "Xiaoxiao (Nữ)"),
            ("zh-CN-YunxiNeural", "Yunxi (Nam)"),
        ],
    }

    def __init__(self, callbacks=None):
        """
        callbacks: dict với các key:
            - on_start(dialog_id)
            - on_complete(dialog_id, filepath)
            - on_error(dialog_id, error_msg)
            - on_log(message)
            - on_progress(current, total)
        """
        self.callbacks = callbacks or {}
        self.is_running = False
        self._stop_event = threading.Event()
        self.current_voice = "vi-VN-HoaiMyNeural"
        self.output_format = "mp3"

    def _emit(self, event_name, *args):
        cb = self.callbacks.get(event_name)
        if cb:
            try:
                cb(*args)
            except Exception:
                pass

    def _log(self, msg):
        self._emit('on_log', msg)

    def set_voice(self, voice_id):
        """Set giọng đọc"""
        self.current_voice = voice_id

    def set_format(self, fmt):
        """Set output format (mp3, wav)"""
        self.output_format = fmt

    async def _synthesize_one(self, text, output_path, voice=None):
        """Tổng hợp giọng nói cho 1 đoạn text"""
        try:
            import edge_tts

            voice = voice or self.current_voice
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            return True
        except Exception as e:
            self._log(f"❌ API Error: {e}")
            return False

    def synthesize(self, text, output_path, voice=None):
        """Synchronous wrapper cho _synthesize_one"""
        loop = asyncio.new_event_loop()
        try:
            result = loop.run_until_complete(self._synthesize_one(text, output_path, voice))
            return result
        finally:
            loop.close()

    def export_single(self, dialog_id, text, export_dir, voice=None):
        """Export 1 dialog thành file audio"""
        os.makedirs(export_dir, exist_ok=True)
        filename = f"{dialog_id}.{self.output_format}"
        filepath = os.path.join(export_dir, filename)

        self._emit('on_start', dialog_id)
        self._log(f"🔊 Đang tạo: {dialog_id}")

        success = self.synthesize(text, filepath, voice)

        if success:
            self._emit('on_complete', dialog_id, filepath)
            self._log(f"✅ Đã lưu: {filepath}")
        else:
            self._emit('on_error', dialog_id, "Synthesis failed")

        return success

    def export_batch(self, data_rows, key_col, text_col, export_dir, voice=None):
        """
        Export batch nhiều dialog.
        data_rows: list of dicts
        """
        self.is_running = True
        self._stop_event.clear()

        total = len(data_rows)
        success_count = 0
        error_count = 0

        self._log(f"🚀 Bắt đầu export {total} dialogs qua API...")

        for i, row in enumerate(data_rows):
            if self._stop_event.is_set():
                self._log("🛑 Đã dừng bởi người dùng.")
                break

            dialog_id = str(row[key_col])
            text = str(row[text_col])

            if not text or text.strip() == '' or text == 'nan':
                self._log(f"⏭️ Bỏ qua (trống): {dialog_id}")
                continue

            self._emit('on_progress', i + 1, total)

            if self.export_single(dialog_id, text, export_dir, voice):
                success_count += 1
            else:
                error_count += 1

        self.is_running = False
        self._log(f"🎉 Hoàn tất! ✅ {success_count} thành công, ❌ {error_count} lỗi")
        self._emit('on_progress', total, total)

        return success_count, error_count

    def stop(self):
        """Dừng batch export"""
        self._stop_event.set()
        self.is_running = False

    @classmethod
    def get_voices_for_language(cls, language):
        """Lấy danh sách giọng đọc cho ngôn ngữ"""
        return cls.VOICE_PRESETS.get(language, [])

    @classmethod
    def get_all_languages(cls):
        """Lấy tất cả ngôn ngữ có sẵn"""
        return list(cls.VOICE_PRESETS.keys())

    @classmethod
    async def fetch_all_voices(cls):
        """Lấy toàn bộ danh sách voices từ Edge TTS API"""
        try:
            import edge_tts
            voices = await edge_tts.list_voices()
            return voices
        except Exception:
            return []
