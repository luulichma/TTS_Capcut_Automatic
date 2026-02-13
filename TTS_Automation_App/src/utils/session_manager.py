"""
Session Manager - Lưu và khôi phục trạng thái session
"""
import json
import os
from datetime import datetime

SESSION_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "sessions")


class SessionManager:
    """Save/resume session state for batch processing"""

    def __init__(self, session_dir=None):
        self.session_dir = session_dir or SESSION_DIR
        os.makedirs(self.session_dir, exist_ok=True)

    def _session_path(self, name="last_session"):
        return os.path.join(self.session_dir, f"{name}.json")

    def save_session(self, state, name="last_session"):
        """
        Lưu session state.
        state: dict chứa:
            - mode: 'capcut' hoặc 'api'
            - completed_indices: list các index đã xử lý
            - total: tổng số items
            - config: run config snapshot
            - timestamp: thời gian lưu
        """
        state['timestamp'] = datetime.now().isoformat()
        path = self._session_path(name)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            return True
        except Exception:
            return False

    def load_session(self, name="last_session"):
        """Load session đã lưu"""
        path = self._session_path(name)
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def has_saved_session(self, name="last_session"):
        """Kiểm tra có session đã lưu chưa"""
        path = self._session_path(name)
        return os.path.exists(path)

    def clear_session(self, name="last_session"):
        """Xóa session đã lưu"""
        path = self._session_path(name)
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception:
                pass

    def get_session_info(self, name="last_session"):
        """Lấy thông tin tóm tắt session"""
        session = self.load_session(name)
        if session:
            completed = len(session.get('completed_indices', []))
            total = session.get('total', 0)
            timestamp = session.get('timestamp', 'Unknown')
            mode = session.get('mode', 'Unknown')
            return {
                'completed': completed,
                'remaining': total - completed,
                'total': total,
                'mode': mode,
                'timestamp': timestamp,
            }
        return None
