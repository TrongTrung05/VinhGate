"""
System & Environment Verification Script for Member A (Computer Vision & AI)
Hệ thống quản lý xe ra vào Đại học Vinh - Hướng tới khuôn viên thông minh
"""

import sys
import re

if hasattr(sys.stdout, "reconfigure"):
    getattr(sys.stdout, "reconfigure")(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    getattr(sys.stderr, "reconfigure")(encoding="utf-8", errors="replace")

def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def check_python():
    print_header("1. KIỂM TRA PYTHON")
    print(f"Python Version: {sys.version}")
    print(f"Executable:     {sys.executable}")
    if sys.version_info >= (3, 10) and sys.version_info < (3, 13):
        print("  -> [PASS] Phiên bản Python tương thích tốt (3.10 - 3.12)")
        return True
    else:
        print("  -> [WARNING] Khuyến nghị dùng Python 3.10 - 3.12 để đảm bảo tương thích thư viện AI.")
        return False

def check_torch_cuda():
    print_header("2. KIỂM TRA PYTORCH & CUDA (GPU)")
    try:
        import torch
        print(f"PyTorch Version: {torch.__version__}")
        cuda_avail = torch.cuda.is_available()
        print(f"CUDA Available:  {cuda_avail}")
        if cuda_avail:
            gpu_count = torch.cuda.device_count()
            gpu_name = torch.cuda.get_device_name(0)
            capability = torch.cuda.get_device_capability(0)
            total_mem_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            print(f"GPU Count:       {gpu_count}")
            print(f"GPU Name:        {gpu_name}")
            print(f"Compute Cap.:    {capability}")
            print(f"VRAM:            {total_mem_gb:.2f} GB")
            print("  -> [PASS] GPU NVIDIA hoạt động hoàn hảo với PyTorch!")
            return True
        else:
            print("  -> [WARNING] CUDA chưa được kích hoạt, PyTorch đang chạy ở chế độ CPU.")
            return False
    except ImportError as e:
        print(f"  -> [FAIL] Chưa cài đặt PyTorch: {e}")
        return False

def check_ultralytics():
    print_header("3. KIỂM TRA YOLOV8 (ULTRALYTICS)")
    try:
        import ultralytics
        print(f"Ultralytics Version: {ultralytics.__version__}")
        from ultralytics import YOLO
        # Test loading a tiny model
        model = YOLO("yolov8n.pt")
        print(f"YOLOv8 Model loaded successfully: {model.task}")
        print("  -> [PASS] Ultralytics YOLOv8 sẵn sàng cho nhận diện biển số!")
        return True
    except Exception as e:
        print(f"  -> [FAIL] Lỗi YOLOv8: {e}")
        return False

def check_opencv():
    print_header("4. KIỂM TRA OPENCV")
    try:
        import cv2
        import numpy as np
        print(f"OpenCV Version: {cv2.__version__}")
        # Test basic image matrix
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        print("  -> [PASS] OpenCV hoạt động bình thường!")
        return True
    except Exception as e:
        print(f"  -> [FAIL] Lỗi OpenCV: {e}")
        return False

def check_paddleocr():
    print_header("5. KIỂM TRA PADDLEOCR")
    try:
        import paddle
        print(f"PaddlePaddle Version: {paddle.__version__}")
        from paddleocr import PaddleOCR
        ocr = PaddleOCR(use_angle_cls=True, lang='en')
        print("  -> [PASS] PaddleOCR khởi tạo thành công!")
        return True
    except Exception as e:
        print(f"  -> [FAIL/PENDING] Lỗi/Chưa cài PaddleOCR: {e}")
        return False

def check_regex_samples():
    print_header("6. KIỂM TRA BIỂU THỨC CHÍNH QUY (REGEX) BIỂN SỐ VN")
    # Biển 1 dòng ô tô (ví dụ: 37A-123.45 hoặc 37A-12345)
    car_pattern = re.compile(r"^(?P<prov>\d{2})(?P<series>[A-Z]{1,2})[-.]?(?P<num>\d{4,5})$")
    # Biển 2 dòng xe máy (dòng 1: 37-B1 hoặc 37B1; dòng 2: 123.45 hoặc 12345)
    moto_pattern = re.compile(r"^(?P<prov>\d{2})[-.]?(?P<series>[A-Z]\d|[A-Z]{2})[-.]?(?P<num>\d{4,5})$")
    
    samples = [
        ("37A12345", "Ô tô"),
        ("37B112345", "Xe máy"),
        ("29H188888", "Xe máy Nghệ An / Hà Nội"),
        ("43A56789", "Ô tô Đà Nẵng")
    ]
    all_matched = True
    for text, desc in samples:
        m_car = car_pattern.match(text)
        m_moto = moto_pattern.match(text)
        matched = m_car or m_moto
        status = "MATCHED" if matched else "FAILED"
        if not matched:
            all_matched = False
        print(f"  [{status}] {text} ({desc})")
    
    if all_matched:
        print("  -> [PASS] Logic regex cơ bản cho biển số xe Việt Nam hoạt động đúng!")
    return all_matched

def main():
    print("\n" + "#" * 60)
    print("  BẮT ĐẦU KIỂM TRA MÔI TRƯỜNG PHÁT TRIỂN (THÀNH VIÊN A)")
    print("#" * 60)
    
    p = check_python()
    t = check_torch_cuda()
    u = check_ultralytics()
    c = check_opencv()
    o = check_paddleocr()
    r = check_regex_samples()
    
    print("\n" + "=" * 60)
    print("  KẾT QUẢ TỔNG QUAN")
    print("=" * 60)
    print(f"Python:       {'OK' if p else 'FAILED'}")
    print(f"PyTorch CUDA: {'OK' if t else 'FAILED'}")
    print(f"YOLOv8:       {'OK' if u else 'FAILED'}")
    print(f"OpenCV:       {'OK' if c else 'FAILED'}")
    print(f"PaddleOCR:    {'OK' if o else 'PENDING/FAILED'}")
    print(f"Regex Plate:  {'OK' if r else 'FAILED'}")

if __name__ == "__main__":
    main()
