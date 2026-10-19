"""
Tool trích xuất frames từ video để chuẩn bị dữ liệu gán nhãn (Roboflow / LabelImg)
Thành viên A - Tuần 2: Xử lý video thô thành tập ảnh huấn luyện YOLOv8
"""

import sys
import os
import cv2
import argparse

if hasattr(sys.stdout, "reconfigure"):
    getattr(sys.stdout, "reconfigure")(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    getattr(sys.stderr, "reconfigure")(encoding="utf-8", errors="replace")

def extract_frames(video_path, output_dir=None, sample_fps=1, max_frames=None):
    """
    Trích xuất khung hình từ video theo tần suất mong muốn (mặc định 1 frame/giây).
    
    Args:
        video_path (str): Đường dẫn tới video đầu vào.
        output_dir (str): Thư mục lưu ảnh cắt ra.
        sample_fps (float): Số khung hình muốn lấy mỗi giây (ví dụ: 1.0 = 1s lấy 1 ảnh, 2.0 = 0.5s lấy 1 ảnh).
        max_frames (int): Giới hạn số lượng frame tối đa (None = không giới hạn).
    """
    if not os.path.exists(video_path):
        print(f"[ERROR] Không tìm thấy video: {video_path}")
        return 0

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[ERROR] Không thể mở video: {video_path}")
        return 0

    video_name = os.path.splitext(os.path.basename(video_path))[0]
    if output_dir is None:
        output_dir = os.path.join("data", "datasets", "raw_frames", video_name)
    os.makedirs(output_dir, exist_ok=True)

    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = total_frames / video_fps if video_fps > 0 else 0

    # Tính bước nhảy frame (interval)
    step = max(1, int(round(video_fps / sample_fps)))

    print("=" * 60)
    print(f"  TRÍCH XUẤT FRAME TỪ VIDEO: {os.path.basename(video_path)}")
    print("=" * 60)
    print(f"Độ phân giải:      {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
    print(f"Tốc độ khung hình: {video_fps:.2f} FPS")
    print(f"Tổng số frame:     {total_frames}")
    print(f"Thời lượng:        {duration:.2f} giây")
    print(f"Tần suất lấy mẫu:  {sample_fps} frame/giây (cách mỗi {step} frames)")
    print(f"Thư mục lưu ảnh:   {output_dir}")
    print("-" * 60)

    saved_count = 0
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % step == 0:
            saved_count += 1
            out_filename = f"{video_name}_f{saved_count:04d}.jpg"
            out_path = os.path.join(output_dir, out_filename)
            cv2.imwrite(out_path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

            if max_frames and saved_count >= max_frames:
                break

        frame_idx += 1

    cap.release()
    print(f"  -> [HOÀN TẤT] Đã trích xuất thành công {saved_count} ảnh vào: {output_dir}")
    return saved_count

def main():
    parser = argparse.ArgumentParser(description="Trích xuất frames từ video cho gán nhãn")
    parser.add_argument("--video", type=str, default="data/raw/XeMay/Vao/nhaxe1_xemay_vao_20261019_sang_001.mp4", help="Đường dẫn file video")
    parser.add_argument("--output", type=str, default=None, help="Thư mục xuất ảnh")
    parser.add_argument("--fps", type=float, default=1.0, help="Số ảnh trích xuất mỗi giây (mặc định 1.0)")
    parser.add_argument("--max", type=int, default=None, help="Số ảnh tối đa muốn trích xuất")
    args = parser.parse_args()

    extract_frames(args.video, args.output, args.fps, args.max)

if __name__ == "__main__":
    main()
