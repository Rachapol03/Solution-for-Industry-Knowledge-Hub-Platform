from pymongo import MongoClient
from sentence_transformers import SentenceTransformer


# เชื่อมต่อกับ MongoDB Atlas
client = MongoClient("mongodb+srv://natchapolsr_db_user:7vstZcQFUAKbvvfj@cluster0.vqtkoim.mongodb.net/")
db = client['Knowledge_hub']
collection = db['Document']


model = SentenceTransformer('BAAI/bge-m3')

def get_embedding(text):
    return model.encode(text).tolist()
# ข้อมูลที่ต้องการเก็บ
data_to_insert = [  
    {"text": "ทดสอบๆๆ"}
]

# วนลูปสร้าง Embedding และ Insert
for item in data_to_insert:
    item['embedding'] = get_embedding(item['text'])
    
collection.insert_many(data_to_insert)

print("บันทึกข้อมูลเรียบร้อยแล้ว!")