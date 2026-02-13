"""
API Engine - Xuất âm thanh TTS trực tiếp qua Edge TTS (miễn phí)
"""
import asyncio
import os
import threading
import time


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
            - on_batch_complete(success_count, error_count, skipped_count)
        """
        self.callbacks = callbacks or {}
        self.is_running = False
        self._stop_event = threading.Event()
        self.current_voice = "vi-VN-HoaiMyNeural"
        self.output_format = "mp3"

        # Enhanced features
        self.retry_attempts = 2
        self.auto_backup = False
        self.failed_items = []
        self.completed_indices = []
        self.success_count = 0
        self.error_count = 0
        self.skipped_count = 0

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

    def set_retry_attempts(self, attempts):
        """Đặt số lần retry"""
        self.retry_attempts = max(0, int(attempts))

    def set_auto_backup(self, enabled):
        """Bật/tắt auto backup"""
        self.auto_backup = enabled

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

    def _backup_file(self, filepath):
        """Backup file trước khi overwrite"""
        if os.path.exists(filepath) and self.auto_backup:
            backup_path = filepath + '.bak'
            try:
                import shutil
                shutil.copy2(filepath, backup_path)
                return backup_path
            except Exception:
                pass
        return None

    def export_single(self, dialog_id, text, export_dir, voice=None):
        """Export 1 dialog thành file audio"""
        os.makedirs(export_dir, exist_ok=True)
        filename = f"{dialog_id}.{self.output_format}"
        filepath = os.path.join(export_dir, filename)

        # Backup nếu file đã tồn tại
        self._backup_file(filepath)

        self._emit('on_start', dialog_id)
        self._log(f"🔊 Đang tạo: {dialog_id}")

        success = self.synthesize(text, filepath, voice)

        if success:
            self._emit('on_complete', dialog_id, filepath)
            self._log(f"✅ Đã lưu: {filepath}")
        else:
            self._emit('on_error', dialog_id, "Synthesis failed")

        return success

    def _export_with_retry(self, dialog_id, text, export_dir, voice=None):
        """Export 1 dialog với retry logic"""
        for attempt in range(self.retry_attempts + 1):
            if attempt > 0:
                self._log(f"🔄 Retry lần {attempt}/{self.retry_attempts}: {dialog_id}")
                time.sleep(1)

            success = self.export_single(dialog_id, text, export_dir, voice)
            if success:
                return True

            if self._stop_event.is_set():
                return False

        return False

    def export_batch(self, data_rows, key_col, text_col, export_dir,
                     voice=None, resume_from=None):
        """
        Export batch nhiều dialog.
        data_rows: list of dicts
        resume_from: set of indices đã hoàn thành (để resume session)
        """
        self.is_running = True
        self._stop_event.clear()
        self.failed_items = []
        self.completed_indices = list(resume_from) if resume_from else []
        self.success_count = 0
        self.error_count = 0
        self.skipped_count = 0

        total = len(data_rows)

        self._log(f"🚀 Bắt đầu export {total} dialogs qua API...")

        if resume_from:
            self._log(f"📂 Tiếp tục từ session trước ({len(resume_from)} đã xong)")

        for i, row in enumerate(data_rows):
            if self._stop_event.is_set():
                self._log("🛑 Đã dừng bởi người dùng.")
                break

            # Skip nếu đã xử lý (resume mode)
            if resume_from and i in resume_from:
                continue

            dialog_id = str(row[key_col])
            text = str(row[text_col])

            if not text or text.strip() == '' or text == 'nan':
                self._log(f"⏭️ Bỏ qua (trống): {dialog_id}")
                self.skipped_count += 1
                continue

            self._emit('on_progress', i + 1, total)

            if self._export_with_retry(dialog_id, text, export_dir, voice):
                self.success_count += 1
                self.completed_indices.append(i)
            else:
                self.error_count += 1
                self.failed_items.append({
                    'index': i,
                    'dialog_id': dialog_id,
                    'text': text,
                })
                if self._stop_event.is_set():
                    break

        self.is_running = False
        self._log(f"🎉 Hoàn tất! ✅ {self.success_count} thành công, "
                   f"❌ {self.error_count} lỗi, ⏭️ {self.skipped_count} bỏ qua")
        self._emit('on_progress', total, total)
        self._emit('on_batch_complete', self.success_count, self.error_count, self.skipped_count)

        return self.success_count, self.error_count

    def retry_failed(self, export_dir, voice=None):
        """Retry các items bị lỗi"""
        if not self.failed_items:
            self._log("✅ Không có items cần retry")
            return 0, 0

        self.is_running = True
        self._stop_event.clear()

        items_to_retry = list(self.failed_items)
        self.failed_items = []

        total = len(items_to_retry)
        self._log(f"🔄 Retry {total} items bị lỗi...")

        retried_success = 0
        retried_error = 0

        for i, item in enumerate(items_to_retry):
            if self._stop_event.is_set():
                self._log("🛑 Đã dừng bởi người dùng.")
                break

            self._emit('on_progress', i + 1, total)
            success = self.export_single(item['dialog_id'], item['text'], export_dir, voice)

            if success:
                retried_success += 1
                self.success_count += 1
                self.error_count -= 1
                self.completed_indices.append(item['index'])
            else:
                retried_error += 1
                self.failed_items.append(item)

        self.is_running = False
        self._log(f"🔄 Retry hoàn tất! ✅ {retried_success} thành công, ❌ {retried_error} vẫn lỗi")

        return retried_success, retried_error

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
