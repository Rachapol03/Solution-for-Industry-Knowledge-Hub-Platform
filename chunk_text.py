import os
import re

def chunk_text(text_path, chunk_size=1024):
    full_content = ""
    text_path.sort(key=lambda f: int(re.sub(r'\D', '', os.path.basename(f))))
    page_ranges = []
    current_length = 0
    
    for path in text_path:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

            start_idx = current_length
            full_content += content + "\n"
            current_length = len(content)
            end_idx = current_length

            page_num = int(re.sub(r'\D', '', os.path.basename(path)))
            page_ranges.append({"page": page_num, "start": start_idx, "end": end_idx})

    sections = []
    header_pattern = r'(^#+ .*|\n#+ .*)'
    last_idx = 0
    current_header = "บทนำ/General"

    for match in re.finditer(header_pattern, full_content, flags=re.MULTILINE):
        section_text = full_content[last_idx:match.start()].strip()
        if section_text:
            sections.append({
                "header": current_header, 
                "text": section_text, 
                "start": last_idx, 
                "end": match.start()
            })
        current_header = match.group(0).strip()
        last_idx = match.end()
    
    sections.append({
        "header": current_header,
        "text": full_content[last_idx:].strip(),
        "start": last_idx,
        "end": len(full_content)
    })

    max_chunk_size = chunk_size
    chunks = []

    for sec in sections:
        paragraphs = sec['text'].split('\n')
        buffer_text = ""
        buffer_start = sec['start']

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if (para.startswith(('*', '-')) or buffer_text.endswith(':')):
                buffer_text += "\n" + para
            elif len(buffer_text) + len(para) < max_chunk_size:
                buffer_text = (buffer_text + "\n\n" + para) if buffer_text else para
            else:
                if buffer_text:
                    chunks.append({
                        "header": sec['header'],
                        "content": buffer_text.strip(),
                        "start": buffer_start,
                        "end": buffer_start + len(buffer_text)
                    })
                buffer_text = para
                buffer_start = sec['start'] + len(full_content[:sec['start']].split('\n', 1)[0]) + 1

        if buffer_text:
            chunks.append({
                "header": sec['header'],
                "content": buffer_text.strip(),
                "start": buffer_start,
                "end": buffer_start + len(buffer_text)
            })
    

    texts_to_embed = []

    for chunk in chunks:
        raw_display_text = f"หัวข้อ: {chunk['header']}\nเนื้อหา: {chunk['content']}"
        clean_text = raw_display_text.replace("หัวข้อ:", "").replace("เนื้อหา:", "")
        clean_text = re.sub(r'#+', '', clean_text)
        clean_text = clean_text.replace('\n', ' ')
        clean_text = re.sub(r' +', ' ', clean_text).strip()
        texts_to_embed.append(clean_text)

    return texts_to_embed, chunks, page_ranges

