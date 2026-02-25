# 📖 Hướng Dẫn Sử Dụng TTS Automation Tool

**Version:** 1.0 | **Ngày cập nhật:** 25/02/2026

---

## 🎯 Tổng Quan

**TTS Automation Tool** là một ứng dụng tự động hóa Text-to-Speech (chuyển text thành audio) với 2 chế độ:

### Chế độ 1: **API Export** (Miễn phí, Nhanh) ⭐
- Sử dụng Edge TTS (API miễn phí từ Microsoft)
- **Ưu điểm:** Nhanh, không cần CapCut, hỗ trợ 50+ ngôn ngữ
- **Nhược điểm:** Chỉ tạo audio, không tích hợp vào project

### Chế độ 2: **CapCut Automation** (Tích hợp Project) 🎬
- Tự động hóa UI CapCut Desktop
- **Ưu điểm:** Audio tích hợp trực tiếp vào project, dễ dàng chỉnh sửa sau
- **Nhược điểm:** Chậm hơn (15-20 phút cho 28 dòng)

---

## 📥 Cài Đặt & Khởi Động

### Bước 1: Chuẩn Bị
```
Yêu cầu:
✓ Python 3.10+
✓ CapCut Desktop (nếu dùng chế độ CapCut)
✓ File Excel/CSV chứa dữ liệu
```

### Bước 2: Cài Đặt Thư Viện
```powershell
# Mở terminal, cd tới folder TTS_Automation_App
cd D:\Du_an_cong_ty\TTS_Capcut_Automatic\TTS_Automation_App

# Cài đặt dependencies
pip install -r requirements.txt
```

### Bước 3: Chạy Ứng Dụng
```powershell
python main.py
```

Cửa sổ giao diện sẽ mở lên 🎉

---

## 🎮 Giao Diện Chính

```
┌─ TTS Automation Tool ──────────────────────────────────────┐
│                                                             │
│  📊 Tab 1: Data Panel (Tải dữ liệu)                       │
│  ┌────────────────────────────────────────────────────┐   │
│  │ 📂 Nguồn dữ liệu: [Nhập file Excel/CSV]  [📁]    │   │
│  │ 🔤 Gán ngôn ngữ cho cột: C1=Key, C2=English...   │   │
│  │ 👁️ Xem trước dữ liệu                             │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  📋 Tab 2: CapCut Mode / API Mode (Chọn chế độ)           │
│  ┌────────────────────────────────────────────────────┐   │
│  │ [⏱️ Tốc độ] [🔍 Dry Run] [⏱️ Đếm ngược]         │   │
│  │ [🌐 Ngôn ngữ] [📁 Thư mục] [⚙️ Level]           │   │
│  └────────────────────────────────────────────────────┘   │
│                                                             │
│  ⚙️ Settings | 💾 Save Profile | 📋 Log                   │
│  [◀ Pause] [▶ Run] [⏹ Stop] [❌ Errors]                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Quy Trình Cơ Bản

### Step 1️⃣: Tải Dữ Liệu

**Data Panel → Bước 1: Chọn File**

```
1. Click nút [📁]
2. Chọn file Excel hoặc CSV chứa dữ liệu
3. File phải có format:
   ┌─────────────────────────────────────┐
   │ dialog_id  │ text_english │ level   │
   ├─────────────────────────────────────┤
   │ intro_001  │ Hello       │ 1       │
   │ intro_002  │ Welcome     │ 1       │
   │ menu_001   │ Play Game   │ 2       │
   └─────────────────────────────────────┘
```

**Bước 2: Gán Ngôn Ngữ Cho Cột**

```
Bạn sẽ thấy:
├─ Cột A (dialog_id)      → Chọn "(Key/ID)"
├─ Cột B (text_english)   → Chọn "English"
├─ Cột C (text_vietnamese) → Chọn "Vietnamese"
└─ Cột D (level)          → Chọn "(Bỏ qua)"

