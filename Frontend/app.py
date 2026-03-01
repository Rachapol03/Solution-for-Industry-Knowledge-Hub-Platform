import os
import threading
import time
import uuid

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

# ================== UTIL ==================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ================== MEMORY ==================

conversations = {}
processing_queue = []
processing_lock = threading.Lock()
system_log = []
processing_thread = None

def log(msg):
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    entry = f"[{ts}] {msg}"
    system_log.append(entry)
    print(entry)

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


@app.route("/")
def dashboard():
    total_documents = len(os.listdir(UPLOAD_FOLDER))

    with processing_lock:
        queue_count = len(processing_queue)

    recent_logs = system_log[-10:]  # เอา 10 รายการล่าสุด
    # quick health checks for backend and embedding service
    backend_up = False
    embed_up = False
    try:
        r = requests.get(BACKEND_URL, timeout=1)
        backend_up = r.ok
    except Exception:
        backend_up = False
    try:
        r2 = requests.get(EMBED_URL, timeout=1)
        embed_up = r2.ok
    except Exception:
        embed_up = False

    return render_template(
        "dashboard.html",
        total_documents=total_documents,
        queue_count=queue_count,
        recent_logs=recent_logs,
        backend_up=backend_up,
        embed_up=embed_up,
    )


@app.route('/health')
def health():
    """Return combined health for frontend, main backend and embed server."""
    status = {"frontend": True}
    try:
        status['backend'] = requests.get(BACKEND_URL, timeout=1).ok
    except Exception:
        status['backend'] = False
    try:
        status['embed'] = requests.get(EMBED_URL, timeout=1).ok
    except Exception:
        status['embed'] = False
    return jsonify(status)


@app.route("/rag", methods=["GET", "POST"])
def rag():
    mode = request.args.get("mode", "chat")
    conv_id = request.args.get("conv")

    if mode == "history":
        return render_template(
            "rag.html",
            mode="history",
            conversations=conversations
        )

    if request.method == "POST":
        message = request.form.get("message", "")

        if not conv_id:
            conv_id = str(uuid.uuid4())
            conversations[conv_id] = []

        conversations.setdefault(conv_id, [])
        conversations[conv_id].append({"role": "user", "content": message})

        # Forward the message to the main backend /chat endpoint
        try:
            resp = requests.post(f"{BACKEND_URL}/chat", json={"message": message}, timeout=15)
            if resp.ok:
                data = resp.json()
                answer = data.get('answer') or data.get('response') or ''
            else:
                answer = f"Backend error: {resp.status_code}"
        except Exception as e:
            answer = f"Error contacting backend: {e}"

        conversations[conv_id].append({"role": "bot", "content": answer})

    messages = conversations.get(conv_id, [])

    return render_template(
        "rag.html",
        mode="chat",
        messages=messages,
        conv_id=conv_id
    )

@app.route("/community")
def community_list():
    return render_template("community.html", page="list")


@app.route("/community/create")
def community_create():
    return render_template("community.html", page="create")


# In-memory community posts store
community_posts = []
import uuid


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


@app.route('/community/generate_summary', methods=['POST'])
def community_generate_summary():
    data = request.get_json() or {}
    pid = data.get('id')
    post = next((p for p in community_posts if p['id']==pid), None)
    if not post:
        return jsonify({'error':'post not found'}), 404
    # simple mock summary: first 3 sentences or first 300 chars
    content = post.get('content','')
    summary = content.split('.')[:3]
    summary = '.'.join([s.strip() for s in summary if s.strip()])
    if not summary:
        summary = content[:300]
    return jsonify({'summary': summary})


@app.route("/logbook")
def logbook():
    return render_template("logbook.html")


@app.route("/upload", methods=["POST"])
def upload():
    # ✅ ตรวจ file
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # ✅ รับค่าจาก form
    title = request.form.get('title')
    category = request.form.get('category')
    access_level = request.form.get('access_level', '')
    tags = request.form.get('tags', '')

    # ✅ Validate เพิ่ม (สำคัญ)
    if not title:
        return jsonify({"error": "Title is required"}), 400

    if not category:
        return jsonify({"error": "Category is required"}), 400

    # ✅ เตรียม forward ไป backend หลัก
    files = {
        'file': (
            secure_filename(file.filename),
            file.stream,
            file.mimetype
        )
    }

    data = {
        'title': title,
        'category': category,
        'access_level': access_level,
        'tags': tags
    }

    try:
        resp = requests.post(
            f"{BACKEND_URL}/upload",
            files=files,
            data=data,
            timeout=120
        )

        if resp.ok:
            log(f"Forwarded upload to backend: {file.filename} ({title})")
            return (resp.content, resp.status_code, resp.headers.items())
        else:
            return jsonify({
                "error": "Backend upload failed",
                "detail": resp.text
            }), resp.status_code

    except Exception as e:
        return jsonify({
            "error": "Error contacting backend",
            "detail": str(e)
        }), 500


@app.route("/queue")
def get_queue():
    with processing_lock:
        return jsonify(processing_queue)


@app.route("/system_log")
def get_log():
    return jsonify(system_log)


@app.route("/start_indexing", methods=["POST"])
def start_indexing():
    global processing_thread
    if processing_thread and processing_thread.is_alive():
        return jsonify({"status": "already_running"})
    processing_thread = threading.Thread(target=background_processor, daemon=True)
    processing_thread.start()
    return jsonify({"status": "started"})


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


if __name__ == "__main__":
    print(f"Frontend starting on http://127.0.0.1:{FRONTEND_PORT} -> backend={BACKEND_URL} embed={EMBED_URL}")
    app.run(debug=True, port=FRONTEND_PORT)