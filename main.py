import os
import threading
import time
import uuid
import datetime
import json

from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# ==== RAG Modules ====
from pdf_to_image import pdf_to_images
from ocr_image_to_text import run_ocr
from chunk_text import chunk_text
from embedding_input_data import create_embeddings_to_db
from rag_system import ask_rag

import requests
from openai import OpenAI
from pymongo import MongoClient

load_dotenv()

app = Flask(__name__)

# ================= CONFIG =================

BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

CONFIG = {
    "db_key": os.getenv("DB_KEY"),
    "api_key": os.getenv("API_KEY"),
    "base_url": os.getenv("BASE_URL", "https://gen.ai.kku.ac.th/api/v1"),
    # ชี้ไปที่ Local embedding/ rerank service (server_local.py)
    # ใน production บน Render ให้กำหนดเป็น URL ของ ngrok หรือ endpoint ของ service
    "local_api_url": os.getenv("LOCAL_API_URL", "http://127.0.0.1:8000")
}

# ================= DATABASE =================

client = MongoClient(CONFIG["db_key"])
db = client['Knowledge_hub']
# ใช้แค่ตารางโพสต์อย่างเดียว
posts_collection = db['Community_post'] 

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ================== UTIL ==================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ================== MEMORY ==================

conversations = {}
processing_queue = []
processing_lock = threading.Lock()
system_log = []
processing_thread = None
community_posts = []

def log(msg):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    entry = f"[{ts}] {msg}"
    system_log.append(entry)
    print(entry)

def summarize_post(content, config):
    kku_client = OpenAI(api_key=config['api_key'], base_url=config['base_url'])
    messages = [
    {
        "role": "system", 
        "content": "คุณคือผู้ช่วย AI ที่เชี่ยวชาญด้านการจับใจความสำคัญ คุณมีหน้าที่สรุปบทความยาวๆ ให้สั้น กระชับ อ่านเข้าใจง่าย และใช้ภาษาที่เป็นธรรมชาติ"
    },
    {
        "role": "user", 
        "content": f"ช่วยสรุปใจความสำคัญของบทความต่อไปนี้ให้สั้น กระชับ และเข้าใจง่ายที่สุด ความยาวประมาณ 3-4 ประโยค (ไม่เกิน 1 ย่อหน้าสั้นๆ):\n\n{content}"
    }
]
    response = kku_client.chat.completions.create(
        model="gemini-3-pro-preview",
        messages=messages,
        temperature=0.2
    )
    return response.choices[0].message.content

def background_processor():
    while True:
        with processing_lock:
            if not processing_queue:
                break
            item = processing_queue.pop(0)
        fname = item.get('filename')
        log(f"Started processing: {fname}")
        time.sleep(1)
        log(f"Extracting text from {fname}... Done")
        time.sleep(1)
        log(f"Indexing {fname}... Done")
        time.sleep(0.5)
        log(f"Completed: {fname}")

# --- Routes ---

@app.route("/", methods=["GET", "POST"])
def rag():
    mode = request.args.get("mode", "chat")
    conv_id = request.args.get("conv")

    if mode == "history":
        return render_template("rag.html", mode="history", conversations=conversations)

    if request.method == "POST":
        message = request.form.get("message", "").strip()
        
        if not conv_id:
            conv_id = str(uuid.uuid4())
        if conv_id not in conversations:
            conversations[conv_id] = []

        # เก็บข้อความผู้ใช้
        conversations[conv_id].append({"role": "user", "content": message})

        debug = (request.args.get("debug", "0").lower() in ("1", "true", "yes")) or (request.form.get("debug", "0").lower() in ("1", "true", "yes"))

        final_answer = ""
        try:
            # === เรียกใช้ RAG ระบบจริง ===
            result = ask_rag(message, CONFIG, debug=debug) # ตอนนี้ส่งกลับมาเป็น Dictionary แล้ว

            # แยกคำตอบ Text กับ Images
            answer_text = result.get("answer", "ขออภัย ไม่พบคำตอบ")
            images = result.get("images", [])

            final_answer = answer_text

            # ถ้าระบบ RAG เจาะจงรูปมาให้ นำมาประกอบเป็น HTML ทันที
            if images:
                final_answer += "<br><br><div class='mt-2'><b>📸 รูปภาพประกอบ:</b><br>"
                final_answer += "<div style='display: flex; gap: 10px; overflow-x: auto; margin-top: 8px;'>"
                for img in images:
                    final_answer += f"<div style='border: 1px solid #e5e7eb; padding: 8px; border-radius: 8px; text-align: center; background-color: #fff;'>"
                    final_answer += f"<img src='{img.get('url', '')}' alt='{img.get('name', 'image')}' style='max-height: 150px; border-radius: 4px;'>"
                    final_answer += f"<p style='font-size: 12px; color: #6b7280; margin-top: 4px;'>อ้างอิง: หน้า {img.get('page', '-')}</p>"
                    final_answer += "</div>"
                final_answer += "</div></div>"

            # แสดง Debug info (ถ้าเปิด)
            if debug:
                debug_info = result.get("debug")
                if debug_info:
                    final_answer += "<details style='margin-top: 12px;'><summary style='cursor: pointer; color: #2563eb;'>🔍 Debug info (คลิกเพื่อดู)</summary>"
                    final_answer += "<pre style='background: #f3f4f6; padding: 10px; border-radius: 6px; overflow-x: auto;'>"
                    final_answer += json.dumps(debug_info, indent=2, ensure_ascii=False)
                    final_answer += "</pre></details>"

        except Exception as e:
            final_answer = f"เกิดข้อผิดพลาดจากระบบ RAG: {str(e)}"

        # เก็บคำตอบลงแชท
        conversations[conv_id].append({"role": "bot", "content": final_answer})
        # เก็บ debug flag ไว้ใน URL เพื่อให้ Debug info ยังคงแสดงในหน้าต่อ ๆ ไป
        return redirect(url_for('rag', conv=conv_id, debug="1" if debug else "0"))

    # ส่วนแสดงหน้าเว็บ (GET)
    messages = conversations.get(conv_id, [])
    return render_template("rag.html", mode="chat", messages=messages, conv_id=conv_id)