Hệ thống sẽ tự động detect ✓
```

**Bước 3: Tải Dữ Liệu**

```
⬇️ Click "Tải dữ liệu" → Hệ thống sẽ load file
✅ Kết quả: "Đã tải 28 dòng dữ liệu"
```

---

## 🎬 Chế Độ 1: CapCut Automation

**Dành cho:** Export audio trực tiếp vào project CapCut

### Chuẩn Bị

```
1. Mở CapCut Desktop
2. Tạo 1 project mẫu với:
   - 1 text element
   - 1 audio timeline
   (Tool sẽ tự động update text + export audio)

3. Ghi nhớ vị trí trên màn hình của:
   - Nút "Start Reading"
   - Nút "Export"
   (Dùng để calibrate coordinates)
```

### Cách Sử Dụng

```
1. Chọn Tab "CapCut Mode"
   ├─ 🌐 Ngôn ngữ: Chọn "Vietnamese" hoặc "English"
   ├─ ⏱️ Tốc độ: 
   │   ├─ 🐌 Slow: Chậm (2x) - dễ dàng observe
   │   ├─ ⚡ Normal: Bình thường (1x) - cân bằng
   │   └─ 🚀 Fast: Nhanh (0.5x) - tiết kiệm time
   ├─ 📁 Thư mục: Chọn nơi lưu audio
   └─ 📊 Level: Chọn level nào (để "All" là export tất cả)

2. Review Template (nếu cần)
   - Tab "CapCut Mode" → Xem "Chuỗi tương tác"
   - Không cần chỉnh nếu chưa biết

3. Click [▶ Run] để bắt đầu
   ├─ Countdown 5 giây (chuẩn bị)
   ├─ Hệ thống sẽ tự động:
   │   ├─ Update text
   │   ├─ Click "Start Reading"
   │   ├─ Chờ audio render (smart detect ✨)
   │   └─ Export file MP3
   └─ Log sẽ hiển thị tiến độ

4. Sau khi xong:
   ✅ Audio được lưu vào: D:\Du_an_cong_ty\Voice\vi\
   ✅ Project CapCut có audio mới
```

**Ví Dụ Kết Quả:**

```
D:\Du_an_cong_ty\Voice\
├─ vi/  (Vietnamese)
│  ├─ intro_001.mp3
│  ├─ intro_002.mp3
│  └─ menu_001.mp3
└─ en/  (English)
   ├─ intro_001.mp3
   └─ ...
```

---

## 🌐 Chế Độ 2: API Export

**Dành cho:** Xuất audio nhanh mà không cần CapCut

### Cách Sử Dụng

```
1. Chọn Tab "API Export"
   ├─ Ngôn ngữ: Chọn "Vietnamese", "English", v.v.
   ├─ Giọng đọc: 
   │   ├─ Vietnamese: Hoài My (Nữ) / Nam Minh (Nam)
   │   ├─ English: Jenny (Nữ) / Guy (Nam)
   │   └─ ... (50+ options)
   ├─ Định dạng: MP3 hoặc WAV
   ├─ 💾 Backup: Tự động backup file cũ
   └─ 📊 Level: Chọn level

2. Click [🔊 Thử] để test giọng
   - Sẽ tự động phát 1 câu mẫu

3. Click [▶ Run]
   ├─ Hệ thống sẽ:
   │   ├─ Lấy từng text từ cột
   │   ├─ Gọi Edge TTS API
   │   ├─ Lưu file MP3
   │   └─ Hiển thị tiến độ
   └─ Nhanh hơn CapCut (~ 2-3 phút cho 28 dòng)

4. Kết quả:
   ✅ Audio được lưu vào: D:\Du_an_cong_ty\Voice\en\
   ✅ Manifest.json được tạo (báo cáo chi tiết)
   ✅ Lỗi được ghi vào: errors.csv
