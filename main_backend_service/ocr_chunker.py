import os
import re
import pytesseract
from PIL import Image
from pathlib import Path

def run_ocr_and_chunk(image_paths, max_chunk_size=1000, overlap_size=200):
    all_text_content = ""
    
    # 1. ทำ OCR ทีละรูป (เรียงตามชื่อไฟล์เพื่อรักษาลำดับเนื้อหา)
    image_paths.sort(key=lambda f: int(re.sub(r'\D', '', os.path.basename(f))))
    
    for img_path in image_paths:
        # บน Cloud ต้องมั่นใจว่าติดตั้ง tesseract-ocr และระบุ lang='tha+eng'
        text = pytesseract.image_to_string(Image.open(img_path), lang='tha+eng')
        # ใส่ Page Marker ชั่วคราวเพื่อให้ระบบรู้จุดตัดหน้า (ถ้าจำเป็น)
        all_text_content += text + "\n\n"

    # 2. Cleaning ข้อมูล
    clean_text = re.sub(r'<page_number>.*?</page_number>', '', all_text_content, flags=re.DOTALL)
    clean_text = re.sub(r"[|'\"—_]", '', clean_text) 
    clean_text = re.sub(r' +', ' ', clean_text)

    # 3. Algorithm: Header-Based Semantic Chunking with Overlap
    sections = re.split(r'(^#+ .*|\n#+ .*)', clean_text, flags=re.MULTILINE)
    
    chunks = []
    current_header = "บทนำ/General"
    
    for section in sections:
        clean_section = section.strip()
        if not clean_section: continue
        
        if clean_section.startswith('#'):
            current_header = clean_section
        else:
            paragraphs = clean_section.split('\n\n')
            buffer_text = ""
            
            for p in paragraphs:
                p = p.strip()
                if not p: continue
                
                if (p.startswith(('*', '-', '1.', '2.', '3.', '4.', '5.')) or buffer_text.endswith(':')):
                    buffer_text += "\n" + p
                elif len(buffer_text) + len(p) < max_chunk_size:
                    buffer_text = (buffer_text + "\n\n" + p) if buffer_text else p
                else:
                    if buffer_text:
                        chunks.append({"header": current_header, "content": buffer_text})
                    
                    # สร้าง Overlap เพื่อความต่อเนื่อง
                    overlap_context = buffer_text[-overlap_size:] if len(buffer_text) > overlap_size else buffer_text
                    if '\n' in overlap_context:
                        overlap_context = overlap_context[overlap_context.find('\n'):].strip()
                    buffer_text = overlap_context + "\n\n" + p if overlap_context else p
            
            if buffer_text:
                chunks.append({"header": current_header, "content": buffer_text})

    return chunks