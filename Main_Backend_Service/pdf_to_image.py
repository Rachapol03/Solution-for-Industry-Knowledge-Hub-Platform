import os
from pathlib import Path
from pdf2image import convert_from_path


def pdf_to_images(pdf_path, output_folder):
    """
    แปลง PDF เป็นภาพ (PNG) และบันทึกในโฟลเดอร์ที่กำหนด
    คืนค่าเป็นรายการของเส้นทางไฟล์ภาพที่สร้างขึ้น
    """
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    
    try:
        images = convert_from_path(pdf_path, dpi=300)
        image_paths = []
        
        for i, img in enumerate(images):
            image_path = os.path.join(output_folder, f"page_{i+1}.jpg")
            img.save(image_path, 'JPEG')
            image_paths.append(image_path)
        
        return image_paths
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return []
