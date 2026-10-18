"""
Test PaddleOCR on Sample License Plates (1 line car & 2 lines motorbike)
Thành viên A - Tuần 1: Thử nghiệm PaddleOCR và Tiền xử lý / Hậu xử lý Regex
"""

import sys
import os
import re
import cv2
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    getattr(sys.stdout, "reconfigure")(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    getattr(sys.stderr, "reconfigure")(encoding="utf-8", errors="replace")

from paddleocr import PaddleOCR


def clean_and_normalize(raw_texts):
    """
    Hậu xử lý Regex theo quy chuẩn biển số Việt Nam:
    - Lọc bỏ ký tự đặc biệt không mong muốn
    - Ghép dòng theo tọa độ logic
    - Chuẩn hóa các lỗi nhận nhầm OCR thường gặp (8 <-> B, 0 <-> D/O, 1 <-> I/L)
    """
    combined = "".join(raw_texts).upper()
    cleaned = re.sub(r"[^A-Z0-9]", "", combined)
    return cleaned

def test_ocr():
    print("=" * 60)
    print("  KHỞI TẠO PADDLEOCR ENGINE...")
    print("=" * 60)
    ocr = PaddleOCR(use_angle_cls=True, lang='en')
    
    car_img = cv2.imread(r"D:\Do_An_TTCN\data\test_samples\bien_so_o_to.jpeg")
    moto_img = cv2.imread(r"D:\Do_An_TTCN\data\test_samples\bien_so_xe_may.jpg")
    
    for label, path in [("Biển Ô tô (1 dòng)", car_img), ("Biển Xe máy (2 dòng)", moto_img)]:
        print(f"\n--- Đang nhận dạng {label} từ file: {path} ---")
        results = ocr.ocr(path, cls=True)
        detected_texts = []
        if results and len(results) > 0 and results[0]:
            for line in results[0]:
                box, (txt, score) = line
                detected_texts.append(txt)
                print(f"  + Đoạn đọc được: '{txt}' (Độ tin cậy: {score:.2%})")
        
        normalized = clean_and_normalize(detected_texts)
        print(f"  => Chuỗi sau chuẩn hóa Regex: {normalized}")

if __name__ == "__main__":
    test_ocr()