```

**So Sánh 2 Chế Độ:**

| Yếu Tố | CapCut Mode | API Mode |
|--------|-----------|----------|
| **Tốc độ** | 15-20 phút | 2-3 phút |
| **Chất lượng** | 🔊 CapCut TTS | 🔊 Edge TTS |
| **Tích hợp** | ✅ (Trong project) | ❌ (File riêng) |
| **Có internet** | Không cần | Cần |
| **Tuỳ chỉnh giọng** | ✅ (Trong CapCut) | ✅ (Panel) |

---

## 🎯 Các Tính Năng Nâng Cao

### 1. **Dry Run** (Mô Phỏng)
```
✓ Click checkbox "🔍 Dry Run" để test
- Sẽ mô phỏng tất cả bước mà không thực thi
- Dùng để check xem steps có đúng không
```

### 2. **Retry** (Thử Lại)
```
Nếu có lỗi:
1. Xem log → Click [❌ Errors (n)]
2. Chỉnh sửa nếu cần
3. Click [🔄 Retry] → Chỉ retry items bị lỗi
```

### 3. **Profiles** (Lưu Cấu Hình)
```
1. Cấu hình xong (chọn file, language, v.v.)
2. Click [💾 Save Profile]
3. Đặt tên: "Profile_Vietnamese" 
4. Lần sau: Chọn profile → Tất cả setting sẽ restore
```

### 4. **Session Resume** (Tiếp Tục)
```
Nếu chương trình crash hoặc bị dừng:
- Lần tiếp theo: Pop-up sẽ hỏi "Tiếp tục session cũ?"
- Click "Yes" → Chỉ export những items chưa xong
```

---

## 📊 Đọc Log & Debug

### Log Colors

```
🟢 ✅ Thành công     → Màu xanh
🔴 ❌ Lỗi           → Màu đỏ
🟠 ⚠️ Cảnh báo      → Màu cam
🔵 🚀 Bắt đầu      → Màu xanh lam
⚫ ⏭️ Bỏ qua        → Màu xám
```

### Ví Dụ Log

```
🚀 Bắt đầu CapCut Automation — Vietnamese
📝 Xử lý: intro_001
  → Click Audio Timeline
  → Xóa audio cũ
  → Click Text Timeline
  → Dán nội dung mới
  → Click "Start Reading"
  ⏳ Chờ file export: intro_001...
  ✅ File đã export trong 4.2s       (Smart Wait ✨)
✅ Hoàn thành: intro_001
🏁 LEVEL 1 → D:\Du_an_cong_ty\Voice\vi

🎉 Hoàn tất! ⏱ 12 phút 34 giây
```

---

## ⚙️ Settings (Cấu Hình Nâng Cao)

Click [⚙️ Settings] để:

```
📊 Display:
  ├─ Theme: Darkly / Light / ...
  └─ Auto-save interval

⚡ Performance:
  ├─ Max concurrent exports
  └─ Timing multiplier

🔔 Notifications:
  ├─ Sound on complete
  ├─ Windows notification
  └─ Error popup

🔧 Advanced:
  ├─ Debug mode
  ├─ Log level: DEBUG / INFO / WARNING
  ├─ Auto backup: On/Off
  └─ Retry attempts: 1-5
```

---

## 🆘 Troubleshooting

### ❌ Lỗi: "Không tải được file"
```
Nguyên nhân: File không tồn tại hoặc format sai
Giải pháp:
1. Kiểm tra đường dẫn file
2. Đảm bảo file là Excel (.xlsx) hoặc CSV (.csv)
3. File phải có header row
```

### ❌ Lỗi: "Chưa chọn ngôn ngữ"
```
Nguyên nhân: Quên gán ngôn ngữ cho cột
Giải pháp:
1. Vào Data Panel
2. Chọn ít nhất 1 cột → Gán ngôn ngữ
3. Click "Tải dữ liệu"
```

### ❌ CapCut Mode chậm
```
Nguyên nhân: Delay quá lâu hoặc template sai
Giải pháp:
1. Chọn "🚀 Fast" preset thay vì "Normal"
2. Kiểm tra template coordinates (nếu biết)
3. Dùng "🔍 Dry Run" để test trước
```

### ❌ API Mode lỗi "Network"
```
Nguyên nhân: Không có internet hoặc API quá tải
Giải pháp:
1. Kiểm tra internet connection
2. Chờ vài phút rồi retry
3. Nếu vẫn lỗi: Chuyển sang CapCut mode
```

### ⚠️ File MP3 quá nhỏ (< 10KB)
```
Nguyên nhân: Audio render không hoàn tất
Giải pháp:
1. Tăng "Start Reading" wait time lên (settings)
2. Chạy lại retry
3. Kiểm tra CapCut project có lỗi không
```

---

## 💡 Mẹo & Best Practices

### ✨ Tối Ưu Tốc Độ

**CapCut Mode:**
```
1. Chọn "🚀 Fast" preset
   → Tốc độ nhanh lên 2x
   
