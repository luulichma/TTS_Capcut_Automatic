# ⚙️ Hướng Dẫn Cấu Hình & Setup Chi Tiết

---

## 📋 Mục Lục

1. [Chuẩn Bị Ban Đầu](#chuẩn-bị-ban-đầu)
2. [Cấu Hình File Dữ Liệu](#cấu-hình-file-dữ-liệu)
3. [Cấu Hình CapCut Mode](#cấu-hình-capcut-mode)
4. [Cấu Hình API Mode](#cấu-hình-api-mode)
5. [Cấu Hình Template](#cấu-hình-template)
6. [Tối Ưu Performance](#tối-ưu-performance)

---

## 🛠️ Chuẩn Bị Ban Đầu

### 1.1 Kiểm Tra Python

```powershell
# Mở PowerShell, gõ:
python --version

# Kết quả mong đợi:
# Python 3.10.0 trở lên ✓
```

### 1.2 Cài Đặt Thư Viện

```powershell
# Navigates tới folder project
cd D:\Du_an_cong_ty\TTS_Capcut_Automatic\TTS_Automation_App

# Cài tất cả dependencies
pip install -r requirements.txt

# Kiểm tra (tùy chọn)
pip list | findstr "pandas pyautogui edge-tts"
```

### 1.3 Tạo Folder Output

```powershell
# Tạo folder lưu audio (nếu chưa tồn tại)
mkdir D:\Du_an_cong_ty\Voice

# Hoặc dùng file explorer
# D:\Du_an_cong_ty → New Folder → "Voice"
```

---

## 📊 Cấu Hình File Dữ Liệu

### 2.1 Format File Excel

**Tệp phải có các cột sau:**

```
┌──────────────┬──────────────────┬─────────────────┬───────┐
│ dialog_id    │ text_english     │ text_vietnamese │ level │
├──────────────┼──────────────────┼─────────────────┼───────┤
│ intro_001    │ Welcome to game  │ Chào mừng      │ 1     │
│ intro_002    │ Let's start      │ Bắt đầu nào    │ 1     │
│ menu_001     │ Play             │ Chơi game      │ 2     │
│ menu_002     │ Settings         │ Cài đặt        │ 2     │
│ end_001      │ Game over        │ Kết thúc       │ 3     │
└──────────────┴──────────────────┴─────────────────┴───────┘
```

**Requirements:**
- ✓ Cột 1: **dialog_id** (Key duy nhất, không trùng lặp)
- ✓ Các cột text: Tối thiểu 1 cột (English, Vietnamese, ...)
- ✓ Cột Level: Tùy chọn (dùng để phân loại)
- ✓ **Không có row trống** giữa dữ liệu
- ✓ **Bỏ qua 2 dòng đầu** (header + metadata)

### 2.2 Export Từ Google Sheets

```
1. Mở Google Sheets
2. Chuẩn bị dữ liệu format trên
3. File → Download → Excel (.xlsx)
4. Lưu vào D:\Du_an_cong_ty\Data\
```

### 2.3 Kiểm Tra Dữ Liệu

```
Mở file trong Excel:
✓ Có ít nhất 1 cột text không trống
✓ dialog_id không trùng lặp
✓ Text không quá dài (< 500 ký tự)
✓ Không có ký tự đặc biệt lạ
```

---

## 🎬 Cấu Hình CapCut Mode

### 3.1 Chuẩn Bị Project CapCut

```
1. Mở CapCut Desktop
2. Tạo NEW project:
   ├─ Title: "TTS_Template" (tuỳ ý)
   ├─ Tạo 1 TEXT element
   │   └─ Nội dung: "Sample text"
   ├─ Tạo 1 AUDIO track trống
   └─ Lưu project

3. Ghi nhớ vị trí các element:
   ├─ Text element: Đâu trên timeline?
   ├─ Audio track: Đâu trên timeline?
   └─ (Dùng để calibrate coordinates)
```

### 3.2 Calibrate Template Coordinates

**Cách 1: Dùng Built-in Coordinate Tool**

```
1. Chạy app → Data Panel → Load file
2. Tab "CapCut Mode" → Nút [🎯 Pick Coords]
3. Click nút → Màn hình sẽ hiển thị grid tọa độ
4. Di chuột tới element trong CapCut
5. Ghi nhớ (X, Y) hiển thị
6. Copy vào template JSON
```

**Cách 2: Tìm Bằng Tay**

```
Template JSON:
{
  "id": 1,
  "action": "click",
  "target": [X, Y],
  "label": "Click Audio Timeline"
}

Steps để tìm X, Y:
1. Mở CapCut, tìm vị trí element
2. Đếm pixel từ góc trái (X) và trên (Y)
3. Hoặc dùng inspect tool Windows:
   - Nhấn Windows Key + Shift + S (Screenshot tool)
   - Đặt cursor trên vị trí → Ghi X, Y
```

### 3.3 Các Template Sẵn Có

```
Trong folder templates/:

1. capcut_tts_default.json
   └─ Template mặc định, hỗ trợ tất cả

2. capcut_pc_tts.json
   └─ Template tối ưu cho CapCut PC

Cách sử dụng:
- App sẽ auto-load template
- Hoặc bạn có thể load thủ công:
  CapCut Panel → [📂 Load] → Chọn file .json
```

### 3.4 Tối Ưu Template

**Nếu tool quá chậm:**

```json
{
  "id": 11,
  "label": "Bắt đầu đọc (Start Reading)",
  "wait_after": 6.0
  // ↓ Giảm xuống
  // "wait_after": 5.0
}
```

**Giảm các delays nhỏ:**

```json
// Thay
"wait_after": 1.0
// Thành
"wait_after": 0.8
```

**Nếu có lỗi "file not found":**

```json
// Tăng wait time:
{
  "id": 23,
  "label": "Xác nhận Export",
  "wait_after": 10.0
  // ↓ Tăng nếu vẫn lỗi
  // "wait_after": 12.0
}
```

---

## 🌐 Cấu Hình API Mode

### 4.1 Chọn Ngôn Ngữ & Giọng

**Bảng Giọng Đọc Tương Ứng:**

```
Vietnamese:
  ├─ vi-VN-HoaiMyNeural (Nữ, khuyên dùng)
  └─ vi-VN-NamMinhNeural (Nam)

English:
  ├─ en-US-JennyNeural (Nữ, khuyên dùng)
  ├─ en-US-GuyNeural (Nam)
  ├─ en-US-AriaNeural (Nữ, tự nhiên)
  ├─ en-GB-SoniaNeural (Nữ, UK accent)
  └─ en-GB-RyanNeural (Nam, UK accent)

Japanese:
  ├─ ja-JP-NanamiNeural (Nữ)
  └─ ja-JP-KeitaNeural (Nam)

Korean:
  ├─ ko-KR-SunHiNeural (Nữ)
  └─ ko-KR-InJoonNeural (Nam)

Chinese:
  ├─ zh-CN-XiaoxiaoNeural (Nữ, Mandarin)
  └─ zh-CN-YunxiNeural (Nam, Mandarin)
```

### 4.2 Cấu Hình config.yaml

```yaml
api:
  provider: "edge-tts"          # Luôn là edge-tts
  voices:
    Vietnamese: "vi-VN-HoaiMyNeural"
    English: "en-US-JennyNeural"
  output_format: "mp3"          # hoặc "wav"
```

### 4.3 Test Giọng Trước

```
UI: API Panel → Nút [🔊 Thử]
↓
Sẽ phát 1 câu mẫu
↓
Kiểm tra có ổn không
↓
Nếu OK → Click [▶ Run] để export batch
```

---

## 📝 Cấu Hình Template

### 5.1 Cấu Trúc Template JSON

```json
{
  "name": "My Custom Template",
  "description": "Mô tả template",
  "version": "1.0",
  "steps": [
    {
      "id": 1,
      "action": "click",
      "target": [X, Y],
      "label": "Mô tả bước này",
      "description": "Chi tiết hơn",
      "wait_after": 0.5
    },
    {
      "id": 2,
      "action": "hotkey",
      "target": "ctrl+a",
      "label": "Select All",
      "wait_after": 0.2
    },
    {
      "id": 3,
      "action": "paste_text",
      "source": "{{CURRENT_TEXT}}",
      "label": "Paste text từ data",
      "wait_after": 1.0
    }
  ]
}
```

### 5.2 Các Actions Có Sẵn

```
1. "click"
   target: [X, Y]
   → Click tại vị trí (X, Y)

2. "double_click"
   target: [X, Y]
   → Double-click

3. "key"
   target: "delete"
   → Nhấn 1 phím (delete, enter, etc.)

4. "hotkey"
   target: "ctrl+a"
   → Tổ hợp phím (Ctrl+A, Ctrl+C, etc.)

5. "paste_text"
   source: "{{CURRENT_TEXT}}"
   → Paste nội dung (hỗ trợ {{VARIABLES}})

6. "type_text"
   target: "Some text"
   → Type text từng ký tự

7. "wait"
   → Đợi (wait_after sẽ được dùng)
```

### 5.3 Template Variables

```
{{CURRENT_TEXT}}
  → Text từ cột dữ liệu
  → Ví dụ: "Welcome to game"

{{DIALOG_ID}}
  → ID của dialog
  → Ví dụ: "intro_001"

{{EXPORT_DIR}}
  → Đường dẫn thư mục export
  → Ví dụ: "D:\Du_an_cong_ty\Voice\vi"

{{LEVEL}}
  → Level của dialog
  → Ví dụ: "1"
```

### 5.4 Lưu Custom Template

```
1. Chỉnh sửa template trong CapCut Panel
2. Click [💾 Save] → Lưu vào file
3. Hoặc [📝 Save As] → Lưu với tên khác

Kỳ sau:
- Click [📂 Load] → Chọn file vừa lưu
- Template sẽ được load
```

---

## 🚀 Tối Ưu Performance

### 6.1 Tăng Tốc CapCut Mode

**Option 1: Timing Preset**
```
Normal (1x)  →  Nhanh, ổn định
    ↓
Fast (0.5x)  →  Nhanh 2x, nếu ok thì dùng cái này
    ↓
Slow (2x)    →  Chậm, để debug khi có lỗi
```

**Option 2: Giảm Wait Times**
```json
// Trước
"wait_after": 6.0

// Sau
"wait_after": 4.0

// Kiểm tra có lỗi không, nếu ok thì giảm tiếp
```

**Option 3: Smart Wait** ✨
```
(Đã built-in!)
- Auto detect file export thay vì delay cứng
- Tiết kiệm 30-40% thời gian nếu audio render nhanh
```

### 6.2 Tăng Tốc API Mode

**Nhanh sẵn rồi!** 
```
- 28 dialogs: ~2-3 phút
- Dùng MP3 thay vì WAV (nhẹ hơn)
```

### 6.3 Batch Processing

```
Nếu có 1000 dialogs:

1. Chia thành 5 batch (200 dialogs/lần)
2. Chạy batch 1 → Lưu session
3. Nghỉ 5 phút
4. Chạy batch 2 (app sẽ auto-resume)
5. ... (tiếp tục)

→ Tránh lỗi, máy không quá nóng
```

### 6.4 Cấu Hình Threads

```yaml
# config.yaml
performance:
  max_concurrent_exports: 3
  # Nếu máy mạnh: tăng lên 5
  # Nếu máy yếu: giảm xuống 1-2
```

---

## 📊 Monitoring & Logging

### 7.1 Xem Real-time Log

```
App sẽ hiển thị:
🚀 Bắt đầu...
📝 Xử lý dialog_001
✅ Hoàn thành
⚠️ Cảnh báo
❌ Lỗi

Mỗi dòng có color code ✓
```

### 7.2 Bật Debug Mode

```yaml
# config.yaml
advanced:
  debug_mode: true
  log_level: "DEBUG"
```

Khi bật:
```
- Log chi tiết hơn
- Thông tin timing của mỗi step
- Memory usage
- File size khi export
```

### 7.3 Export Report

```
Sau khi xong, tạo:
├─ manifest.json
│   ├─ Tổng files
│   ├─ Success count
│   ├─ Error count
│   └─ Elapsed time
│
├─ errors.csv
│   ├─ dialog_id
│   ├─ error message
│   └─ timestamp
│
└─ export_report.json
    ├─ Chi tiết từng file
    ├─ File size
    └─ Status
```

---

## 🔧 Troubleshooting Cấu Hình

### Lỗi: "Template không load"
```
Giải pháp:
1. Kiểm tra file JSON có valid không:
   - JSON online validator
   - Hoặc: python -m json.tool template.json

2. Đảm bảo file nằm trong templates/
3. Click [📂 Load] → Chọn file
```

### Lỗi: "Coordinates sai"
```
Giải pháp:
1. Click [🎯 Pick Coords]
2. Mở CapCut lên
3. Di chuột tới đúng vị trị element
4. Ghi X, Y, thay trong template
5. Test với 1 dialog trước (Dry Run)
```

### Lỗi: "Audio bị cut off"
```
Giải pháp:
1. Tăng "Start Reading" wait time:
   "wait_after": 8.0  (thay vì 6.0)
2. Kiểm tra text không quá dài
3. Thử giọng khác
```

---

## ✅ Checklist Cấu Hình

```
□ Python 3.10+ cài đặt
□ requirements.txt installed
□ Folder D:\Du_an_cong_ty\Voice/ tạo sẵn
□ File dữ liệu format đúng
□ Dialog ID không trùng lặp
□ Ít nhất 1 cột text được gán
□ (CapCut) CapCut Desktop cài sẵn
□ (CapCut) Project mẫu tạo xong
□ (CapCut) Template coordinates calibrate
□ (API) Internet connection OK
□ config.yaml cập nhật đường dẫn output
□ Thử test với 5 dialogs trước
□ Review log không có lỗi
□ Chạy batch chính thức ✓
```

---

**Bạn đã sẵn sàng! Hãy bắt đầu sử dụng tool 🚀**

