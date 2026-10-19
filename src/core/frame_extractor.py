"""
==============================================================================
MODULE: TRÍCH XUẤT KHUNG HÌNH CÓ XE MÁY TỪ VIDEO (FRAME EXTRACTOR)
==============================================================================
Mục đích:
    - Quét qua video quay tại cổng trường Đại học Vinh.
    - Dùng mô hình YOLOv8 (pretrained COCO) để tự động phát hiện khung hình nào
      có xe máy (class: 'motorcycle').
    - Chỉ lưu những khung hình có xe máy và lọc bỏ các đoạn đường trống không có xe.
    - Giúp người học dễ dàng hiểu từng bước xử lý Video và AI trong OpenCV + YOLO.
==============================================================================
"""

import os
import sys
import cv2

# Đảm bảo in tiếng Việt có dấu không bị lỗi trên Windows PowerShell
if hasattr(sys.stdout, "reconfigure"):
    getattr(sys.stdout, "reconfigure")(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    getattr(sys.stderr, "reconfigure")(encoding="utf-8", errors="replace")

from ultralytics import YOLO


def extract_frames_with_motorcycles(
    video_path: str,
    output_dir: str = None,
    conf_threshold: float = 0.45,
    min_interval_seconds: float = 0.8,
    save_annotated_preview: bool = False
):
    """
    Hàm đọc video và chỉ lưu lại các khung hình xuất hiện XE MÁY.

    Các tham số giải thích chi tiết:
    --------------------------------
    :param video_path: Đường dẫn tới file video cần xử lý (ví dụ: 'data/raw/XeMay/Vao/nhaxe1_xemay_vao_20261019_sang_001.mp4')
    :param output_dir: Thư mục để lưu ảnh kết quả (nếu để None sẽ tự động tạo theo tên video)
    :param conf_threshold: Độ tin cậy tối thiểu để kết luận đó là xe máy (0.45 = 45% chắc chắn)
    :param min_interval_seconds: Khoảng cách thời gian tối thiểu giữa 2 lần lưu ảnh (tránh lưu 2 ảnh quá sát nhau)
    :param save_annotated_preview: Nếu True, sẽ lưu thêm ảnh có vẽ bounding box viền xanh quanh xe để kiểm tra
    :return: Tổng số ảnh xe máy đã trích xuất được (int)
    """

    # -------------------------------------------------------------------------
    # BƯỚC 1: KIỂM TRA FILE VIDEO VÀ KHỞI TẠO ĐỐI TƯỢNG ĐỌC VIDEO (OPENCV)
    # -------------------------------------------------------------------------
    if not os.path.exists(video_path):
        print(f"[LỖI] Không tìm thấy file video tại: {video_path}")
        return 0

    # cv2.VideoCapture là hàm tiêu chuẩn của OpenCV dùng để mở và đọc video từng frame
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        print(f"[LỖI] OpenCV không thể mở được video: {video_path}")
        return 0

    # -------------------------------------------------------------------------
    # BƯỚC 2: ĐỌC CÁC THÔNG SỐ CƠ BẢN CỦA VIDEO
    # -------------------------------------------------------------------------
    fps = video_capture.get(cv2.CAP_PROP_FPS)                      # Tốc độ khung hình (khung hình / giây)
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT)) # Tổng số frame trong video
    width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))       # Chiều rộng video (pixel)
    height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))     # Chiều cao video (pixel)
    duration_seconds = total_frames / fps if fps > 0 else 0        # Thời lượng video (giây)

    # -------------------------------------------------------------------------
    # BƯỚC 3: XÁC ĐỊNH THƯ MỤC LƯU ẢNH
    # -------------------------------------------------------------------------
    # Lấy tên video gốc (loại bỏ phần mở rộng .mp4) để đặt tên thư mục
    video_basename = os.path.splitext(os.path.basename(video_path))[0]

    if output_dir is None:
        # Đường dẫn mặc định chuẩn hóa theo dự án: data/datasets/raw_frames/<tên_video>/
        output_dir = os.path.join("data", "datasets", "raw_frames", video_basename)

    os.makedirs(output_dir, exist_ok=True)

    # Nếu chọn lưu ảnh preview có vẽ box, tạo thêm thư mục preview
    preview_dir = os.path.join(output_dir, "preview_boxes") if save_annotated_preview else None
    if preview_dir:
        os.makedirs(preview_dir, exist_ok=True)

    # -------------------------------------------------------------------------
    # BƯỚC 4: TẢI MÔ HÌNH YOLOV8 ĐỂ NHẬN DIỆN XE MÁY
    # -------------------------------------------------------------------------
    # Mô hình yolov8n (nano) nhẹ, nhanh và đã được huấn luyện sẵn trên tập dữ liệu COCO
    # Trong COCO: class 3 chính là 'motorcycle' (xe máy)
    print("--> Đang tải mô hình YOLOv8n để phát hiện xe máy...")
    model = YOLO("yolov8n.pt")
    MOTORCYCLE_CLASS_ID = 3  # ID của xe máy trong COCO dataset

    print("=" * 70)
    print(f"  BẮT ĐẦU TRÍCH XUẤT ẢNH XE MÁY TỪ: {os.path.basename(video_path)}")
    print("=" * 70)
    print(f"  * Độ phân giải:        {width} x {height}")
    print(f"  * Tốc độ:              {fps:.2f} FPS")
    print(f"  * Thời lượng:          {duration_seconds:.2f} giây ({total_frames} frames)")
    print(f"  * Ngưỡng tin cậy xe:   {conf_threshold:.0%}")
    print(f"  * Giãn cách tối thiểu: {min_interval_seconds} giây giữa 2 ảnh")
    print(f"  * Thư mục xuất ảnh:    {output_dir}")
    print("-" * 70)

    # -------------------------------------------------------------------------
    # BƯỚC 5: VÒNG LẶP DUYỆT QUA TỪNG FRAME CỦA VIDEO
    # -------------------------------------------------------------------------
    frame_index = 0
    saved_count = 0
    last_saved_time = -999.0  # Mốc thời gian (giây) của lần lưu ảnh gần nhất

    # Để tối ưu tốc độ, ta không cần suy luận AI trên 100% tất cả các frame
    # Cứ mỗi 0.25 giây (khoảng 7-8 frame ở 30fps), ta kiểm tra AI một lần
    step_check = max(1, int(round(fps * 0.25)))

    while True:
        # video_capture.read() đọc 1 frame tiếp theo từ video
        # success: True nếu đọc thành công, False nếu đã hết video
        # current_frame: Ma trận ảnh (numpy array) ở định dạng BGR
        success, current_frame = video_capture.read()
        if not success:
            break  # Đã đọc hết video

        # Tính thời điểm hiện tại của frame trong video (tính bằng giây)
        current_time_seconds = frame_index / fps

        # Chỉ chạy AI kiểm tra ở các frame cách đều nhau (step_check)
        if frame_index % step_check == 0:

            # Kiểm tra xem đã đủ khoảng cách thời gian tối thiểu kể từ lần lưu trước chưa
            time_since_last_save = current_time_seconds - last_saved_time
            if time_since_last_save >= min_interval_seconds:

                # Dùng YOLOv8 để phát hiện vật thể trong frame
                # classes=[3]: Chỉ quan tâm đến xe máy, bỏ qua các vật thể khác (người, ô tô...)
                # conf=conf_threshold: Chỉ lấy phát hiện có độ tin cậy >= ngưỡng đã đặt
                # verbose=False: Không in log chi tiết của YOLO ra màn hình để tránh rối mắt
                results = model(
                    current_frame,
                    classes=[MOTORCYCLE_CLASS_ID],
                    conf=conf_threshold,
                    verbose=False
                )

                # Kiểm tra xem có xe máy nào được tìm thấy không
                boxes = results[0].boxes
                has_motorcycle = len(boxes) > 0

                if has_motorcycle:
                    saved_count += 1
                    last_saved_time = current_time_seconds

                    # Lấy độ tin cậy cao nhất của xe máy trong khung hình này
                    best_conf = float(boxes.conf.max().item())

                    # Đặt tên file ảnh theo chuẩn: <tên_video>_f<số_thứ_tự_ảnh>.jpg
                    filename = f"{video_basename}_f{saved_count:04d}.jpg"
                    file_path = os.path.join(output_dir, filename)

                    # Lưu ảnh gốc (ảnh sạch không vẽ khung để sau này đưa vào Roboflow gán nhãn biển số)
                    # cv2.IMWRITE_JPEG_QUALITY đặt chất lượng 95% để ảnh sắc nét
                    cv2.imwrite(file_path, current_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

                    # Nếu người dùng muốn xem trước vị trí YOLO tìm thấy xe
                    if preview_dir:
                        annotated_frame = results[0].plot()  # Vẽ khung chữ nhật và nhãn lên ảnh
                        preview_path = os.path.join(preview_dir, f"preview_{filename}")
                        cv2.imwrite(preview_path, annotated_frame)

                    print(
                        f"  [+] Ảnh #{saved_count:03d} | "
                        f"Giây thứ {current_time_seconds:5.2f}s | "
                        f"Số xe: {len(boxes)} | "
                        f"Tin cậy: {best_conf:.1%} -> Lưu: {filename}"
                    )

        frame_index += 1

    # -------------------------------------------------------------------------
    # BƯỚC 6: GIẢI PHÓNG TÀI NGUYÊN VÀ BÁO CÁO KẾT QUẢ
    # -------------------------------------------------------------------------
    video_capture.release()  # Luôn đóng video_capture sau khi xử lý xong

    print("-" * 70)
    print(f"--> [HOÀN TẤT] Tổng số khung hình đã quét: {frame_index}/{total_frames}")
    print(f"--> [KẾT QUẢ] Đã trích xuất được {saved_count} ảnh có xe máy!")
    print(f"--> [VỊ TRÍ] Ảnh đã lưu tại: {output_dir}")
    print("=" * 70)

    return saved_count


if __name__ == "__main__":
    # Đường dẫn file video mẫu của dự án
    SAMPLE_VIDEO = "data/raw/XeMay/Vao/nhaxe1_xemay_vao_20261019_sang_001.mp4"

    print("Đang khởi động thử nghiệm hàm trích xuất khung hình...")
    extract_frames_with_motorcycles(
        video_path=SAMPLE_VIDEO,
        conf_threshold=0.45,
        min_interval_seconds=1.0,  # Cứ ít nhất 1.0 giây mới lấy 1 ảnh nếu có xe
        save_annotated_preview=True # Lưu thêm ảnh có vẽ bounding box để kiểm tra trực quan
    )
