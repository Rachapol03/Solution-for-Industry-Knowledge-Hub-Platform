from sentence_transformers import SentenceTransformer

def generate_embeddings(chunks):
    """
    ฟังก์ชันสำหรับสร้าง Vector Embedding จากรายการ Chunks
    :param chunks: List ของข้อมูลที่ผ่านการ Clean มาแล้วจาก Cloud
    :return: List ของเอกสารที่มีการเพิ่มฟิลด์ 'embedding' เข้าไปแล้ว
    """
    # โหลดโมเดลที่เครื่อง Local
    print("กำลังโหลดโมเดล BAAI/bge-m3...")
    model = SentenceTransformer('BAAI/bge-m3')
    
    final_documents = []
    print(f"กำลังเริ่มกระบวนการ Embedding จำนวน {len(chunks)} chunks...")

    for item in chunks:
        # ทำ Embedding ขนาด 1024 มิติ
        embedding = model.encode(item['text_to_embed']).tolist()
        
        doc = {
            "chunk_id": item['chunk_id'],
            "text": item['text_to_embed'],
            "header": item['header'],
            "page": item['page'],
            "embedding": embedding
        }
        final_documents.append(doc)
    
    return final_documents