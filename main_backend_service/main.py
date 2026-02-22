import os
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from ocr_chunker import run_ocr_and_chunk
from embedding_processor import generate_embeddings
from database_manager import save_to_mongodb
from rag_system import ask_rag_system

# Load Models
from sentence_transformers import CrossEncoder, SentenceTransformer
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET")
app.config['UPLOAD_FOLDER'] = 'temp_uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# โหลดโมเดลไว้ครั้งเดียวที่ระดับ Global เพื่อความเร็วและประหยัด RAM
print("กำลังโหลดโมเดล Reranker และ Embedding...")
rerank_model = CrossEncoder('BAAI/bge-reranker-v2-m3')
embed_model_local = SentenceTransformer('BAAI/bge-m3')

@app.route('/')
def index():
    return render_template('index.html')

# --- ส่วนที่ 2: ระบบ Chat ---
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    db_config = {
        'mongo_uri': os.getenv("DB_KEY"), 
        'db_name': "Knowledge_hub", 
        'coll_name': "Data_project"
    }
    # local_ai_url ต้องตรงกับ port ที่ Flask รัน (8000)
    ai_config = {
        'api_key': os.getenv("API_KEY"), 
        'local_ai_url': "http://localhost:8000", 
        'rerank_model': rerank_model
    }
    
    answer = ask_rag_system(user_input, db_config, ai_config)
    return jsonify({"answer": answer})

# --- ส่วนที่ 3: ระบบอัปโหลดไฟล์ ---
@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('files')
    image_paths = []
    for file in files:
        path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename))
        file.save(path)
        image_paths.append(path)

    try:
        # ใช้ชื่อตัวแปรตามที่คุณแจ้งมา
        typhoon_key = os.getenv("TYPHOON_OCR_API_KEY") 
        
        # 1. OCR (Typhoon)
        chunks = run_ocr_and_chunk(image_paths, typhoon_key)
        
        # 2. Re-format สำหรับ Embedding
        formatted = [{"chunk_id": i, "text_to_embed": c['content'], "header": c['header'], "page": [1]} for i, c in enumerate(chunks)]
        
        # 3. Embedding & Save
        docs = generate_embeddings(formatted)
        save_to_mongodb(docs, os.getenv("DB_KEY"), "Knowledge_hub", "Data_project")
        
        # ลบไฟล์ชั่วคราว
        for p in image_paths: os.remove(p)
        
        return jsonify({"message": "Upload Success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/embed', methods=['POST'])
def get_embed():
    try:
        data = request.json
        text = data.get('text')
        if not text:
            return jsonify({"error": "No text provided"}), 400
            
        # ใช้ embed_model_local ที่โหลดไว้ที่ Global บรรทัดที่ 26 ใน main.py
        embedding = embed_model_local.encode(text).tolist()
        return jsonify({"embedding": embedding})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=8000)