# QUY ƯỚC QUẢN LÝ & ĐẶT TÊN DỮ LIỆU (DATA CONVENTION)

> **Dự án**: Hệ thống Quản lý Xe Ra Vào Đại học Vinh bằng Thị giác Máy tính  
> **Mục tiêu**: Chuẩn hóa dữ liệu video/ảnh và thiết lập chiến lược chia tập Train/Val/Test theo thời gian (**Temporal Split**) nhằm triệt tiêu hoàn toàn rò rỉ dữ liệu (**Data Leakage**).

---

## 1. Phân chia Khu vực Bãi đỗ xe Đại học Vinh

* **`nhaxe1`**: **Khu vực Nhà xe Máy** (phục vụ sinh viên, giảng viên đi xe máy/xe đạp điện - đặc thù biển số 2 dòng).
* **`nhaxe2`**: **Khu vực Bãi đỗ Ô tô** (khuôn viên bãi đỗ ô tô cán bộ, giảng viên, khách - đặc thù biển số 1 dòng).

---

## 2. Quy tắc Đặt tên File Video Gốc (`data/raw/`)

Cú pháp chuẩn hóa:
```text
[khu_vuc]_[loai_xe]_[lan_xe]_[YYYYMMDD]_[buoi/gio]_[so_thu_tu].mp4
```

### Bảng giải thích chi tiết các trường:

| Trường | Định dạng / Giá trị | Ý nghĩa nghiệp vụ |
| :--- | :--- | :--- |
| **`[khu_vuc]`** | `nhaxe1` / `nhaxe2` | Nhà xe 1 (Xe máy) hoặc Nhà xe 2 (Ô tô) |
| **`[loai_xe]`** | `xemay` / `oto` | Phân loại phương tiện |
| **`[lan_xe]`** | `vao` / `ra` | Hướng di chuyển tại cổng kiểm soát (Làn Vào / Làn Ra) |
| **`[YYYYMMDD]`**| `20261019`, `20261020`... | **Ngày quay thực tế** (Năm-Tháng-Ngày) |
| **`[buoi/gio]`**| `sang` (sáng), `chieu` (chiều), `toi` (tối) hoặc `0730`, `1130` | **Thời điểm / Ca quay** trong ngày |
| **`[so_thu_tu]`**| `001`, `002`, `003`... | Số thứ tự video trong cùng ca quay (3 chữ số) |

### Ví dụ áp dụng thực tế:
* `nhaxe1_xemay_vao_20261019_sang_001.mp4` : Video làn vào nhà xe máy, quay sáng ngày 19/10/2026, file 1.
* `nhaxe1_xemay_ra_20261019_chieu_001.mp4`  : Video làn ra nhà xe máy, quay chiều ngày 19/10/2026, file 1.
* `nhaxe2_oto_vao_20261020_0730_001.mp4`   : Video làn vào ô tô, quay lúc 7h30 sáng 20/10/2026, file 1.
* `nhaxe2_oto_ra_20261020_1700_001.mp4`    : Video làn ra ô tô, quay lúc 17h00 chiều 20/10/2026, file 1.

---

## 3. Chiến lược Phân chia Dữ liệu Tránh Rò rỉ (Temporal Data Splitting)

### ⚠️ Nguy cơ Rò rỉ Dữ liệu (Data Leakage) trong Bài toán Thị giác Máy tính Video:
* Khi quay một chiếc xe di chuyển qua cổng, camera sẽ thu được từ **15 đến 60 khung hình liên tiếp** của cùng chiếc xe/biển số đó.
* **Sai lầm phổ biến**: Nếu trích xuất toàn bộ ảnh rồi xáo trộn ngẫu nhiên (**Random Shuffle**) để chia 80% Train - 20% Test, thì các khung hình của cùng 1 xe sẽ xuất hiện ở CẢ HAI tập Train và Test.  
  $\Rightarrow$ Kết quả: Mô hình bị "học vẹt" (overfitting), chỉ số đánh giá trên tập Test cao ảo nhưng khi đưa vào vận hành thực tế gặp xe lạ thì tỉ lệ nhận diện rớt thảm hại!

