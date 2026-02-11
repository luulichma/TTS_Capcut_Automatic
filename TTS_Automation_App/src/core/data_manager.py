"""
Data Manager - Quản lý dữ liệu từ Excel, CSV, Google Sheets
"""
import pandas as pd
import os
import re


class DataManager:
    """Load và quản lý dữ liệu text từ nhiều nguồn"""

    def __init__(self):
        self.df = None
        self.source_type = None  # 'excel', 'csv', 'google_sheet'
        self.source_path = ""
        self.column_names = []
        self.column_language_map = {}  # {col_index: language_name}

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

    def filter_by_level(self, key_col_index=0, level=None):
        """Lọc dữ liệu theo Level (dựa trên key pattern: s_dialog_X_Y hoặc s_re_dialog_X_Y)"""
        if self.df is None:
            return pd.DataFrame()

        key_col = self.column_names[key_col_index]

        if level is not None:
            mask = self.df[key_col].astype(str).str.match(rf's_(re_)?dialog_{level}_\d+')
            return self.df[mask].copy()
        return self.df.copy()

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
