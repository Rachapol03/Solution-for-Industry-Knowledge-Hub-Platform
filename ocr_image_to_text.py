import os
import re
import time
from typhoon_ocr import ocr_document
from pathlib import Path

def run_ocr(image_paths, output_folder):
    """
    ใช้ Typhoon OCR เพื่อแปลงภาพเป็นข้อความ
    คืนค่าเป็นข้อความรวมของทุกหน้า
    """
    full_text = ""
    
    Path(output_folder).mkdir(parents=True, exist_ok=True)
    text_path = []


    for path in image_paths:
        try:
            print(f"กำลังประมวลผล: {os.path.basename(path)}...")
            
            markdown = ocr_document(
                path, 
                model="typhoon-ocr", 
                figure_language="Thai", 
                task_type="v1.5"
            )
            
            base_name = os.path.basename(path)
            file_name_without_ext = os.path.splitext(base_name)[0]
            output_filename = os.path.join(output_folder, f"{file_name_without_ext}.txt")
            
            with open(output_filename, 'w', encoding='utf-8') as f:
                content = re.sub(r'<page_number>.*?</page_number>', '', markdown, flags=re.DOTALL)
                content = re.sub(r' +', ' ', content)
                f.write(content)

            print(f"ประมวณผล {base_name} สำเร็จ!")
            text_path.append(output_filename)
            time.sleep(4)
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาดกับไฟล์ {base_name}: {e}")
    
    return text_path

