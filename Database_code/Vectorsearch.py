from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

client = MongoClient("mongodb+srv://natchapolsr_db_user:7vstZcQFUAKbvvfj@cluster0.vqtkoim.mongodb.net/")
db = client['Knowledge_hub']
collection = db['Document']

model = SentenceTransformer('BAAI/bge-m3')

def get_embedding(text):
    return model.encode(text,normalize_embeddings=True).tolist()

# ข้อความใหม่
new_text = "พรุ่งนี้ฝนตกแน่ๆ"
new_embedding = get_embedding(new_text)
collection.insert_one({"text": new_text, "embedding": new_embedding})

# Vector Search ใน MongoDB (Atlas หรือ MongoDB 7.0+)
pipeline = [
    {
        "$vectorSearch": {
            "queryVector": new_embedding,
            "path": "embedding",
            "numCandidates": 10,
            "limit": 3,
            "index": "vector_index"  # เปลี่ยนเป็นชื่อ index ที่สร้างไว้
        }
    }
]

results = list(collection.aggregate(pipeline))
for r in results:
    print(r["text"], r.get("score", ""))