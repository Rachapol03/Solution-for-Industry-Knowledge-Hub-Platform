from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, CrossEncoder
import uvicorn

app = FastAPI()

# ตั้งค่า CORS เพื่อให้ Flask หรือ Frontend ยิงหาได้
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# โหลดโมเดลตัวจริงที่เครื่อง Local
print("🚀 Loading BGE-M3 and Reranker-V2-M3 on Local Machine...")
embed_model = SentenceTransformer('BAAI/bge-m3')
rerank_model = CrossEncoder('BAAI/bge-reranker-v2-m3')

class EmbedRequest(BaseModel):
    text: str

class BatchEmbedRequest(BaseModel):
    texts: list

class RerankRequest(BaseModel):
    query: str
    documents: list

@app.get("/")
async def health_check():
    return {"status": "ready", "model": "BGE-M3 & Reranker-V2"}

@app.post("/embed")
async def embed(request: EmbedRequest):
    vector = embed_model.encode(request.text).tolist()
    return {"embedding": vector}

@app.post("/embed_batch")
async def embed_batch(request: BatchEmbedRequest):
    vectors = embed_model.encode(request.texts, batch_size=32).tolist()
    return {"embeddings": vectors}

@app.post("/rerank")
async def rerank(request: RerankRequest):
    pairs = [[request.query, doc] for doc in request.documents]
    scores = rerank_model.predict(pairs).tolist()
    return {"scores": scores}

if __name__ == "__main__":
    # รันที่พอร์ต 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)