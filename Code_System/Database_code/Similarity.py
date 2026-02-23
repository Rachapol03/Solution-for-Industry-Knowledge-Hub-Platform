from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import os 
from dotenv import load_dotenv

load_dotenv()
db_key = os.getenv("DB_KEY")
# 1. เชื่อมต่อฐานข้อมูล
client = MongoClient(db_key)
db = client['Knowledge_hub']
collection = db['Document']

# 2. โหลดโมเดล (แนะนำ BAAI/bge-m3 เพราะรองรับภาษาไทยได้ดีมาก)
model = SentenceTransformer('BAAI/bge-m3')

def search_knowledge(query_text, limit=5):
    # แปลงคำค้นหาเป็น Vector
    query_embedding = model.encode(query_text).tolist()

    # 3. สร้าง Pipeline สำหรับ Vector Search
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",      # ชื่อนี้ต้องตรงกับที่ตั้งไว้ใน MongoDB Atlas
                "queryVector": query_embedding,
                "path": "embedding",          # ชื่อ field ที่เก็บ vector ใน document
                "numCandidates": 100,         # จำนวน candidate ที่จะนำมาคำนวณ (ยิ่งเยอะยิ่งแม่นแต่ช้าลง)
                "limit": limit                # จำนวนผลลัพธ์ที่ต้องการ
            }
        },
        {
            # ดึงคะแนนความคล้าย (Score) ออกมาแสดงผล
            "$project": {
                "_id": 0,
                "text": 1,
                "score": {"$meta": "vectorSearchScore"} 
            }
        }
    ]

    # รันการค้นหา
    results = list(collection.aggregate(pipeline))
    return results

# --- ทดลองใช้งาน ---
search_query = "ไอ้พีเป็นนายก"
print(f"กำลังค้นหา: {search_query}\n")

search_results = search_knowledge(search_query)

if not search_results:
    print("ไม่พบข้อมูลที่ใกล้เคียง")
else:
    for i, r in enumerate(search_results, 1):
        print(f"{i}. Score: {r['score']:.4f} | Text: {r['text']}")