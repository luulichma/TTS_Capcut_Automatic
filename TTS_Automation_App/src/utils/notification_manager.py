"""
Notification Manager - Quản lý thông báo Windows và âm thanh
"""
import threading
import winsound


class NotificationManager:
    """Handle Windows notifications and sound alerts"""

    # Sound frequencies
    SOUNDS = {
        'complete': (1000, 300),   # frequency, duration_ms
        'error': (400, 500),
        'warning': (600, 200),
    }

    @staticmethod
    def show_toast(title, message, duration=5):
        """Hiển thị Windows toast notification"""
        try:
            from plyer import notification
            notification.notify(
                title=title,
                message=message,
                timeout=duration,
                app_name="TTS Automation Tool"
            )
        except ImportError:
            # Fallback: dùng winsound beep
            try:
                winsound.MessageBeep(winsound.MB_ICONINFORMATION)
            except Exception:
                pass
        except Exception:
            pass

    @staticmethod
    def play_sound(sound_type='complete'):
        """Phát âm thanh thông báo (non-blocking)"""
        def _play():
            try:
                if sound_type in NotificationManager.SOUNDS:
                    freq, dur = NotificationManager.SOUNDS[sound_type]
                    winsound.Beep(freq, dur)
                else:
                    winsound.MessageBeep(winsound.MB_ICONINFORMATION)
            except Exception:
                pass
        threading.Thread(target=_play, daemon=True).start()

    @staticmethod
    def notify_completion(title, success_count, error_count,
                          sound_enabled=True, toast_enabled=True):
        """Thông báo hoàn tất batch processing"""
        message = f"✅ {success_count} thành công"
        if error_count > 0:
            message += f", ❌ {error_count} lỗi"

        if toast_enabled:
            NotificationManager.show_toast(title, message)

        if sound_enabled:
            if error_count > 0:
                NotificationManager.play_sound('warning')
            else:
                NotificationManager.play_sound('complete')

    @staticmethod
    def confirm_action(parent, message, title="Xác nhận"):
        """Hiển thị dialog xác nhận"""
        from tkinter import messagebox
        return messagebox.askyesno(title, message, parent=parent)
