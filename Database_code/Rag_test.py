import os
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer, CrossEncoder
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- 1. การตั้งค่า ---
db_key = os.getenv("DB_KEY")
api_key = os.getenv("API_KEY") 

client = MongoClient(db_key)
db = client['Knowledge_hub']
collection = db['Data_project']

kku_client = OpenAI(
    api_key=api_key, 
    base_url="https://gen.ai.kku.ac.th/api/v1"
)

# โหลดโมเดล 2 ตัว: ตัวหนึ่งหา (Embedding) อีกตัวคัดเกรด (Reranker)
print("กำลังโหลดโมเดล Embedding & Reranker...")
embed_model = SentenceTransformer('BAAI/bge-m3')
rerank_model = CrossEncoder('BAAI/bge-reranker-v2-m3') # ตัวนี้รองรับภาษาไทยดีมาก

# --- 2. ฟังก์ชัน RAG พร้อม Reranking ---
def ask_rag(user_question):
    # Step 1: Retrieval (ดึงมาเยอะหน่อย เช่น 10 ชิ้น เพื่อให้ Reranker คัดเลือก)
    query_embedding = embed_model.encode(user_question).tolist()
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "numCandidates": 100,
                "limit": 10 
            }
        },
        {"$project": {"_id": 0, "text": 1}}
    ]
    initial_docs = list(collection.aggregate(pipeline))
    
    if not initial_docs:
        return "ขออภัย ไม่พบข้อมูลที่เกี่ยวข้อง"

    # Step 2: Reranking (คัดเกรดข้อมูลที่ดึงมา)
    # เตรียมคู่คำถามและเนื้อหาสำหรับ Reranker
    pairs = [[user_question, doc['text']] for doc in initial_docs]
    scores = rerank_model.predict(pairs)
    
    # รวมคะแนนเข้ากับข้อมูลเดิมและเรียงลำดับใหม่
    for i in range(len(initial_docs)):
        initial_docs[i]['rerank_score'] = scores[i]
    
    # เรียงลำดับตามคะแนน Rerank (จากมากไปน้อย)
    reranked_docs = sorted(initial_docs, key=lambda x: x['rerank_score'], reverse=True)

    # Step 3: เลือก Top 3-5 ที่ดีที่สุดหลัง Rerank มาทำ Context
    top_docs = reranked_docs[:5]
    context_items = [f"[แหล่งข้อมูลที่ {i+1}]: {d['text']}" for i, d in enumerate(top_docs)]
    context_text = "\n\n".join(context_items)

    # Step 4: Generation ด้วย Prompt ที่เน้นการสรุปเรียงข้อ
    system_instruction = (
        "คุณคือผู้ช่วยอัจฉริยะที่แม่นยำที่สุด หากพบข้อมูลที่คล้ายกันจากหลายแหล่ง "
        "จงสรุปและเปรียบเทียบเป็นข้อๆ (1, 2, 3...) โดยระบุเลขแหล่งข้อมูลอ้างอิงเสมอ"
    )

    response = kku_client.chat.completions.create(
        model="gemini-3-pro-preview", 
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"ข้อมูลประกอบ:\n{context_text}\n\nคำถาม: {user_question}"},
        ],
        temperature=0.2, # ลดลงเพื่อให้ผลลัพธ์มีความนิ่ง
        stream=False
    )
    return response.choices[0].message.content

# --- 3. Interactive Loop ---
print("\n" + "★"*50)
print("ระบบ Advanced RAG (Vector Search + Reranking) พร้อมใช้งาน!")
print("พิมพ์ 'exit' เพื่อเลิกใช้งาน")
print("★"*50 + "\n")

while True:
    user_input = input("👤 คุณ: ")
    if user_input.lower() in ['exit', 'quit', 'ออก']: break
    if not user_input.strip(): continue

    print("🤖 กำลังค้นหาและคัดกรองข้อมูลที่ดีที่สุด...")
    try:
        answer = ask_rag(user_input)
        print(f"🤖 AI:\n{answer}\n")
        print("-" * 30)
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาด: {e}")