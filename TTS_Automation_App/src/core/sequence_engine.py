"""
Sequence Engine - Chạy chuỗi tương tác automation cho CapCut
"""
import pyautogui
import pyperclip
import time
import json
import threading
import copy
import os
import glob


class SequenceEngine:
    """Engine chạy chuỗi tương tác tự động dựa trên template"""

    SUPPORTED_ACTIONS = ['click', 'double_click', 'key', 'hotkey', 'paste_text', 'type_text', 'wait']

    # Timing presets: multiplier cho wait_after
    TIMING_PRESETS = {
        'slow': 2.0,
        'normal': 1.0,
        'fast': 0.5,
    }

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
            - on_retry(dialog_id, attempt)
            - on_batch_complete(success_count, error_count, skipped_count)
        """
        self.callbacks = callbacks or {}
        self.template = None
        self.is_running = False
        self.is_paused = False
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # Not paused initially

        # Enhanced features
        self.timing_preset = 'normal'
        self.retry_attempts = 2
        self.dry_run = False
        self.failed_items = []
        self.completed_indices = []
        self.success_count = 0
        self.error_count = 0
        self.skipped_count = 0

        # Undo/redo for template editing
        self._undo_stack = []
        self._redo_stack = []

    def load_template(self, template_data):
        """Load template (dict hoặc file path)"""
        if isinstance(template_data, str):
            with open(template_data, 'r', encoding='utf-8') as f:
                self.template = json.load(f)
        else:
            self.template = template_data

    def set_timing_preset(self, preset):
        """Đặt timing preset: 'slow', 'normal', 'fast'"""
        if preset in self.TIMING_PRESETS:
            self.timing_preset = preset
            self._log(f"⏱️ Timing: {preset} (x{self.TIMING_PRESETS[preset]})")

    def set_retry_attempts(self, attempts):
        """Đặt số lần retry"""
        self.retry_attempts = max(0, int(attempts))

    def set_dry_run(self, enabled):
        """Bật/tắt dry-run mode"""
        self.dry_run = enabled

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

    # ==================== Smart Wait (File/Process Detection) ====================

    def _wait_for_file_export(self, export_dir, dialog_id, max_wait=15, check_interval=0.5):
        """
        Chờ cho đến khi file audio được export.
        Thay vì delay cứng, detect file thực tế được tạo.
        
        Args:
            export_dir: Thư mục chứa file export
            dialog_id: ID của dialog (tên file)
            max_wait: Thời gian chờ tối đa (giây)
            check_interval: Khoảng time check file (giây)
        
        Returns:
            True nếu file được tạo, False nếu timeout
        """
        expected_file = os.path.join(export_dir, f"{dialog_id}.mp3")
        expected_file_wav = os.path.join(export_dir, f"{dialog_id}.wav")
        
        start_time = time.time()
        last_size = 0
        stable_count = 0  # Đếm bao nhiêu lần file size không thay đổi
        
        self._log(f"  ⏳ Chờ file export: {dialog_id}...")
        
        while time.time() - start_time < max_wait:
            if not self._check_controls():
                return False
            
            # Kiểm tra file MP3 hoặc WAV
            for filepath in [expected_file, expected_file_wav]:
                if os.path.exists(filepath):
                    file_size = os.path.getsize(filepath)
                    
                    # File size phải > 0 và ổn định (không thay đổi 2 lần liên tiếp)
                    if file_size > 0:
                        if file_size == last_size:
                            stable_count += 1
                        else:
                            stable_count = 0
                            last_size = file_size
                        
                        if stable_count >= 2:  # File size ổn định
                            elapsed = time.time() - start_time
                            self._log(f"  ✅ File đã export trong {elapsed:.1f}s")
                            return True
            
            time.sleep(check_interval)
        
        # Timeout
        elapsed = time.time() - start_time
        self._log(f"  ⚠️ Timeout chờ file (>{max_wait}s)")
        return False

    def _smart_wait(self, wait_after, export_dir=None, dialog_id=None):
        """
        Smart wait: Kết hợp file detection + delay fallback.
        Nếu có export_dir + dialog_id → detect file export
        Nếu không → dùng delay cứng
        """
        # Nếu có export directory, thử detect file
        if export_dir and dialog_id and os.path.isdir(export_dir):
            # Giảm max_wait xuống (vì nó có fallback delay)
            max_wait_file = min(wait_after * 1.5, 20)
            success = self._wait_for_file_export(export_dir, dialog_id, max_wait=max_wait_file, check_interval=0.3)
            
            if success:
                return  # File đã được export, không cần chờ thêm
        
        # Fallback: dùng delay cứng với responsiveness tốt
        elapsed = 0
        while elapsed < wait_after:
            if not self._check_controls():
                return
            chunk = min(0.2, wait_after - elapsed)
            time.sleep(chunk)
            elapsed += chunk


    # ==================== Template Editing (Undo/Redo) ====================

    def _save_undo_state(self):
        """Lưu state hiện tại vào undo stack"""
        if self.template:
            self._undo_stack.append(copy.deepcopy(self.template))
            self._redo_stack.clear()
            # Giới hạn stack size
            if len(self._undo_stack) > 50:
                self._undo_stack.pop(0)

    def undo_template(self):
        """Undo template edit"""
        if self._undo_stack:
            self._redo_stack.append(copy.deepcopy(self.template))
            self.template = self._undo_stack.pop()
            return True
        return False

    def redo_template(self):
        """Redo template edit"""
        if self._redo_stack:
            self._undo_stack.append(copy.deepcopy(self.template))
            self.template = self._redo_stack.pop()
            return True
        return False

    def can_undo(self):
        return len(self._undo_stack) > 0

    def can_redo(self):
        return len(self._redo_stack) > 0

    def clone_step(self, step_index):
        """Clone 1 step tại vị trí step_index, chèn ngay sau nó"""
        if not self.template or 'steps' not in self.template:
            return False
        steps = self.template['steps']
        if 0 <= step_index < len(steps):
            self._save_undo_state()
            cloned = copy.deepcopy(steps[step_index])
            cloned['id'] = max(s.get('id', 0) for s in steps) + 1
            cloned['label'] = cloned.get('label', '') + ' (Copy)'
            steps.insert(step_index + 1, cloned)
            return True
        return False

    # ==================== Step Execution ====================

    def execute_step(self, step, context=None, dry_run=False):
        """Thực thi một bước trong sequence"""
        context = context or {}
        action = step.get('action', '')
        target = step.get('target')
        wait_after = step.get('wait_after', 0.5)
        label = step.get('label', '')
        step_id = step.get('id', 0)

        # Apply timing preset
        multiplier = self.TIMING_PRESETS.get(self.timing_preset, 1.0)
        wait_after = wait_after * multiplier

        # Dry-run mode: chỉ log, không thực thi
        if dry_run or self.dry_run:
            if action in ('click', 'double_click') and target:
                self._log(f"  🔍 [DRY RUN] {label}: {action} at ({target[0]}, {target[1]})")
            else:
                self._log(f"  🔍 [DRY RUN] {label}: {action}")
            return True

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
            self._emit('on_error', step_id, str(e))
            self._log(f"  ❌ Lỗi: {e}")
            return False

        if wait_after > 0:
            # Kiểm tra nếu đây là step export → dùng smart wait
            is_export_step = 'export' in label.lower() or step_id in [11, 23]  # Step 11: Start Reading, Step 23: Confirm Export
            
            if is_export_step and context.get('EXPORT_DIR'):
                # Smart wait: detect file thay vì chỉ delay
                dialog_id = context.get('DIALOG_ID', 'unknown')
                export_dir = context.get('EXPORT_DIR', '')
                self._smart_wait(wait_after, export_dir, dialog_id)
            else:
                # Regular wait: delay cứng
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

    # ==================== Dialog Execution ====================

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

    def _run_with_retry(self, dialog_id, text, export_dir, dialog_index):
        """Chạy dialog với retry logic"""
        for attempt in range(self.retry_attempts + 1):
            if attempt > 0:
                self._emit('on_retry', dialog_id, attempt)
                self._log(f"🔄 Retry lần {attempt}/{self.retry_attempts}: {dialog_id}")
                time.sleep(1)  # Wait before retry

            success = self.run_for_dialog(dialog_id, text, export_dir, dialog_index)
            if success:
                return True

            if self._stop_event.is_set():
                return False

        return False

    # ==================== Batch Processing ====================

    def run_batch(self, data_rows, key_col, text_col, export_dir, resume_from=None):
        """
        Chạy batch cho nhiều dialog.
        data_rows: list of dicts hoặc DataFrame rows
        resume_from: set of indices đã hoàn thành (để resume session)
        """
        self.is_running = True
        self._stop_event.clear()
        self._pause_event.set()
        self.failed_items = []
        self.completed_indices = list(resume_from) if resume_from else []
        self.success_count = 0
        self.error_count = 0
        self.skipped_count = 0

        total = len(data_rows)
        self._log(f"🚀 Bắt đầu batch: {total} dialogs")

        if resume_from:
            self._log(f"📂 Tiếp tục từ session trước ({len(resume_from)} đã xong)")

        for i, row in enumerate(data_rows):
            if not self._check_controls():
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
            success = self._run_with_retry(dialog_id, text, export_dir, i)

            if success:
                self.success_count += 1
                self.completed_indices.append(i)
            else:
                if self._stop_event.is_set():
                    break
                self.error_count += 1
                self.failed_items.append({
                    'index': i,
                    'dialog_id': dialog_id,
                    'text': text,
                })

        self.is_running = False
        self._log(f"🎉 Batch hoàn tất! ✅ {self.success_count} thành công, "
                   f"❌ {self.error_count} lỗi, ⏭️ {self.skipped_count} bỏ qua")
        self._emit('on_progress', total, total)
        self._emit('on_batch_complete', self.success_count, self.error_count, self.skipped_count)

    def retry_failed(self, export_dir):
        """Retry các items bị lỗi"""
        if not self.failed_items:
            self._log("✅ Không có items cần retry")
            return

        self.is_running = True
        self._stop_event.clear()
        self._pause_event.set()

        items_to_retry = list(self.failed_items)
        self.failed_items = []

        total = len(items_to_retry)
        self._log(f"🔄 Retry {total} items bị lỗi...")

        retried_success = 0
        retried_error = 0

        for i, item in enumerate(items_to_retry):
            if not self._check_controls():
                break

            self._emit('on_progress', i + 1, total)
            success = self.run_for_dialog(
                item['dialog_id'], item['text'], export_dir, item['index']
            )

            if success:
                retried_success += 1
                self.success_count += 1
                self.error_count -= 1
                self.completed_indices.append(item['index'])
            else:
                retried_error += 1
                self.failed_items.append(item)
                if self._stop_event.is_set():
                    break

        self.is_running = False
        self._log(f"🔄 Retry hoàn tất! ✅ {retried_success} thành công, ❌ {retried_error} vẫn lỗi")

    # ==================== Controls ====================

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
