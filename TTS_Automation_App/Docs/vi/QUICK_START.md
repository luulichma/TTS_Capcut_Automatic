# ⚡ Quick Start - Bắt Đầu Nhanh (5 Phút)

**Dành cho ai muốn chạy tool ngay mà không cần biết quá nhiều chi tiết.**

---

## 🎯 Mục Tiêu

Xuất 10 dòng thoại thành audio trong **5 phút** ✓

---

## 📋 Chuẩn Bị (2 phút)

### Bước 1: Tạo File Dữ Liệu

**Tùy chọn A: Dùng Excel**

Tạo file `data.xlsx` với nội dung:

```
dialog_id  | text_english      | level
-----------|-------------------|------
intro_001  | Hello             | 1
intro_002  | Welcome to game   | 1
intro_003  | Let's start       | 1
...
```

Lưu vào: `D:\Du_an_cong_ty\Data\data.xlsx`

**Tùy chọn B: Download Mẫu**

```
Có file mẫu sẵn:
D:\Du_an_cong_ty\TTS_Capcut_Automatic\TTS_Automation_App\samples\
```

### Bước 2: Chuẩn Bị Folder Output

```powershell
# PowerShell
mkdir D:\Du_an_cong_ty\Voice
```

---

## 🚀 Chạy Tool (3 phút)

### Step 1: Mở App

```powershell
cd D:\Du_an_cong_ty\TTS_Capcut_Automatic\TTS_Automation_App
python main.py
```

### Step 2: Load Dữ Liệu

```
1. Tab "Data Panel"
2. Nhập đường dẫn: D:\Du_an_cong_ty\Data\data.xlsx
3. Click [📁] để browse (nếu không muốn gõ)
4. Chọn file
5. Click [⬇️ Tải dữ liệu]

✓ Kết quả: "✅ Đã tải X dòng dữ liệu"
```

### Step 3: Gán Ngôn Ngữ

```
Bạn sẽ thấy:
[ dialog_id → Chọn (Key/ID) ]
[ text_english → Chọn English ]  ✓
[ level → Chọn (Bỏ qua) ]

(App sẽ tự động detect)
```

### Step 4: Chọn Chế Độ

**Nếu muốn NHANH nhất (khuyên dùng):**

```
1. Click Tab "API Export"
2. Language: English (mặc định)
3. Voice: Jenny (mặc định)
4. Output dir: D:\Du_an_cong_ty\Voice
5. Click [▶ Run]
6. Chờ 2-3 phút ✓

→ Hoàn tất! Audio lưu vào D:\Du_an_cong_ty\Voice\en\
```

**Nếu muốn tích hợp vào CapCut:**

```
1. Mở CapCut Desktop (chuẩn bị project sẵn)
2. Click Tab "CapCut Mode"
3. Language: English
4. Timing: Fast (🚀)
5. Output dir: D:\Du_an_cong_ty\Voice
6. Click [▶ Run]
7. Chờ 10-15 phút ✓

→ Hoàn tất! Audio tích hợp trong CapCut
```

---

## ✅ Kiểm Tra Kết Quả

```
Nếu thành công:
✓ Folder D:\Du_an_cong_ty\Voice\ có file .mp3
✓ Log hiển thị ✅ Hoàn tất!
✓ Có thể nghe thử file audio

Nếu có lỗi:
✗ Kiểm tra log (xem phần Troubleshooting)
✗ Hoặc xem file HUONG_DAN_SU_DUNG.md
```

---

## 🎯 Lần Sau (Nhanh Hơn)

```
Nếu muốn export thêm dữ liệu khác:

1. Tạo file Excel mới
2. Lặp lại Step 2-4 trên
3. Hoặc: Dùng Profiles
   - Lần đầu: Click [💾 Save Profile]
   - Lần sau: Chọn profile → Settings restore tự động
```

---

## 📞 SOS - Nếu Gặp Lỗi

### Lỗi: "File not found"
```
→ Kiểm tra đường dẫn file có đúng không
→ Hoặc dùng nút [📁] để browse
```

### Lỗi: "Chưa chọn ngôn ngữ"
```
→ Quay lại Data Panel
→ Gán ngôn ngữ cho ít nhất 1 cột text
→ Click "Tải dữ liệu" lại
```

### Lỗi: "API Error / Network"
```
→ Kiểm tra internet connection
→ Chờ vài phút rồi thử lại
```

### Audio quá nhỏ/lỗi (CapCut mode)
```
→ Click [⚙️ Settings]
→ Advanced → Retry attempts: 3
→ Chạy lại với [🔄 Retry]
```

---

## 💡 Tips Nhanh

```
⚡ Tất cả tùy chọn mặc định đều OK
⚡ Chỉ nhập: File + Folder output + Click Run
⚡ Dùng "🔊 Thử" để test giọng trước
⚡ Dùng "🔍 Dry Run" để test template (CapCut)
⚡ Log sẽ hiển thị tiến độ real-time
```

---

## 📊 Bảng So Sánh Chế Độ

| Yếu Tố | API Export | CapCut Mode |
|--------|-----------|------------|
| **Tốc độ** | ⚡⚡⚡ (2-3 min) | ⚡ (15-20 min) |
| **Khó** | Dễ | Vừa |
| **Tích hợp** | ❌ | ✅ |
| **Chất lượng** | 🔊 Rất tốt | 🔊 Rất tốt |

→ **Lần đầu: Dùng API Export** (nhanh, dễ)

---

## 🎉 Xong!

**Bạn vừa hoàn thành export audio tự động!**

```
Next steps:
1. Thử với dữ liệu khác
2. Đọc file HUONG_DAN_SU_DUNG.md để biết thêm
3. Xem CAIDAT_CHI_TIET.md để tối ưu
4. Enjoy! 🚀
```

---

**Cần giúp? Xem HUONG_DAN_SU_DUNG.md hoặc CAIDAT_CHI_TIET.md**
