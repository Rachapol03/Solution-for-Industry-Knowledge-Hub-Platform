from pymongo import MongoClient
from openai import OpenAI
from embedding import get_embedding, get_rerank_scores 
import os

def ask_rag(user_question, config, debug=False):
    client = MongoClient(config['db_key'])
    
    # แยกการเชื่อมต่อเป็น 2 Collection
    text_collection = client['Knowledge_hub']['Data_project']
    fig_collection = client['Knowledge_hub']['Fig_data']
    
    kku_client = OpenAI(api_key=config['api_key'], base_url=config['base_url'])

    # --- 1. แปลงคำถามเป็น Vector (ทำครั้งเดียว ใช้ได้ทั้ง 2 สาย) ---
    query_vector = get_embedding(user_question, config['local_api_url'])
    
    # ==========================================
    # สายที่ 1: ค้นหาข้อความ (Text) จาก Data_project
    # ==========================================
    text_pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index", # ชื่อ Index ของ Data_project
                "queryVector": query_vector,
                "path": "embedding", # สมมติว่าใน Data_project มีฟิลด์ embedding ด้วย
                "numCandidates": 100,
                "limit": 10 
            }
        },
        {"$project": {"_id": 0, "text": 1, "header": 1, "page": 1}}
    ]
    initial_text_docs = list(text_collection.aggregate(text_pipeline))
    
    # ทำ Reranking สำหรับสาย Text
    top_text_docs = []
    if initial_text_docs:
        docs_text = [doc['text'] for doc in initial_text_docs]
        scores = get_rerank_scores(user_question, docs_text, config['local_api_url'])
        
        for i in range(len(initial_text_docs)):
            initial_text_docs[i]['rerank_score'] = scores[i]
        
        reranked_docs = sorted(initial_text_docs, key=lambda x: x['rerank_score'], reverse=True)
        top_text_docs = reranked_docs[:5] # เอาแค่ 5 อันดับแรกไปให้ LLM

    # ==========================================
    # สายที่ 2: ค้นหารูปภาพ (Image) จาก Fig_data
    # ==========================================
    fig_pipeline = [
        {
            "$vectorSearch": {
                "index": "fig_vector_index", # **ต้องสร้าง Index ใน Atlas ให้ Fig_data ด้วยนะครับ**
                "queryVector": query_vector,
                "path": "embedding",
                "numCandidates": 50,
                "limit": 3 # เอารูปที่เกี่ยวที่สุดมาสัก 3 รูปก็พอ
            }
        },
        {
            "$project": {
                "_id": 0, 
                "path": 1, 
                "pic_name": 1, 
                "page": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]
    fig_docs = list(fig_collection.aggregate(fig_pipeline))
    
    # เตรียมข้อมูลรูปภาพส่งกลับไปหน้าเว็บ (เอาเฉพาะรูปที่คะแนนถึงเกณฑ์)
    image_list = []
    for d in fig_docs:
        # เช็ค score ก่อน
        if d.get('score', 0) > 0.8: 

            cloud_url = d.get('path', '')
            image_list.append({
                "url": cloud_url, 
                "name": d.get('pic_name', 'รูปภาพประกอบ'),
                "page": d.get('page', '-')
            })

    # ==========================================
    # สายที่ 3: สรุปผลด้วย LLM (Generation)
    # ==========================================
    if not top_text_docs:
        result = {
            "answer": "ขออภัย ไม่พบข้อมูลข้อความที่เกี่ยวข้องในระบบ",
            "images": image_list # ถึงข้อความไม่เจอ แต่ถ้ารูปเจอ ก็ส่งรูปไปโชว์ได้
        }
        if debug:
            result["debug"] = {
                "query": user_question,
                "query_vector_length": len(query_vector) if hasattr(query_vector, '__len__') else None,
                "text_hits": initial_text_docs,
                "fig_hits": fig_docs,
                "image_list": image_list
            }
        return result

    # รวม Text ไว้ให้ LLM (บอกหน้าด้วย เพื่อให้อ้างอิงได้แม่นขึ้น)
    context_text = "\n\n".join([
        f"[แหล่งข้อมูลที่ {i+1} (หน้า {d.get('page', '-')})]: {d.get('text', '')}" 
        for i, d in enumerate(top_text_docs)
    ])
    
    system_instruction = (
        "คุณคือผู้ช่วยอัจฉริยะที่แม่นยำที่สุด หากพบข้อมูลที่คล้ายกันจากหลายแหล่ง "
        "จงสรุปและเปรียบเทียบเป็นข้อๆ (1, 2, 3...) "
        "ทำให้คำตอบชัดเจน กระชับ เข้าใจง่าย และสะอาดที่สุด หลีกเลี่ยงการใช้เครื่องหมาย *"
    )

    response = kku_client.chat.completions.create(
        model="gemini-3-pro-preview", 
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"ข้อมูลประกอบ:\n{context_text}\n\nคำถาม: {user_question}"},
        ],
        temperature=0.2
    )
    
    answer_text = response.choices[0].message.content

    # ส่งกลับทั้งคำตอบจาก LLM และรูปภาพจาก Fig_data
    result = {
        "answer": answer_text,
        "images": image_list
    }
    if debug:
        result["debug"] = {
            "query": user_question,
            "query_vector_length": len(query_vector) if hasattr(query_vector, '__len__') else None,
            "top_text_docs": top_text_docs,
            "fig_hits": fig_docs,
            "image_list": image_list
        }
    return result