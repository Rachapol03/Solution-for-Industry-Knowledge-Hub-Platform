from flask import Flask, render_template, request, redirect, url_for, jsonify, send_from_directory
import os
import threading
import time
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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

    return render_template(
        "dashboard.html",
        total_documents=total_documents,
        queue_count=queue_count,
        recent_logs=recent_logs
    )


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

        conversations[conv_id].append({
            "role": "user",
            "content": message
        })

        conversations[conv_id].append({
            "role": "bot",
            "content": "Sample RAG response from knowledge base."
        })

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
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    filename = secure_filename(file.filename)
    save_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(save_path)

    title = request.form.get('title', '')
    category = request.form.get('category', '')
    access_level = request.form.get('access_level', '')
    tags = request.form.get('tags', '')

    item = {
        "filename": filename,
        "title": title,
        "category": category,
        "access_level": access_level,
        "tags": tags,
        "status": "Uploaded"
    }
    with processing_lock:
        processing_queue.append(item)

    log(f"Uploaded: {filename} ({title})")

    return jsonify({"status": "ok", "item": item})


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
    app.run(debug=True)