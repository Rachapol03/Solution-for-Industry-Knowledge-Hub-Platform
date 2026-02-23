import os
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Import modules ที่คุณเขียนไว้
from pdf_to_image import pdf_to_images
from ocr_image_to_text import run_ocr
from chunk_text import chunk_text
from embedding_input_data import create_embeddings_to_db
from rag_system import ask_rag

load_dotenv()

app = Flask(__name__)

# --- Configuration ---
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CONFIG = {
    "db_key": os.getenv("DB_KEY"),
    "api_key": os.getenv("API_KEY"),
    "base_url": "https://gen.ai.kku.ac.th/api/v1",
    "local_api_url": "http://127.0.0.1:8000" # แก้เป็น URL ngrok เมื่อขึ้น cloud
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({"error": "No message"}), 400
    try:
        answer = ask_rag(user_input, CONFIG)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_data():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '' or not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type. Only PDF, JPG, PNG allowed"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        # 1. จัดการไฟล์ตามประเภท
        ext = filename.rsplit('.', 1)[1].lower()
        image_paths = []
        
        if ext == 'pdf':
            image_paths = pdf_to_images(filepath, "output_images")
        else:
            image_paths = [filepath]

        # 2. OCR
        txt_paths = run_ocr(image_paths, "output_texts")

        # 3. Chunking
        texts_to_embed, raw_chunks, page_ranges = chunk_text(txt_paths)

        # 4. Embedding & Database
        create_embeddings_to_db(
            texts_to_embed, 
            raw_chunks, 
            page_ranges, 
            CONFIG["local_api_url"],
            CONFIG["db_key"],
            "Knowledge_hub",
            "Data_project"
        )

        return jsonify({"message": f"Successfully processed {filename}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)