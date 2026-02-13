"""
Data Manager - Quản lý dữ liệu từ Excel, CSV, Google Sheets
"""
import pandas as pd
import os
import re


class DataManager:
    """Load và quản lý dữ liệu text từ nhiều nguồn"""

    # Các ngôn ngữ có thể detect tự động
    LANGUAGE_KEYWORDS = {
        'Vietnamese': ['vi', 'viet', 'vietnamese', 'tiếng việt'],
        'English': ['en', 'eng', 'english', 'tiếng anh'],
        'Japanese': ['ja', 'jp', 'japanese', 'tiếng nhật', 'nihongo'],
        'Korean': ['ko', 'kr', 'korean', 'tiếng hàn'],
        'Chinese': ['zh', 'cn', 'chinese', 'tiếng trung'],
    }

    def __init__(self):
        self.df = None
        self.source_type = None  # 'excel', 'csv', 'google_sheet'
        self.source_path = ""
        self.column_names = []
        self.column_language_map = {}  # {col_index: language_name}

    # ==================== Data Loading ====================

    def load_excel(self, filepath, skip_rows=2):
        """Load từ Excel file"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File không tồn tại: {filepath}")

        self.df = pd.read_excel(filepath, skiprows=skip_rows)
        self.df.columns = [str(col).strip() for col in self.df.columns]
        self.source_type = 'excel'
        self.source_path = filepath
        self.column_names = list(self.df.columns)
        return True

    def load_csv(self, filepath, skip_rows=0, encoding='utf-8'):
        """Load từ CSV file"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File không tồn tại: {filepath}")

        self.df = pd.read_csv(filepath, skiprows=skip_rows, encoding=encoding)
        self.df.columns = [str(col).strip() for col in self.df.columns]
        self.source_type = 'csv'
        self.source_path = filepath
        self.column_names = list(self.df.columns)
        return True

    def load_google_sheet(self, url_or_id, worksheet_index=0, skip_rows=2):
        """Load từ Google Sheet (public hoặc private)"""
        try:
            sheet_id = self._extract_sheet_id(url_or_id)

            # Thử public access trước
            try:
                return self._load_public_sheet(sheet_id, skip_rows)
            except Exception:
                pass

            # Private access với OAuth
            return self._load_private_sheet(sheet_id, worksheet_index, skip_rows)

        except Exception as e:
            raise ConnectionError(f"Không thể load Google Sheet: {e}")

    def _extract_sheet_id(self, url_or_id):
        """Trích xuất Sheet ID từ URL hoặc trả về ID trực tiếp"""
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url_or_id)
        if match:
            return match.group(1)
        return url_or_id

    def _load_public_sheet(self, sheet_id, skip_rows):
        """Load public Google Sheet qua CSV export URL"""
        csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"
        self.df = pd.read_csv(csv_url, skiprows=skip_rows)
        self.df.columns = [str(col).strip() for col in self.df.columns]
        self.source_type = 'google_sheet'
        self.source_path = sheet_id
        self.column_names = list(self.df.columns)
        return True

    def _load_private_sheet(self, sheet_id, worksheet_index, skip_rows):
        """Load private Google Sheet qua gspread + OAuth"""
        try:
            import gspread
            from google.auth.transport.requests import Request
            from google_auth_oauthlib.flow import InstalledAppFlow

            SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

            # Tìm credentials file
            creds_path = os.path.join(os.path.dirname(__file__), '..', '..', 'credentials.json')
            token_path = os.path.join(os.path.dirname(__file__), '..', '..', 'token.json')

            creds = None
            if os.path.exists(token_path):
                from google.oauth2.credentials import Credentials
                creds = Credentials.from_authorized_user_file(token_path, SCOPES)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(creds_path):
                        raise FileNotFoundError(
                            "Cần file credentials.json cho private sheets.\n"
                            "Tải từ: Google Cloud Console > APIs > Credentials > OAuth 2.0"
                        )
                    flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                    creds = flow.run_local_server(port=0)

                with open(token_path, 'w') as token:
                    token.write(creds.to_json())

            gc = gspread.authorize(creds)
            spreadsheet = gc.open_by_key(sheet_id)
            worksheet = spreadsheet.get_worksheet(worksheet_index)
            data = worksheet.get_all_values()

            if skip_rows > 0:
                data = data[skip_rows:]

            if len(data) > 1:
                self.df = pd.DataFrame(data[1:], columns=data[0])
            else:
                self.df = pd.DataFrame(data)

            self.df.columns = [str(col).strip() for col in self.df.columns]
            self.source_type = 'google_sheet'
            self.source_path = sheet_id
            self.column_names = list(self.df.columns)
            return True

        except ImportError:
            raise ImportError("Cần cài gspread và google-auth: pip install gspread google-auth google-auth-oauthlib")

    # ==================== Column & Language ====================

    def set_column_language(self, col_index, language_name):
        """Gán ngôn ngữ cho cột"""
        self.column_language_map[col_index] = language_name

    def get_available_languages(self):
        """Lấy danh sách ngôn ngữ đã được map"""
        return dict(self.column_language_map)

    def get_key_column(self, col_index=0):
        """Lấy tên cột key"""
        if self.df is not None and col_index < len(self.column_names):
            return self.column_names[col_index]
        return None

    def detect_column_language(self, col_index):
        """Tự động detect ngôn ngữ của cột dựa trên tên cột"""
        if col_index >= len(self.column_names):
            return None
        col_name = self.column_names[col_index].lower().strip()
        for lang, keywords in self.LANGUAGE_KEYWORDS.items():
            for kw in keywords:
                if kw in col_name:
                    return lang
        return None

    def auto_detect_all_languages(self):
        """Tự động detect ngôn ngữ cho tất cả cột"""
        detected = {}
        for i, col_name in enumerate(self.column_names):
            lang = self.detect_column_language(i)
            if lang:
                detected[i] = lang
        return detected

    # ==================== Level Selection (Enhanced) ====================

    @staticmethod
    def parse_level_selection(selection_string):
        """
        Parse chuỗi level selection linh hoạt.
        Hỗ trợ:
            - "all" hoặc "" → None (tất cả levels)
            - "10" → [10]
            - "8-10" → [8, 9, 10]
            - "8,10,15" → [8, 10, 15]
            - "8-10,15,20-22" → [8, 9, 10, 15, 20, 21, 22]
        Returns: list of int levels, hoặc None cho tất cả
        """
        if not selection_string or selection_string.strip().lower() == 'all':
            return None

        levels = set()
        parts = selection_string.replace(' ', '').split(',')
        for part in parts:
            part = part.strip()
            if not part:
                continue
            if '-' in part:
                try:
                    start, end = part.split('-', 1)
                    start, end = int(start), int(end)
                    if start > end:
                        start, end = end, start
                    levels.update(range(start, end + 1))
                except ValueError:
                    continue
            else:
                try:
                    levels.add(int(part))
                except ValueError:
                    continue

        return sorted(levels) if levels else None

    def filter_by_levels(self, key_col_index=0, levels=None):
        """
        Lọc dữ liệu theo danh sách levels.
        levels: list of int, hoặc None cho tất cả
        """
        if self.df is None:
            return pd.DataFrame()

        if levels is None:
            return self.df.copy()

        key_col = self.column_names[key_col_index]
        masks = []
        for level in levels:
            mask = self.df[key_col].astype(str).str.match(rf's_(re_)?dialog_{level}_\d+')
            masks.append(mask)

        if masks:
            combined_mask = masks[0]
            for m in masks[1:]:
                combined_mask = combined_mask | m
            return self.df[combined_mask].copy()

        return pd.DataFrame()

    def filter_by_level(self, key_col_index=0, level=None):
        """Lọc dữ liệu theo Level (backward compatible)"""
        if level is not None:
            return self.filter_by_levels(key_col_index, [level])
        return self.filter_by_levels(key_col_index, None)

    def get_level_preview(self, key_col_index=0, levels=None, max_items=20):
        """Lấy preview danh sách dialog IDs sẽ được xử lý"""
        filtered = self.filter_by_levels(key_col_index, levels)
        key_col = self.column_names[key_col_index]
        all_ids = filtered[key_col].astype(str).tolist()
        return {
            'total_count': len(all_ids),
            'preview_ids': all_ids[:max_items],
            'has_more': len(all_ids) > max_items,
        }

    # ==================== Data Quality ====================

    def get_text_for_row(self, row, language_col_index):
        """Lấy text từ row theo cột ngôn ngữ"""
        col_name = self.column_names[language_col_index]
        text = row[col_name]
        if pd.isna(text) or str(text).strip() == "":
            return None
        return str(text).strip()

    def get_preview_data(self, max_rows=100):
        """Lấy preview data để hiển thị trên GUI"""
        if self.df is None:
            return [], []
        headers = list(self.df.columns)
        rows = self.df.head(max_rows).values.tolist()
        return headers, rows

    def get_total_rows(self):
        """Tổng số dòng dữ liệu"""
        return len(self.df) if self.df is not None else 0

    def get_data_quality_report(self, key_col_index=0, text_col_indices=None):
        """
        Phân tích chất lượng dữ liệu.
        Returns dict:
            - total_rows: tổng số dòng
            - empty_rows: dict {col_index: count}
            - duplicate_keys: count
            - long_texts: dict {col_index: count} (>500 chars)
            - issues: list of dicts {type, message, severity}
        """
        if self.df is None:
            return {'total_rows': 0, 'issues': []}

        text_col_indices = text_col_indices or []
        report = {
            'total_rows': len(self.df),
            'empty_rows': {},
            'duplicate_keys': 0,
            'long_texts': {},
            'issues': [],
        }

        # Kiểm tra duplicate keys
        if key_col_index < len(self.column_names):
            key_col = self.column_names[key_col_index]
            dup_count = self.df[key_col].duplicated().sum()
            report['duplicate_keys'] = int(dup_count)
            if dup_count > 0:
                report['issues'].append({
                    'type': 'duplicate',
                    'message': f"⚠️ Có {dup_count} key trùng lặp",
                    'severity': 'warning'
                })

        # Kiểm tra từng cột text
        for col_idx in text_col_indices:
            if col_idx >= len(self.column_names):
                continue
            col_name = self.column_names[col_idx]

            # Empty rows
            empty_count = self.df[col_name].isna().sum() + (self.df[col_name].astype(str).str.strip() == '').sum()
            report['empty_rows'][col_idx] = int(empty_count)
            if empty_count > 0:
                report['issues'].append({
                    'type': 'empty',
                    'message': f"⚠️ Cột '{col_name}': {empty_count} dòng trống",
                    'severity': 'warning'
                })

            # Long texts (>500 chars - có thể gây lỗi TTS)
            long_count = (self.df[col_name].astype(str).str.len() > 500).sum()
            report['long_texts'][col_idx] = int(long_count)
            if long_count > 0:
                report['issues'].append({
                    'type': 'long_text',
                    'message': f"⚠️ Cột '{col_name}': {long_count} dòng text quá dài (>500 ký tự)",
                    'severity': 'info'
                })

        if not report['issues']:
            report['issues'].append({
                'type': 'ok',
                'message': '✅ Dữ liệu hợp lệ, không có vấn đề',
                'severity': 'success'
            })

        return report

    # ==================== Validation ====================

    @staticmethod
    def validate_file_path(filepath):
        """
        Validate file path.
        Returns: (is_valid, message)
        """
        if not filepath or not filepath.strip():
            return False, "Chưa nhập đường dẫn"

        filepath = filepath.strip()

        # Check Google Sheet URL
        if 'docs.google.com/spreadsheets' in filepath or len(filepath) == 44:
            return True, "Google Sheet URL"

        if not os.path.exists(filepath):
            return False, "File không tồn tại"

        ext = os.path.splitext(filepath)[1].lower()
        valid_exts = ['.xlsx', '.xls', '.csv']
        if ext not in valid_exts:
            return False, f"Định dạng không hỗ trợ: {ext}"

        return True, f"✅ {ext.upper()[1:]} file"

    # ==================== Auto Detect ====================

    def auto_detect_source(self, source_string, skip_rows=2):
        """Tự động detect và load từ đúng nguồn"""
        source_string = source_string.strip()

        if 'docs.google.com/spreadsheets' in source_string or len(source_string) == 44:
            return self.load_google_sheet(source_string, skip_rows=skip_rows)
        elif source_string.endswith('.csv'):
            return self.load_csv(source_string, skip_rows=skip_rows)
        elif source_string.endswith(('.xlsx', '.xls')):
            return self.load_excel(source_string, skip_rows=skip_rows)
        else:
            # Thử detect
            if os.path.exists(source_string):
                ext = os.path.splitext(source_string)[1].lower()
                if ext == '.csv':
                    return self.load_csv(source_string, skip_rows=skip_rows)
                else:
                    return self.load_excel(source_string, skip_rows=skip_rows)
            else:
                return self.load_google_sheet(source_string, skip_rows=skip_rows)