@app.route("/community")
def community_list():
    return render_template("community.html", page="list")


@app.route("/community/create")
def community_create():
    return render_template("community.html", page="create")


@app.route('/community/post', methods=['POST'])
def community_post():
    title = request.form.get('title','')
    ptype = request.form.get('type','discussion')
    content = request.form.get('content','')
    tags = request.form.get('tags','')

    files = []
    if 'files' in request.files:
        f = request.files.getlist('files')
        for fi in f:
            if fi and fi.filename:
                fname = secure_filename(fi.filename)
                path = os.path.join(UPLOAD_FOLDER, fname)
                fi.save(path)
                files.append(fname)

    post_data = {
        'id': str(uuid.uuid4()),
        'title': title,
        'type': ptype,
        'content': content,
        'tags': tags,
        'files': files,
        'created_at': time.time(),
        'author': 'Anonymous User'
    }
    
    # บันทึกข้อมูลไปยัง MongoDB
    try:
        posts_collection.insert_one(post_data)
        post_data.pop('_id', None) # ลบ _id ออกก่อนส่งกลับไปที่ Frontend
        
        log(f"Community post added to DB: {title}")
        return jsonify({'status':'ok', 'post': post_data})
    except Exception as e:
        log(f"DB Error (Create Post): {str(e)}")
        return jsonify({'error': 'Failed to save to database'}), 500


@app.route('/community/posts')
def community_posts_list():
    # ดึงข้อมูลโพสต์ทั้งหมดจาก MongoDB
    try:
        posts = list(posts_collection.find({}, {'_id': 0}))
        return jsonify(posts)
    except Exception as e:
        log(f"DB Error (Get Posts): {str(e)}")
        return jsonify([]), 500


@app.route("/community/post/<post_id>")
def community_detail(post_id):
    # ดึงข้อมูลโพสต์แบบเฉพาะเจาะจงจาก MongoDB (ไม่ต้องดึงคอมเมนต์แล้ว)
    try:
        post = posts_collection.find_one({'id': post_id}, {'_id': 0})
        if not post:
            return "Post not found", 404
        
        # จัดรูปแบบวันที่สำหรับแสดงผล
        if 'created_at' in post:
            post['date'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(float(post['created_at'])))
        else:
            post['date'] = "Unknown Date"

        post.setdefault('author', 'Anonymous User')

        return render_template("community.html", page="detail", post=post)
    except Exception as e:
        log(f"DB Error (Get Post Detail): {str(e)}")
        return "Database Connection Error", 500


@app.route('/community/generate_summary', methods=['POST'])
def community_generate_summary():
    data = request.get_json() or {}
    pid = data.get('id')
    
    # ดึงเนื้อหาจาก MongoDB ก่อนส่งไปสรุป
    try:
        post = posts_collection.find_one({'id': pid}, {'_id': 0})
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        content = post.get('content','')
        summary = summarize_post(content, CONFIG)
        return jsonify({'summary': summary})
        
    except Exception as e:
        return jsonify({'error': f'Error summarizing: {e}'}), 500



@app.route("/logbook")
def logbook():
    return render_template("logbook.html")


@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    title = request.form.get('title')
    category = request.form.get('category')
    access_level = request.form.get('access_level', '')
    tags = request.form.get('tags', '')

    if not title:
        return jsonify({"error": "Title is required"}), 400

    if not category:
        return jsonify({"error": "Category is required"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only PDF, JPG, PNG allowed"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    try:
        ext = filename.rsplit('.', 1)[1].lower()
        image_paths = []
        
        if ext == 'pdf':
            image_paths = pdf_to_images(filepath, "output_images")
        else:
            image_paths = [filepath]

        txt_paths = run_ocr(image_paths, "output_texts")
        texts_to_embed, raw_chunks, page_ranges = chunk_text(txt_paths)

        create_embeddings_to_db(
            texts_to_embed, 
            raw_chunks, 
            page_ranges, 
            CONFIG["local_api_url"],
            CONFIG["db_key"],
            "Knowledge_hub",
            "Data_project"
        )

        log(f"Upload completed: {filename} ({title})")
        return jsonify({"message": f"Successfully processed {filename}"})
    except Exception as e:
        log(f"Upload error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/chat", methods=['POST'])
def chat():
    """Chat endpoint for RAG queries."""
    user_input = request.json.get('message')
    debug = request.json.get('debug', False)
    if not user_input:
        return jsonify({"error": "No message"}), 400
    try:
        # รับค่าแบบ Dictionary จาก ask_rag และส่งออกผ่าน jsonify เลย
        result = ask_rag(user_input, CONFIG, debug=debug)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ให้เสิร์ฟภาพจากโฟลเดอร์ output_images สำหรับการโชว์รูปโดย chatbot
@app.route('/output_images/<path:filename>')
def output_image(filename):
    return send_from_directory(os.path.join(BASE_DIR, "output_images"), filename)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting on port {port}")
    app.run(host='0.0.0.0', port=port)