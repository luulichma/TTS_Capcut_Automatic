# 🔧 Technical Reference - Dành Cho Developers

**Tài liệu kỹ thuật chi tiết về cấu trúc code, API, và extension.**

---

## 📁 Cấu Trúc Project

```
TTS_Automation_App/
├─ main.py                    # Entry point
├─ config.yaml               # Cấu hình chính
├─ requirements.txt          # Dependencies
│
├─ src/
│  ├─ core/                  # Logic chính
│  │  ├─ api_engine.py       # Edge TTS API wrapper
│  │  ├─ sequence_engine.py  # CapCut automation
│  │  ├─ config_manager.py   # Config parser
│  │  ├─ data_manager.py     # Data loading & processing
│  │  └─ __init__.py
│  │
│  ├─ gui/                   # Giao diện Tkinter
│  │  ├─ main_window.py      # Cửa sổ chính
│  │  ├─ data_panel.py       # Panel tải dữ liệu
│  │  ├─ capcut_panel.py     # Panel CapCut automation
│  │  ├─ api_panel.py        # Panel API export
│  │  ├─ settings_window.py  # Settings dialog
│  │  ├─ level_selector.py   # Level filter widget
│  │  ├─ coordinate_tool.py  # Coordinate picker
│  │  └─ __init__.py
│  │
│  └─ utils/                 # Utility functions
│     ├─ logger.py           # Logging setup
│     ├─ export_reporter.py  # Export statistics
│     ├─ notification_manager.py # Desktop notifications
│     ├─ session_manager.py  # Session management
│     └─ __init__.py
│
├─ templates/                # Template files
│  ├─ capcut_tts_default.json
│  ├─ capcut_pc_tts.json
│  └─ ...
│
├─ docs/                     # Documentation
│  ├─ HUONG_DAN_SU_DUNG.md
│  ├─ CAIDAT_CHI_TIET.md
│  ├─ QUICK_START.md
│  └─ TECHNICAL_REFERENCE.md (this file)
│
└─ build/                    # PyInstaller output (khi build exe)
```

---

## 🏗️ Kiến Trúc Chính

### 3 Layer Architecture

```
┌─ GUI Layer (Tkinter) ─────────────────────┐
│ - main_window.py (điều phối)              │
│ - data_panel.py (data input)              │
│ - capcut_panel.py (CapCut config)         │
│ - api_panel.py (API config)               │
└──────────────────────────────────────────┘
            ↓
┌─ Business Logic Layer ────────────────────┐
│ - api_engine.py (Edge TTS API)            │
│ - sequence_engine.py (CapCut automation)  │
│ - data_manager.py (data processing)       │
│ - config_manager.py (config management)   │
└──────────────────────────────────────────┘
            ↓
┌─ Utility Layer ───────────────────────────┐
│ - logger.py                               │
│ - export_reporter.py                      │
│ - session_manager.py                      │
│ - notification_manager.py                 │
└──────────────────────────────────────────┘
```

---

## 📚 Main Modules

### 1. api_engine.py

**Mục đích:** Tạo audio từ text dùng Edge TTS API

```python
class APIEngine:
    """TTS API client"""
    
    def export_batch(self, data_rows, key_col, text_col, export_dir, voice=None):
        """Export batch dialogs"""
        
    async def _synthesize_one(self, text, output_path, voice=None):
        """Tạo 1 audio file"""
        
    def _export_with_retry(self, dialog_id, text, export_dir, voice=None):
        """Export với retry logic"""
```

**Key Features:**
- ✓ Async synthesis
- ✓ Automatic retry (1-5 lần)
- ✓ Auto backup
- ✓ Multi-voice support

### 2. sequence_engine.py

**Mục đích:** Tự động hóa UI CapCut dùng PyAutoGUI

```python
class SequenceEngine:
    """CapCut automation engine"""
    
    def execute_step(self, step, context=None):
        """Thực thi 1 bước automation"""
        
    def _smart_wait(self, wait_after, export_dir, dialog_id):
        """Smart wait: detect file thay vì delay cứng"""
        
    def run_batch(self, data_rows, key_col, text_col, export_dir):
        """Chạy batch automation"""
```

**Key Features:**
- ✓ Template-based automation
- ✓ Smart file detection (detect export)
- ✓ Pause/Resume support
- ✓ Undo/Redo for templates

### 3. data_manager.py

