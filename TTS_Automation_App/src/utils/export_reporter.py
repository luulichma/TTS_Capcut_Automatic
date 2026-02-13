"""
Export Reporter - Tạo báo cáo và manifest cho file đã xuất
"""
import json
import os
import csv
from datetime import datetime


class ExportReporter:
    """Generate export summary reports and manifests"""

    def __init__(self):
        self.exported_files = []  # list of dicts: {dialog_id, filepath, size, status, error}
        self.start_time = None
        self.end_time = None

    def start_tracking(self):
        """Bắt đầu theo dõi export"""
        self.exported_files = []
        self.start_time = datetime.now()
        self.end_time = None

    def record_export(self, dialog_id, filepath=None, status='success', error=None):
        """Ghi nhận 1 file đã export"""
        entry = {
            'dialog_id': dialog_id,
            'filepath': filepath or '',
            'status': status,  # 'success', 'error', 'skipped'
            'error': error or '',
            'timestamp': datetime.now().isoformat(),
        }
        if filepath and os.path.exists(filepath):
            entry['size_bytes'] = os.path.getsize(filepath)
        else:
            entry['size_bytes'] = 0
        self.exported_files.append(entry)

    def stop_tracking(self):
        """Kết thúc theo dõi"""
        self.end_time = datetime.now()

    def get_statistics(self):
        """Tính toán thống kê"""
        total = len(self.exported_files)
        success = sum(1 for f in self.exported_files if f['status'] == 'success')
        errors = sum(1 for f in self.exported_files if f['status'] == 'error')
        skipped = sum(1 for f in self.exported_files if f['status'] == 'skipped')
        total_size = sum(f.get('size_bytes', 0) for f in self.exported_files)

        elapsed = None
        if self.start_time:
            end = self.end_time or datetime.now()
            elapsed = (end - self.start_time).total_seconds()

        speed = (success / elapsed * 60) if elapsed and elapsed > 0 else 0

        return {
            'total': total,
            'success': success,
            'errors': errors,
            'skipped': skipped,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2) if total_size > 0 else 0,
            'elapsed_seconds': round(elapsed, 1) if elapsed else 0,
            'speed_per_min': round(speed, 1),
            'success_rate': round(success / total * 100, 1) if total > 0 else 0,
        }

    def get_failed_items(self):
        """Lấy danh sách items bị lỗi"""
        return [f for f in self.exported_files if f['status'] == 'error']

    def generate_manifest(self, output_path):
        """Tạo manifest.json cho các file đã export"""
        stats = self.get_statistics()
        manifest = {
            'generated_at': datetime.now().isoformat(),
            'statistics': stats,
            'files': self.exported_files,
        }
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        return output_path

    def export_errors_csv(self, output_path):
        """Export danh sách lỗi ra CSV"""
        failed = self.get_failed_items()
        if not failed:
            return None

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=['dialog_id', 'error', 'timestamp'])
            writer.writeheader()
            for item in failed:
                writer.writerow({
                    'dialog_id': item['dialog_id'],
                    'error': item['error'],
                    'timestamp': item['timestamp'],
                })
        return output_path

    def format_elapsed_time(self, seconds=None):
        """Format thời gian dạng human-readable"""
        if seconds is None:
            if self.start_time:
                end = self.end_time or datetime.now()
                seconds = (end - self.start_time).total_seconds()
            else:
                return "0s"
        if seconds < 60:
            return f"{int(seconds)}s"
        elif seconds < 3600:
            m, s = divmod(int(seconds), 60)
            return f"{m}m {s}s"
        else:
            h, remainder = divmod(int(seconds), 3600)
            m, s = divmod(remainder, 60)
            return f"{h}h {m}m {s}s"

    def estimate_eta(self, current_index, total):
        """Ước tính thời gian còn lại"""
        if not self.start_time or current_index <= 0:
            return "Calculating..."
        elapsed = (datetime.now() - self.start_time).total_seconds()
        avg_per_item = elapsed / current_index
        remaining = (total - current_index) * avg_per_item
        return self.format_elapsed_time(remaining)
