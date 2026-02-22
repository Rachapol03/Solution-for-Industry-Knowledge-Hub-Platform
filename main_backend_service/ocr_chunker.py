import os
import re
import time
from typhoon_ocr import ocr_document

def run_ocr_and_chunk(image_paths, typhoon_api_key, max_chunk_size=1000, overlap_size=200):
    """
    ใช้ Typhoon OCR ประมวลผลรูปภาพ -> ทำความสะอาดข้อความ -> แบ่ง Chunk
    """
    # ตั้งค่า API Key ให้กับสภาพแวดล้อมเพื่อให้ Library ของ Typhoon เรียกใช้ได้
    os.environ["TYPHOON_OCR_API_KEY"] = typhoon_api_key
    
    all_text_content = ""
    # 1. เรียงลำดับไฟล์รูปภาพ
    image_paths.sort(key=lambda f: int(re.sub(r'\D', '', os.path.basename(f))))
    
    print(f"เริ่มกระบวนการ Typhoon OCR ทั้งหมด {len(image_paths)} ไฟล์...")
    
    for img_path in image_paths:
        try:
            print(f"ประมวลผลไฟล์: {os.path.basename(img_path)}")
            # 2. ทำ OCR ด้วย Typhoon (ผลลัพธ์ที่ได้มักจะเป็น Markdown)
            markdown_content = ocr_document(
                img_path, 
                model="typhoon-ocr", 
                figure_language="Thai", 
                task_type="v1.5"
            )
            
            all_text_content += markdown_content + "\n\n"
            
            # หน่วงเวลาเพื่อเลี่ยง Rate Limit ของ API (ปรับตามความเหมาะสม)
            time.sleep(2) 
            
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการ OCR ไฟล์ {img_path}: {e}")

    # 3. Cleaning ข้อมูล
    # ลบ Tag page_number และสัญลักษณ์ขยะอื่นๆ
    clean_text = re.sub(r'<page_number>.*?</page_number>', '', all_text_content, flags=re.DOTALL)
    clean_text = re.sub(r"[|'\"—_]", '', clean_text)
    clean_text = re.sub(r' +', ' ', clean_text)

    # 4. Header-Based Semantic Chunking
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
                
                # เงื่อนไขการรวมย่อหน้า (Bullet หรือจบด้วย :)
                if (p.startswith(('*', '-', '1.', '2.', '3.')) or buffer_text.endswith(':')):
                    buffer_text += "\n" + p
                elif len(buffer_text) + len(p) < max_chunk_size:
                    buffer_text = (buffer_text + "\n\n" + p) if buffer_text else p
                else:
                    if buffer_text:
                        chunks.append({"header": current_header, "content": buffer_text})
                    
                    # สร้าง Overlap
                    overlap_context = buffer_text[-overlap_size:] if len(buffer_text) > overlap_size else buffer_text
                    if '\n' in overlap_context:
                        overlap_context = overlap_context[overlap_context.find('\n'):].strip()
                    buffer_text = (overlap_context + "\n\n" + p) if overlap_context else p
            
            if buffer_text:
                chunks.append({"header": current_header, "content": buffer_text})

    return chunks