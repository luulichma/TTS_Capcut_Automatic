"""
Sequence Engine - Chạy chuỗi tương tác automation cho CapCut
"""
import pyautogui
import pyperclip
import time
import json
import threading


class SequenceEngine:
    """Engine chạy chuỗi tương tác tự động dựa trên template"""

    SUPPORTED_ACTIONS = ['click', 'double_click', 'key', 'hotkey', 'paste_text', 'type_text', 'wait']

    def __init__(self, callbacks=None):
        """
        callbacks: dict với các key:
            - on_step_start(step_index, step)
            - on_step_complete(step_index, step)
            - on_dialog_start(dialog_index, dialog_id)
            - on_dialog_complete(dialog_index, dialog_id)
            - on_error(step_index, error_msg)
            - on_log(message)
            - on_progress(current, total)
        """
        self.callbacks = callbacks or {}
        self.template = None
        self.is_running = False
        self.is_paused = False
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # Not paused initially

    def load_template(self, template_data):
        """Load template (dict hoặc file path)"""
        if isinstance(template_data, str):
            with open(template_data, 'r', encoding='utf-8') as f:
                self.template = json.load(f)
        else:
            self.template = template_data

    def _emit(self, event_name, *args):
        """Gọi callback nếu có"""
        cb = self.callbacks.get(event_name)
        if cb:
            try:
                cb(*args)
            except Exception:
                pass

    def _log(self, msg):
        self._emit('on_log', msg)

    def _check_controls(self):
        """Kiểm tra pause/stop. Return False nếu cần stop."""
        if self._stop_event.is_set():
            return False
        self._pause_event.wait()  # Block nếu đang pause
        return not self._stop_event.is_set()

    def execute_step(self, step, context=None):
        """Thực thi một bước trong sequence"""
        context = context or {}
        action = step.get('action', '')
        target = step.get('target')
        wait_after = step.get('wait_after', 0.5)
        label = step.get('label', '')

        self._log(f"  → {label}")

        try:
            if action == 'click':
                if target and isinstance(target, (list, tuple)) and len(target) == 2:
                    pyautogui.click(x=target[0], y=target[1])

            elif action == 'double_click':
                if target and isinstance(target, (list, tuple)) and len(target) == 2:
                    pyautogui.doubleClick(x=target[0], y=target[1])

            elif action == 'key':
                if target:
                    pyautogui.press(str(target))

            elif action == 'hotkey':
                if target:
                    keys = str(target).split('+')
                    pyautogui.hotkey(*keys)

            elif action == 'paste_text':
                source = step.get('source', '')
                text = self._resolve_variable(source, context)
                if text:
                    pyperclip.copy(str(text))
                    time.sleep(0.3)
                    pyautogui.hotkey('ctrl', 'v')

            elif action == 'type_text':
                text = self._resolve_variable(str(target), context)
                if text:
                    pyautogui.typewrite(text, interval=0.05)

            elif action == 'wait':
                pass  # wait_after xử lý bên dưới

            else:
                self._log(f"  ⚠️ Unknown action: {action}")

        except Exception as e:
            self._emit('on_error', step.get('id', 0), str(e))
            self._log(f"  ❌ Lỗi: {e}")
            return False

        if wait_after > 0:
            # Chia sleep thành chunk nhỏ để responsive hơn với pause/stop
            elapsed = 0
            while elapsed < wait_after:
                if not self._check_controls():
                    return False
                chunk = min(0.2, wait_after - elapsed)
                time.sleep(chunk)
                elapsed += chunk

        return True

    def _resolve_variable(self, template_str, context):
        """Thay thế biến template {{VAR}} bằng giá trị thực"""
        if not template_str:
            return template_str
        result = template_str
        for key, value in context.items():
            result = result.replace(f"{{{{{key}}}}}", str(value))
        return result

    def run_for_dialog(self, dialog_id, text, export_dir, dialog_index=0):
        """Chạy toàn bộ sequence cho 1 dialog"""
        if not self.template or 'steps' not in self.template:
            self._log("❌ Chưa load template!")
            return False

        context = {
            'CURRENT_TEXT': text,
            'DIALOG_ID': dialog_id,
            'EXPORT_DIR': export_dir,
        }

        self._emit('on_dialog_start', dialog_index, dialog_id)
        self._log(f"📝 Xử lý: {dialog_id}")

        steps = self.template['steps']
        for i, step in enumerate(steps):
            if not self._check_controls():
                self._log("🛑 Đã dừng.")
                return False

            self._emit('on_step_start', i, step)
            success = self.execute_step(step, context)
            if not success and self._stop_event.is_set():
                return False
            self._emit('on_step_complete', i, step)

        self._emit('on_dialog_complete', dialog_index, dialog_id)
        self._log(f"✅ Hoàn thành: {dialog_id}")
        return True

    def run_batch(self, data_rows, key_col, text_col, export_dir):
        """
        Chạy batch cho nhiều dialog.
        data_rows: list of dicts hoặc DataFrame rows
        """
        self.is_running = True
        self._stop_event.clear()
        self._pause_event.set()

        total = len(data_rows)
        self._log(f"🚀 Bắt đầu batch: {total} dialogs")

        for i, row in enumerate(data_rows):
            if not self._check_controls():
                break

            dialog_id = str(row[key_col])
            text = str(row[text_col])

            if not text or text.strip() == '' or text == 'nan':
                self._log(f"⏭️ Bỏ qua (trống): {dialog_id}")
                continue

            self._emit('on_progress', i + 1, total)
            success = self.run_for_dialog(dialog_id, text, export_dir, i)

            if not success and self._stop_event.is_set():
                break

        self.is_running = False
        self._log(f"🎉 Batch hoàn tất!")
        self._emit('on_progress', total, total)

    def pause(self):
        """Tạm dừng"""
        self.is_paused = True
        self._pause_event.clear()
        self._log("⏸️ Đã tạm dừng")

    def resume(self):
        """Tiếp tục"""
        self.is_paused = False
        self._pause_event.set()
        self._log("▶️ Tiếp tục...")

    def stop(self):
        """Dừng hoàn toàn"""
        self._stop_event.set()
        self._pause_event.set()  # Unblock pause nếu đang pause
        self.is_running = False
        self.is_paused = False
        self._log("🛑 Đã dừng")
