import os
import cv2
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image

def process_pdf_to_images(pdf_input_path, output_folder):

    # 1. สร้างโฟลเดอร์ปลายทางถ้ายังไม่มี
    output_dir = Path(output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 2. แปลง PDF เป็นภาพ (ใช้ DPI สูงเผื่อไว้สำหรับงานคุณภาพ)
    # หมายเหตุ: บน Cloud ต้องมั่นใจว่าติดตั้ง poppler-utils แล้ว
    pages = convert_from_path(pdf_input_path, dpi=300)

    processed_image_paths = []

    for i, page in enumerate(pages, start=1):
        image_name = f"page_{i}.jpg"
        image_path = output_dir / image_name
        
        # 3. Save ภาพดิบก่อน
        page.save(image_path, "JPEG")

        # 4. Cleaning ด้วย OpenCV (Thresholding)
        # อ่านไฟล์ภาพที่เพิ่งเซฟ
        img = cv2.imread(str(image_path))
        if img is not None:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
            
            cv2.imwrite(str(image_path), thresh)
            processed_image_paths.append(str(image_path))
            print(f"Processed and Saved: {image_path}")

    return processed_image_paths