**Mục đích:** Load, validate, và process data

```python
class DataManager:
    """Data loading and processing"""
    
    def auto_detect_source(self, source, skip_rows=2):
        """Detect file type (Excel/CSV/Google Sheets)"""
        
    def auto_detect_all_languages(self):
        """Tự động detect ngôn ngữ mỗi cột"""
        
    def filter_by_level(self, key_col_idx, level):
        """Lọc dữ liệu theo level"""
```

**Key Features:**
- ✓ Multi-source support (Excel, CSV, Google Sheets)
- ✓ Auto language detection
- ✓ Data validation
- ✓ Quality report

### 4. config_manager.py

**Mục đích:** Quản lý cấu hình từ YAML

```python
class ConfigManager:
    """Config management"""
    
    def load(self):
        """Load config từ file"""
        
    def save_profile(self, name, profile_data):
        """Lưu profile"""
        
    def load_profile(self, name):
        """Load profile"""
```

---

## 🔌 API Reference

### APIEngine

#### Methods

```python
# Initialize
engine = APIEngine(callbacks={...})

# Set voice
engine.set_voice("vi-VN-HoaiMyNeural")

# Set output format
engine.set_format("mp3")  # or "wav"

# Export single dialog
success = engine.export_single(
    dialog_id="intro_001",
    text="Hello world",
    export_dir="/path/to/output",
    voice="en-US-JennyNeural"
)

# Export batch
engine.export_batch(
    data_rows=[{...}, {...}],
    key_col="dialog_id",
    text_col="text_english",
    export_dir="/path/to/output",
    voice="en-US-JennyNeural"
)

# Retry failed items
engine.retry_failed(export_dir="/path/to/output")

# Stop
engine.stop()
```

#### Callbacks

```python
callbacks = {
    'on_start': lambda dialog_id: None,
    'on_complete': lambda dialog_id, filepath: None,
    'on_error': lambda dialog_id, error_msg: None,
    'on_log': lambda message: None,
    'on_progress': lambda current, total: None,
    'on_batch_complete': lambda success, errors, skipped: None,
}
```

### SequenceEngine

#### Methods

```python
# Initialize
engine = SequenceEngine(callbacks={...})

# Load template
engine.load_template("/path/to/template.json")

# Execute step
success = engine.execute_step(
    step={
        "action": "click",
        "target": [100, 200],
        "wait_after": 0.5
    },
    context={"CURRENT_TEXT": "Hello", "DIALOG_ID": "intro_001"}
)

# Run for single dialog
success = engine.run_for_dialog(
    dialog_id="intro_001",
    text="Hello world",
    export_dir="/path/to/output"
)

# Run batch
engine.run_batch(
    data_rows=[{...}, {...}],
    key_col="dialog_id",
    text_col="text_english",
    export_dir="/path/to/output"
)

# Undo/Redo
engine.undo_template()
engine.redo_template()
```

### DataManager

#### Methods

```python
# Load data
manager.auto_detect_source(
    source="path/to/file.xlsx",
    skip_rows=2
)

# Get column info
columns = manager.column_names  # List of column names
total = manager.get_total_rows()  # Total rows

# Filter data
filtered = manager.filter_by_level(
    key_col_idx=0,
    level=1
)

# Auto detect languages
langs = manager.auto_detect_all_languages()
# Returns: {col_idx: "language", ...}
```

---

## 📝 Template Format

### JSON Schema

```json
{
  "name": "Template Name",
  "description": "Description",
  "version": "1.0",
  "steps": [
    {
      "id": 1,
      "action": "click|double_click|key|hotkey|paste_text|type_text|wait",
      "target": [X, Y],  // For click actions
      "source": "{{VARIABLE}}",  // For paste_text
      "label": "Step description",
      "description": "Detailed description",
      "wait_after": 0.5  // Seconds
    }
  ]
}
```

### Available Actions

| Action | Target | Purpose |
|--------|--------|---------|
| `click` | [X, Y] | Click at coordinates |
| `double_click` | [X, Y] | Double-click |
| `key` | "delete" | Press single key |
| `hotkey` | "ctrl+a" | Key combination |
| `paste_text` | null | Paste from context |
| `type_text` | "text" | Type characters |
| `wait` | null | Wait (uses wait_after) |

### Context Variables

```
{{CURRENT_TEXT}}      - Text from data column
{{DIALOG_ID}}         - Dialog ID (key)
{{EXPORT_DIR}}        - Export directory path
{{LEVEL}}             - Level value
```

