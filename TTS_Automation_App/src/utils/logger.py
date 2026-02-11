"""
Logger - Hệ thống logging cho ứng dụng
"""
import logging
import os
from datetime import datetime


class AppLogger:
    """Logger hỗ trợ cả file logging và GUI logging"""

    def __init__(self, log_dir=None):
        log_dir = log_dir or os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
        os.makedirs(log_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(log_dir, f"tts_automation_{timestamp}.log")

        self.logger = logging.getLogger('TTS_Automation')
        self.logger.setLevel(logging.DEBUG)

        # File handler
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s'))
        self.logger.addHandler(fh)

        # GUI callback
        self._gui_callback = None

    def set_gui_callback(self, callback):
        """Set callback để gửi log đến GUI widget"""
        self._gui_callback = callback

    def _emit_to_gui(self, message):
        if self._gui_callback:
            try:
                self._gui_callback(message)
            except Exception:
                pass

    def info(self, msg):
        self.logger.info(msg)
        self._emit_to_gui(f"ℹ️ {msg}")

    def success(self, msg):
        self.logger.info(f"[SUCCESS] {msg}")
        self._emit_to_gui(f"✅ {msg}")

    def warning(self, msg):
        self.logger.warning(msg)
        self._emit_to_gui(f"⚠️ {msg}")

    def error(self, msg):
        self.logger.error(msg)
        self._emit_to_gui(f"❌ {msg}")

    def debug(self, msg):
        self.logger.debug(msg)
