"""
Config Manager - Quản lý cấu hình ứng dụng
"""
import yaml
import os
import json

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config.yaml")
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "templates")


class ConfigManager:
    """Quản lý cấu hình ứng dụng từ file YAML"""

    def __init__(self, config_path=None):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.config = {}
        self.load()

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