2. Nếu audio render nhanh (< 5s):
   → Smart Wait sẽ detect sớm
   → Tự động tiết kiệm 30-40%
   
3. Test với 5-10 dialogs trước
   → Đảm bảo ổn định
```

**API Mode:**
```
1. Dùng MP3 (nhẹ hơn WAV)
2. Nếu toàn bộ cột cùng 1 ngôn ngữ:
   → Xuất hết 1 lần
   → Nhanh hơn CapCut 10x
```

### 🎯 Chất Lượng Tốt

**CapCut Mode:**
```
1. Điều chỉnh text trong CapCut trước
   → Đảm bảo phát âm đúng

2. Test giọng với vài câu mẫu
   → Kiểm tra tone/speed

3. Chọn "⚡ Normal" thay vì Fast
   → Ít bị lỗi render
```

**API Mode:**
```
1. Test giọng: Click [🔊 Thử]
   → Nghe thử trước

2. Nếu text có dấu câu lạ:
   → Sửa trong file trước

3. Chọn giọng phù hợp
   → Nữ: Hoài My, Jenny, ...
   → Nam: Nam Minh, Guy, ...
```

### 📁 Quản Lý File

```
Cấu Trúc Recommended:
D:\Du_an_cong_ty\
├─ Data\
│  ├─ original_data.xlsx
│  ├─ edited_data.xlsx
│  └─ backup_data.xlsx
├─ Voice\          (Output folder)
│  ├─ vi\
│  ├─ en\
│  └─ manifest.json
└─ Logs\
   ├─ errors.csv
   └─ export_report.json
```

---

## 📞 FAQ

**Q: Có thể export 2 ngôn ngữ cùng lúc không?**
```
A: CapCut Mode: Phải chạy 2 lần (1 lần/ngôn ngữ)
   API Mode: Có thể tạo batch ngôn ngữ (sắp tới)
```

**Q: Audio bị trễ trong CapCut?**
```
A: 1. Kiểm tra Setting "Start Reading" wait time
   2. Hoặc update coordinates nếu CapCut update
```

**Q: Có thể tạo voice riêng không?**
```
A: CapCut Mode: Dùng voice CapCut built-in
   API Mode: Chọn từ 50+ voices của Edge TTS
   Custom: Không hỗ trợ (sắp tới)
```

**Q: Chạy liên tục 24h được không?**
```
A: Có thể, nhưng khuyến khích chạy 1-2 batch/lần
   Dừng 30 phút giữa các batch để máy cool down
```

---

## 📝 Shortcuts (Phím Tắt)

```
Ctrl + Return  →  Chạy (▶ Run)
Ctrl + L       →  Focus vào data source
Spacebar       →  Pause/Resume (khi đang chạy)
Escape         →  Dừng (⏹ Stop)
```

---

## 📞 Hỗ Trợ & Phản Hồi

```
Nếu gặp lỗi:
1. Kiểm tra troubleshooting section trên
2. Xem log chi tiết (copy text log)
3. Lưu file errors.csv
4. Liên hệ với đội support
```

---

## 🎉 Chúc Mừng!

**Bạn đã sẵn sàng sử dụng TTS Automation Tool!**

```
Next Steps:
1. Load dữ liệu của bạn
2. Thử chế độ API Mode (nhanh, dễ)
3. Nếu OK → Chuyển sang CapCut Mode (tích hợp)
4. Tối ưu settings theo nhu cầu của bạn

Happy Automating! 🚀✨
```

---

**Phiên bản:** 1.0 | **Cập nhật:** 25/02/2026 | **Trạng thái:** ✅ Ổn định
