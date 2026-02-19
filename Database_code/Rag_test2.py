import os
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
from openai import OpenAI  # สำหรับเรียกใช้ KKU IntelSphere
from dotenv import load_dotenv

load_dotenv()

# --- 1. การตั้งค่าการเชื่อมต่อ ---
db_key = os.getenv("DB_KEY")
kku_api_key = os.getenv("API_KEY") # อย่าลืมเพิ่มใน .env
client = MongoClient(db_key)
db = client['Knowledge_hub']
collection = db['Document']

# เชื่อมต่อกับ KKU IntelSphere
kku_client = OpenAI(
    api_key=kku_api_key, 
    base_url="https://gen.ai.kku.ac.th/api/v1"
)

# โหลดโมเดล Embedding (ต้องเป็นตัวเดียวกับที่ใช้ตอนเก็บข้อมูลเข้า MongoDB)
model = SentenceTransformer('BAAI/bge-m3')

# --- 2. ฟังก์ชันค้นหาความรู้ (Retrieval) ---
def search_knowledge(query_text, limit=3):
    query_embedding = model.encode(query_text).tolist()

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 100,
                "limit": limit
            }
        },
        {
            "$project": {
                "_id": 0,
                "text": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]
    return list(collection.aggregate(pipeline))

# --- 3. ฟังก์ชัน RAG (เชื่อมต่อ LLM) ---
def rag_answer_multi(user_question):
    # 1. ดึงข้อมูลที่คล้ายกันมาหลายๆ ชิ้น (เช่น Top 3-5)
    # สมมติว่าผ่านการ Search และ Rerank มาแล้วในชื่อ top_docs
    docs = search_knowledge(user_question, limit=5) # ลองดึงมาซัก 5 เพื่อดูความหลากหลาย
    
    if not docs:
        return "ไม่พบข้อมูลที่เกี่ยวข้อง"

    # 2. เตรียม Context โดยใส่หมายเลขกำกับให้ AI เห็นชัดเจน
    context_with_sources = ""
    for i, d in enumerate(docs, 1):
        context_with_sources += f"แหล่งข้อมูลที่ {i}:\n{d['text']}\n\n"

    # 3. ปรับ Prompt ให้สั่ง AI เรียงลำดับ 1, 2, 3
    prompt = f"""จงตอบคำถามโดยรวบรวมข้อมูลที่เกี่ยวข้องทั้งหมดที่ได้รับมา 
    หากมีข้อมูลที่คล้ายคลึงกันจากหลายแหล่ง ให้สรุปและเปรียบเทียบโดยเรียงลำดับเป็นข้อๆ (1, 2, 3...) 
    และระบุด้วยว่าข้อมูลนั้นมาจากแหล่งข้อมูลที่เท่าไหร่
    
    ข้อมูลที่ค้นพบ:
    {context_with_sources}
    
    คำถามของผู้ใช้: {user_question}"""

    # 4. ส่งให้ KKU IntelSphere
    response = kku_client.chat.completions.create(
        model="gemini-3-pro-preview", 
        messages=[
            {"role": "system", "content": "คุณคือผู้เชี่ยวชาญด้านการวิเคราะห์ข้อมูลอุตสาหกรรม หน้าที่ของคุณคือสรุปข้อมูลที่คล้ายคลึงกันให้เข้าใจง่ายและครบถ้วน"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3, # ปรับเพิ่มเล็กน้อยเพื่อให้ AI เรียบเรียงภาษาได้ดีขึ้น
        stream=False
    )
    
    return response.choices[0].message.content

    return response.choices[0].message.conten

# --- ทดลองใช้งาน ---
user_query = "นโยบายของพัรภัทรมีอะไรบ้าง" 
print(f"คำถาม: {user_query}")
print("-" * 30)

answer = rag_answer_multi(user_query)
print(f"คำตอบจาก IntelSphere:\n{answer}")