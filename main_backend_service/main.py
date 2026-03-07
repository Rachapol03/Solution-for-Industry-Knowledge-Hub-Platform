import os
import threading
import time
import uuid
import datetime

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
    "base_url": "https://gen.ai.kku.ac.th/api/v1",
    "local_api_url": "http://127.0.0.1:8000"
}

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
        
        # ป้องกัน Error
        answer = "" 
        
        if not conv_id:
            conv_id = str(uuid.uuid4())
        if conv_id not in conversations:
            conversations[conv_id] = []

        # เก็บข้อความผู้ใช้
        conversations[conv_id].append({"role": "user", "content": message})

        try:
            # === เรียกใช้ RAG ระบบจริง ===
            answer = ask_rag(message, CONFIG)

            # ถ้าผู้ใช้ถามถึง "รูป" หรือ "ภาพ" (ตัวอย่าง) ให้แนบรูปจากโฟลเดอร์ output_images
            if any(k in message.lower() for k in ("รูป", "ภาพ", "picture", "photo", "image")):
                img_dir = os.path.join(BASE_DIR, "output_images")
                if os.path.isdir(img_dir):
                    imgs = [f for f in os.listdir(img_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
                    if imgs:
                        fname = imgs[0]
                        answer += f"\n<br><img src='/output_images/{fname}' style='max-width:100%;height:auto;border-radius:8px;'>"

        except Exception as e:
            answer = f"เกิดข้อผิดพลาดจากระบบ RAG: {str(e)}"

        # เก็บคำตอบลงแชท
        conversations[conv_id].append({"role": "bot", "content": answer})
        return redirect(url_for('rag', conv=conv_id))

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

    post = {
        'id': str(uuid.uuid4()),
        'title': title,
        'type': ptype,
        'content': content,
        'tags': tags,
        'files': files,
        'created_at': time.time()
    }
    community_posts.append(post)
    log(f"Community post added: {title}")
    return jsonify({'status':'ok','post':post})


@app.route('/community/posts')
def community_posts_list():
    return jsonify(community_posts)


@app.route("/community/post/<post_id>")
def community_detail(post_id):
    post = next((p for p in community_posts if p.get('id') == post_id), None)
    if not post:
        return "Post not found", 404

    if 'created_at' in post:
        post['date'] = time.strftime('%Y-%m-%d %H:%M', time.localtime(post['created_at']))
    else:
        post['date'] = "Unknown Date"

    post.setdefault('author', 'Anonymous User')
    post.setdefault('comments', [])

    return render_template("community.html", page="detail", post=post)


@app.route('/community/post/<post_id>/comment', methods=['POST'])
def community_comment(post_id):
    post = next((p for p in community_posts if p.get('id') == post_id), None)
    if not post:
        return jsonify({'error': 'post not found'}), 404

    data = request.get_json() or {}
    text = data.get('text', '').strip()

    if not text:
        return jsonify({'error': 'comment text is required'}), 400

    if 'comments' not in post:
        post['comments'] = []

    new_comment = {
        'id': str(uuid.uuid4()),
        'text': text,
        'author': 'Anonymous User',
        'date': time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
    }
    
    post['comments'].append(new_comment)
    log(f"Comment added to post ID: {post_id}")
    
    return jsonify({'status': 'ok', 'comment': new_comment})


@app.route('/community/generate_summary', methods=['POST'])
def community_generate_summary():
    data = request.get_json() or {}
    pid = data.get('id')
    post = next((p for p in community_posts if p['id']==pid), None)
    if not post:
        return jsonify({'error':'post not found'}), 404
    
    content = post.get('content','')
    try:
        summary = summarize_post(content, CONFIG)
    except Exception as e:
        summary = f"Error summarizing: {e}"
    return jsonify({'summary': summary})


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
    if not user_input:
        return jsonify({"error": "No message"}), 400
    try:
        answer = ask_rag(user_input, CONFIG)
        return jsonify({"answer": answer})
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
    port = int(os.getenv("PORT", 5000))
    print(f"Frontend starting on http://127.0.0.1:{port}")
    app.run(debug=True, port=port)