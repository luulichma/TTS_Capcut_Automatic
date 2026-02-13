"""
Config Manager - Quản lý cấu hình ứng dụng
"""
import yaml
import os
import json
import copy

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.yaml")
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")
PROFILES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "profiles")

# Default settings khi chưa có config
DEFAULT_SETTINGS = {
    'general': {
        'theme': 'darkly',
        'auto_save_interval': 300,
    },
    'performance': {
        'max_concurrent_exports': 3,
    },
    'notifications': {
        'sound_on_complete': True,
        'windows_notification': True,
        'error_popup': True,
    },
    'advanced': {
        'debug_mode': False,
        'log_level': 'INFO',
        'auto_backup': True,
        'retry_attempts': 2,
    },
}


class ConfigManager:
    """Quản lý cấu hình ứng dụng từ file YAML"""

    def __init__(self, config_path=None):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.config = {}
        self.load()
        self._ensure_defaults()

    def _ensure_defaults(self):
        """Đảm bảo tất cả settings mặc định đều tồn tại"""
        if 'settings' not in self.config:
            self.config['settings'] = {}
        for section, defaults in DEFAULT_SETTINGS.items():
            if section not in self.config['settings']:
                self.config['settings'][section] = {}
            for key, value in defaults.items():
                if key not in self.config['settings'][section]:
                    self.config['settings'][section][key] = value

    def load(self):
        """Load config từ file YAML"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Could not load config: {e}")
            self.config = {}

    def save(self):
        """Lưu config ra file YAML"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key_path, default=None):
        """Lấy giá trị config theo đường dẫn dot-separated. VD: 'api.provider'"""
        keys = key_path.split('.')
        val = self.config
        for k in keys:
            if isinstance(val, dict):
                val = val.get(k)
            else:
                return default
            if val is None:
                return default
        return val

    def set(self, key_path, value):
        """Set giá trị config theo đường dẫn dot-separated"""
        keys = key_path.split('.')
        d = self.config
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = value

    # --- Template Management ---

    def list_templates(self):
        """Liệt kê tất cả template files trong thư mục templates/"""
        templates = []
        if os.path.exists(TEMPLATES_DIR):
            for f in os.listdir(TEMPLATES_DIR):
                if f.endswith('.json'):
                    templates.append(f)
        return templates

    def load_template(self, filename):
        """Load template JSON file"""
        path = os.path.join(TEMPLATES_DIR, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def save_template(self, filename, template_data):
        """Lưu template JSON file"""
        os.makedirs(TEMPLATES_DIR, exist_ok=True)
        path = os.path.join(TEMPLATES_DIR, filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)
        return path

    # --- Profile Management ---

    def list_profiles(self):
        """Liệt kê tất cả profiles"""
        profiles = []
        os.makedirs(PROFILES_DIR, exist_ok=True)
        for f in os.listdir(PROFILES_DIR):
            if f.endswith('.json'):
                profiles.append(f[:-5])  # Remove .json extension
        return profiles

    def save_profile(self, name, profile_data):
        """
        Lưu profile chứa toàn bộ cấu hình hiện tại.
        profile_data: dict chứa data_source, levels, voice, mode, output_dir, etc.
        """
        os.makedirs(PROFILES_DIR, exist_ok=True)
        path = os.path.join(PROFILES_DIR, f"{name}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
        return path

    def load_profile(self, name):
        """Load profile theo tên"""
        path = os.path.join(PROFILES_DIR, f"{name}.json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def delete_profile(self, name):
        """Xóa profile"""
        path = os.path.join(PROFILES_DIR, f"{name}.json")
        if os.path.exists(path):
            os.remove(path)
            return True
        return False

    # --- Settings Shortcuts ---

    def get_setting(self, key, default=None):
        """Shortcut: lấy settings.xxx"""
        return self.get(f"settings.{key}", default)

    def set_setting(self, key, value):
        """Shortcut: set settings.xxx"""
        self.set(f"settings.{key}", value)

    def get_all_settings(self):
        """Lấy tất cả settings"""
        return copy.deepcopy(self.config.get('settings', DEFAULT_SETTINGS))

    def update_settings(self, settings_dict):
        """Cập nhật nhiều settings cùng lúc"""
        if 'settings' not in self.config:
            self.config['settings'] = {}

        def _deep_update(base, update):
            for key, value in update.items():
                if isinstance(value, dict) and isinstance(base.get(key), dict):
                    _deep_update(base[key], value)
                else:
                    base[key] = value

        _deep_update(self.config['settings'], settings_dict)