### ✅ Giải pháp: Phân chia theo Dòng Thời gian (Temporal / Session-based Split):
Dữ liệu sẽ được gom nhóm (**Grouped by Video / Date Session**) và phân chia theo các ngày hoặc ca quay hoàn toàn độc lập:

```text
Toàn bộ Dữ liệu Video / Ảnh
│
├── TẬP HUẤN LUYỆN (Train Set - 70%):
│   └── Video/Ảnh của các ngày đầu (Ví dụ: Ngày 19/10 đến 23/10)
│       └── Mô hình học nhận diện đặc trưng góc chụp, phông chữ, ánh sáng.
│
├── TẬP ĐÁNH GIÁ (Validation Set - 15%):
│   └── Video/Ảnh của ngày tiếp theo (Ví dụ: Ngày 24/10)
│       └── Dùng để tinh chỉnh siêu tham số (Hyperparameters), chọn trọng số Best Checkpoint.
│
└── TẬP KIỂM THỬ ĐỘC LẬP (Test Set - 15%):
    └── Video/Ảnh của ngày mới hoàn toàn (Ví dụ: Ngày 25/10 hoặc ca độc lập)
        └── Đảm bảo 100% các xe trong tập Test là "XE MỚI HOÀN TOÀN" chưa từng xuất hiện trong tập Train!
        └── Phản ánh chính xác 100% hiệu năng khi triển khai thực tế tại cổng trường ĐH Vinh.
```

---

## 4. Cấu trúc Cây Thư mục Dữ liệu

```text
data/
├── raw/                                 # Video gốc có đầy đủ ngày và ca quay
│   ├── XeMay/
│   │   ├── Vao/
│   │   │   ├── nhaxe1_xemay_vao_20261019_sang_001.mp4
│   │   │   └── nhaxe1_xemay_vao_20261020_chieu_001.mp4
│   │   └── Ra/
│   │       ├── nhaxe1_xemay_ra_20261019_chieu_001.mp4
│   │       └── nhaxe1_xemay_ra_20261020_toi_001.mp4
│   └── OTo/
│       ├── Vao/
│       │   └── nhaxe2_oto_vao_20261020_sang_001.mp4
│       └── Ra/
│           └── nhaxe2_oto_ra_20261020_chieu_001.mp4
│
└── datasets/
    ├── raw_frames/                      # Khung hình trích xuất từ từng video
    │   └── nhaxe1_xemay_vao_20261019_sang_001/
    │       ├── nhaxe1_xemay_vao_20261019_sang_001_f0001.jpg
    │       └── ...
    │
    └── license_plate/                   # Dataset đã gán nhãn YOLO phân chia theo thời gian
        ├── images/
        │   ├── train/                   # Khung hình từ các video ngày 19 - 23/10
        │   ├── val/                     # Khung hình từ các video ngày 24/10
        │   └── test/                    # Khung hình từ các video ngày 25/10
        ├── labels/
        │   ├── train/
        │   ├── val/
        │   └── test/
        └── data.yaml
```

---

## 5. Giá trị Học thuật khi Bảo vệ Đồ án

Việc áp dụng chiến lược **Temporal Data Split** này là một điểm cộng rất lớn trong báo cáo thực tập và thuyết trình bảo vệ trước hội đồng khoa học:
1. Chứng minh sự thấu hiểu sâu sắc về phương pháp luận nghiên cứu Học máy (Machine Learning Methodology).
2. Đảm bảo tính trung thực và khách quan của các chỉ số hiệu năng (mAP, Precision, Recall, Accuracy).
3. Đề tài hướng tới sản phẩm triển khai thực tế tại Đại học Vinh thay vì chỉ là bài tập mô phỏng trên tập dữ liệu tĩnh.
