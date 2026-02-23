# pip install -U FlagEmbedding sentence-transformers

from sentence_transformers import SentenceTransformer

# โหลดโมเดล
model = SentenceTransformer('BAAI/bge-m3')

# ข้อความที่ต้องการทดสอบ (รองรับภาษาไทยเต็มรูปแบบ)
sentences = [
    "วิธีการลดน้ำหนักแบบสุขภาพดี",
    "How to lose weight healthily",
    "กินอาหารให้ครบ 5 หมู่และออกกำลังกายสม่ำเสมอ",
    "วันนี้อากาศดีจังเลย"
]

# แปลงข้อความเป็น Vector (Embeddings)
embeddings = model.encode(sentences, normalize_embeddings=True)

txt = "การออกกำลังกายเป็นประจำช่วยให้สุขภาพดีขึ้น"
txt_embedding = model.encode([txt], normalize_embeddings=True)

# ทดสอบหาความคล้ายคลึง (Similarity) ระหว่างประโยคแรกกับประโยคอื่นๆ
similarity = txt_embedding @ embeddings.T
print(f"Similarity scores for '{txt}':")
for i, score in enumerate(similarity[0]):
    print("Embeddings shape:", embeddings[i].shape)
    print(f"- {sentences[i]}: {score:.4f}")