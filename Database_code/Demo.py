from flask import Flask, render_template, request, jsonify
import os
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer, CrossEncoder
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# --- โหลดโมเดลและฐานข้อมูล (ทำครั้งเดียวเมื่อรัน Server) ---
print("Loading Models...")
embed_model = SentenceTransformer('BAAI/bge-m3')
rerank_model = CrossEncoder('BAAI/bge-reranker-v2-m3')

client = MongoClient(os.getenv("DB_KEY"))
collection = client['Knowledge_hub']['Document']
kku_client = OpenAI(api_key=os.getenv("API_KEY"), base_url="https://gen.ai.kku.ac.th/api/v1")

# --- Route สำหรับหน้าเว็บหลัก ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Route สำหรับ API รับคำถาม ---

@app.route('/ask', methods=['POST'])
def ask_rag():
    data = request.json
    user_query = data.get('question')
    
    # 1. Retrieval + ดึง Score มาดูด้วย
    query_embedding = embed_model.encode(user_query).tolist()
    pipeline = [
        {"$vectorSearch": {
            "index": "vector_index",
            "queryVector": query_embedding,
            "path": "embedding",
            "numCandidates": 100,
            "limit": 5
        }},
        {
            "$project": {
                "_id": 0, 
                "text": 1, 
                "score": {"$meta": "vectorSearchScore"} # ดึงค่าความคล้ายออกมา
            }
        }
    ]
    docs = list(collection.aggregate(pipeline))

    # --- ส่วนที่เพิ่มเข้ามา: ตรวจสอบ Threshold ---
    threshold = 0.65  # ตั้งเกณฑ์ความคล้าย (ปรับเปลี่ยนได้ตามความเหมาะสม)
    
    if not docs or docs[0]['score'] < threshold:
        # ถ้าไม่มีข้อมูล หรือ ตัวที่เหมือนที่สุดยังมีคะแนนต่ำกว่าเกณฑ์
        return jsonify({
            "answer": "ขออภัยครับ ข้อมูลที่ค้นพบมีความเกี่ยวข้องน้อยเกินไป ผมจึงไม่สามารถตอบคำถามนี้ได้อย่างแม่นยำ (ไม่ทราบครับ)",
            "sources": docs if docs else []
        })
    # ---------------------------------------

    # 2. Reranking (ถ้าผ่านเกณฑ์ค่อยทำต่อ)
    pairs = [[user_query, d['text']] for d in docs]
    rerank_scores = rerank_model.predict(pairs)
    for i in range(len(docs)): 
        docs[i]['rerank_score'] = float(rerank_scores[i])
    
    docs = sorted(docs, key=lambda x: x['rerank_score'], reverse=True)

    # 3. Generation
    # 3. Generation
    context_text = "\n\n".join([f"[แหล่งข้อมูล {i+1}]: {d['text']}" for i, d in enumerate(docs)])
    
    response = kku_client.chat.completions.create(
        model="gemini-3-pro-preview",
        messages=[
            {
                "role": "system", 
                "content": (
                    "คุณคือผู้ช่วยอัจฉริยะ หน้าที่ของคุณคือตอบคำถามตามข้อมูลประกอบที่ให้มาเท่านั้น "
                    "กฎสำคัญ: หากข้อมูลประกอบที่ให้มาไม่มีเนื้อหาที่เกี่ยวข้องกับคำถาม หรือไม่สามารถใช้ตอบคำถามได้ "
                    "ให้คุณตอบเพียงว่า 'ขออภัยครับ ผมไม่ทราบข้อมูลในส่วนนี้' และห้ามเดาคำตอบเองโดยเด็ดขาด "
                    "หากมีข้อมูลที่เกี่ยวข้อง ให้สรุปเป็นข้อๆ และระบุแหล่งข้อมูลอ้างอิงเสมอ"
                )
            },
            {"role": "user", "content": f"ข้อมูลประกอบ:\n{context_text}\n\nคำถาม: {user_query}"}
        ],
        temperature=0.1 # ปรับลดเหลือ 0.1 เพื่อให้ LLM เคร่งครัดกับคำสั่งมากขึ้น (ลดความสร้างสรรค์ลง)
    )
    answer = response.choices[0].message.content

    return jsonify({
        "answer": answer,
        "sources": docs
    })

if __name__ == '__main__':
    app.run(debug=True)