---

## 🛠️ Config File (config.yaml)

```yaml
general:
  theme: "darkly"
  base_output_path: "D:\\Output"
  auto_save_interval: 300

columns:
  key_column: 0
  language_map:
    1: "English"
    2: "Vietnamese"

levels:
  start: 1
  end: 10

timing:
  default_click_delay: 0.5
  default_render_wait: 6

api:
  provider: "edge-tts"
  voices:
    Vietnamese: "vi-VN-HoaiMyNeural"
    English: "en-US-JennyNeural"
  output_format: "mp3"

advanced:
  debug_mode: false
  log_level: "INFO"
  auto_backup: true
  retry_attempts: 2
```

---

## 🧪 Testing

### Unit Tests

```python
# Test API Engine
def test_api_export():
    engine = APIEngine()
    engine.set_voice("vi-VN-HoaiMyNeural")
    success = engine.export_single(
        dialog_id="test_001",
        text="Xin chào",
        export_dir="/tmp"
    )
    assert success
    assert os.path.exists("/tmp/test_001.mp3")

# Test Sequence Engine
def test_sequence_execute():
    engine = SequenceEngine()
    engine.load_template("/path/to/template.json")
    success = engine.run_for_dialog(
        dialog_id="test_001",
        text="Sample text",
        export_dir="/tmp"
    )
    assert success
```

### Integration Test

```python
# End-to-end test
def test_full_pipeline():
    # 1. Load data
    dm = DataManager()
    dm.auto_detect_source("test_data.xlsx")
    
    # 2. Export with API
    engine = APIEngine()
    data = dm.df.to_dict('records')
    engine.export_batch(data, "dialog_id", "text_english", "/tmp")
    
    # 3. Verify output
    assert os.path.exists("/tmp/intro_001.mp3")
    assert os.path.exists("/tmp/manifest.json")
```

---

## 🚀 Extension Points

### Adding New Language

```python
# In api_engine.py
VOICE_PRESETS = {
    "NewLanguage": [
        ("language-code-VoiceNeural", "Voice Name"),
        ...
    ]
}
```

### Adding New Export Format

```python
# In sequence_engine.py
def export_single(self, ...):
    # Add new format support
    if format == "wav":
        # Handle WAV export
    elif format == "flac":
        # Handle FLAC export
```

### Custom Action in Template

```python
# In sequence_engine.py - execute_step()
elif action == 'custom_action':
    # Implement custom action
    self._do_custom_action(target, context)
```

---

## 📊 Performance Optimization

### Smart Wait System

```python
def _smart_wait(self, wait_after, export_dir, dialog_id):
    """
    Instead of fixed delay:
    1. Check if file exists
    2. Verify file size is stable
    3. Return early if ready
    4. Fallback to delay if timeout
    """
    # Saves 30-40% time on export steps
```

### Async API Calls

```python
async def _synthesize_one(self, text, output_path, voice=None):
    """Async synthesis"""
    # Can parallelize multiple dialogs
    # Edge TTS API supports concurrent requests
```

### Session Management

```python
# Resume incomplete batch
session = SessionManager().load_session()
completed = set(session['completed_indices'])
# Only process uncompleted items
```

---

## 🐛 Debugging

### Enable Debug Mode

```yaml
# config.yaml
advanced:
  debug_mode: true
  log_level: "DEBUG"
```

### Inspect Template Execution

```python
# Use dry_run
engine.set_dry_run(True)
engine.run_for_dialog(...)  # Logs all steps, doesn't execute
```

### Check Logs

```
Log files:
- Console output (real-time)
- export_reporter.json (summary)
- errors.csv (failed items)
```

---

## 📦 Building Standalone Executable

```powershell
# Build with PyInstaller
pyinstaller TTS_Automation_Tool.spec

# Output: dist/TTS_Automation_Tool.exe
```

---

## 📚 Code Style & Conventions

```python
# Classes: PascalCase
class SequenceEngine:
    pass

# Functions/methods: snake_case
def export_single(self):
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3

# Private methods: _snake_case
def _smart_wait(self):
    pass

# Type hints (recommended)
def export_batch(
    self, 
    data_rows: List[Dict], 
    key_col: str
) -> bool:
    pass
```

---

**Document Version:** 1.0 | **Last Updated:** 25/02/2026

