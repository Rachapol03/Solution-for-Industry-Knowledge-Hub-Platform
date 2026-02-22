import requests
from pymongo import MongoClient
from sentence_transformers import CrossEncoder
from openai import OpenAI

# ฟังก์ชันสำหรับการทำ Reranking (รันที่เครื่อง Local เพื่อประหยัด Resource บน Cloud)
def get_local_rerank(query, docs, rerank_model, top_k=5):
    """
    คัดเกรดข้อมูลที่ดึงมาเพื่อให้ได้เนื้อหาที่ตรงประเด็นที่สุด
    """
    if not docs:
        return []
        
    # เตรียมคู่คำถามและเนื้อหาสำหรับ Reranker
    pairs = [[query, doc['text']] for doc in docs]
    scores = rerank_model.predict(pairs)
    
    # รวมคะแนนเข้ากับข้อมูลเดิม
    for i in range(len(docs)):
        docs[i]['rerank_score'] = float(scores[i])
    
    # เรียงลำดับจากคะแนนสูงสุดไปน้อยสุด
    reranked = sorted(docs, key=lambda x: x['rerank_score'], reverse=True)
    return reranked[:top_k]

# ฟังก์ชันหลักสำหรับกระบวนการ RAG
def ask_rag_system(user_question, db_config, ai_config):
    """
    กระบวนการ: Retrieval (Cloud) -> Reranking (Local) -> Generation (LLM)
    """
    # 1. เชื่อมต่อฐานข้อมูลและ AI Client (ใช้ค่าที่ส่งมาจาก main.py)
    client = MongoClient(db_config['mongo_uri'])
    collection = client[db_config['db_name']][db_config['coll_name']]
    
    kku_client = OpenAI(
        api_key=ai_config['api_key'], 
        base_url="https://gen.ai.kku.ac.th/api/v1"
    )

    # 2. Retrieval: ดึง Vector จาก Local Embedding Service
    try:
        embed_res = requests.post(ai_config['local_ai_url'] + "/embed", json={"text": user_question})
        query_embedding = embed_res.json()['embedding']
    except Exception as e:
        return f"Error: ไม่สามารถเชื่อมต่อกับ Local Embedding Service ได้ ({e})"

    # 3. Vector Search บน MongoDB
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index", # ชื่อ index ที่ตั้งไว้ใน MongoDB Atlas
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 100,
                "limit": 10 
            }
        },
        {"$project": {"_id": 0, "text": 1, "chunk_id": 1, "header": 1, "page": 1}}
    ]
    initial_docs = list(collection.aggregate(pipeline))
    
    if not initial_docs:
        return "ขออภัย ไม่พบข้อมูลที่เกี่ยวข้องในระบบฐานข้อมูล"

    # 4. Reranking: ส่งไปคัดเกรดที่เครื่อง Local (ใช้โมเดลที่โหลดไว้ใน main.py หรือโหลดใหม่)
    # ในที่นี้แนะนำให้ส่ง rerank_model เข้ามาผ่านทาง ai_config หรือโหลดที่นี่หากสเปกเครื่องไหว
    top_docs = get_local_rerank(user_question, initial_docs, ai_config['rerank_model'], top_k=5)

    # 5. Generation: สร้าง Context และถาม LLM
    context_items = []
    for i, d in enumerate(top_docs):
        # จัดรูปแบบแหล่งอ้างอิงและเลขหน้า [cite: 8, 9, 10]
        pages = ", ".join(map(str, d.get('page', [])))
        context_items.append(f"[แหล่งข้อมูล {i+1} | หน้า {pages}]: {d['text']}")
    
    context_text = "\n\n".join(context_items)

    system_instruction = (
        "คุณคือผู้ช่วยอัจฉริยะที่แม่นยำที่สุด หน้าที่ของคุณคือตอบคำถามจากข้อมูลประกอบที่ให้มาเท่านั้น "
        "หากพบข้อมูลที่คล้ายกันจากหลายแหล่ง จงสรุปและเปรียบเทียบเป็นข้อๆ (1, 2, 3...) "
        "และต้องระบุเลขแหล่งข้อมูลอ้างอิงพร้อมเลขหน้าเสมอ"
    )

    response = kku_client.chat.completions.create(
        model="gemini-1.5-pro", 
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"ข้อมูลประกอบ:\n{context_text}\n\nคำถาม: {user_question}"},
        ],
        temperature=0.2
    )
    
    client.close()
    return response.choices[0].message.content