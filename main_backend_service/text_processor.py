import os
import re
import pytesseract
from PIL import Image

def process_images_to_chunks(image_paths):
    """
    OCR -> Cleaning -> Semantic Chunking (Index Tracking)
    คืนค่าเป็นรายการของ Chunk ที่พร้อมส่งไปทำ Embedding
    """
    full_content = ""
    page_ranges = []
    current_length = 0
    
    # เรียงลำดับไฟล์ภาพตามตัวเลข
    image_paths.sort(key=lambda f: int(re.sub(r'\D', '', os.path.basename(f))))
    
    # 1. OCR กระบวนการนี้รันบน Cloud ได้ถ้าติดตั้ง Tesseract
    for path in image_paths:
        content = pytesseract.image_to_string(Image.open(path), lang='tha+eng')
        content = re.sub(r' +', ' ', content)
        
        start_idx = current_length
        full_content += content + "\n\n"
        current_length = len(full_content)
        
        page_num = int(re.sub(r'\D', '', os.path.basename(path)))
        page_ranges.append({"page": page_num, "start": start_idx, "end": current_length})

    # 2. แยก Section ตาม Header
    sections = []
    header_pattern = r'(^#+ .*|\n#+ .*)'
    last_idx = 0
    current_header = "บทนำ/General"
    
    for match in re.finditer(header_pattern, full_content, flags=re.MULTILINE):
        section_text = full_content[last_idx:match.start()].strip()
        if section_text:
            sections.append({"header": current_header, "text": section_text, "start": last_idx, "end": match.start()})
        current_header = match.group().strip()
        last_idx = match.start()
    
    sections.append({"header": current_header, "text": full_content[last_idx:].strip(), "start": last_idx, "end": len(full_content)})

    # 3. สร้าง Chunks
    max_chunk_size = 1000
    pre_embedding_chunks = []

    for sec in sections:
        paragraphs = sec['text'].split('\n\n')
        buffer_text = ""
        buffer_start = sec['start']
        
        for p in paragraphs:
            p = p.strip()
            if not p: continue
            
            if (p.startswith(('*', '-')) or buffer_text.endswith(':')):
                buffer_text += "\n" + p
            elif len(buffer_text) + len(p) < max_chunk_size:
                buffer_text = (buffer_text + "\n\n" + p) if buffer_text else p
            else:
                if buffer_text:
                    pre_embedding_chunks.append({
                        "header": sec['header'], 
                        "raw_text": buffer_text,
                        "start_idx": buffer_start,
                        "end_idx": buffer_start + len(buffer_text)
                    })
                buffer_start = full_content.find(p, buffer_start)
                buffer_text = p
        
        if buffer_text:
            pre_embedding_chunks.append({
                "header": sec['header'], 
                "raw_text": buffer_text,
                "start_idx": buffer_start,
                "end_idx": buffer_start + len(buffer_text)
            })

    # 4. Final Cleaning ก่อนส่งออก
    final_chunks = []
    for index, item in enumerate(pre_embedding_chunks):
        combined_raw = f"หัวข้อ: {item['header']}\nเนื้อหา: {item['raw_text']}"
        clean_text = combined_raw.replace("หัวข้อ:", "").replace("เนื้อหา:", "")
        clean_text = re.sub(r'#+', '', clean_text)
        clean_text = clean_text.replace('\n', ' ')
        clean_text = re.sub(r' +', ' ', clean_text).strip()
        
        chunk_pages = [pr['page'] for pr in page_ranges if not (item['end_idx'] <= pr['start'] or item['start_idx'] >= pr['end'])]

        final_chunks.append({
            "chunk_id": index,
            "text_to_embed": clean_text,
            "header": item['header'].replace('#', '').strip(),
            "page": sorted(list(set(chunk_pages)))
        })

    return final_chunks