import requests

def get_embedding(text, local_api_url):
    """ส่งข้อความไปทำ Embedding ที่เครื่อง Local"""
    response = requests.post(f"{local_api_url}/embed", json={"text": text})
    response.raise_for_status()
    return response.json()["embedding"]

def get_batch_embeddings(texts, local_api_url):
    """ส่ง List ของข้อความไปทำ Batch Embedding ที่เครื่อง Local"""
    response = requests.post(f"{local_api_url}/embed_batch", json={"texts": texts})
    response.raise_for_status()
    return response.json()["embeddings"]

def get_rerank_scores(query, documents, local_api_url):
    """ส่งคำถามและรายการเอกสารไปให้ Local Reranker คัดเกรด"""
    response = requests.post(
        f"{local_api_url}/rerank", 
        json={"query": query, "documents": documents}
    )
    response.raise_for_status()
    return response.json()["scores"]