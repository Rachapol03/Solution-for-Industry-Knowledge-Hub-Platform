from pymongo import MongoClient
from openai import OpenAI
from embedding import get_embedding, get_rerank_scores # เรียกใช้ตัว bridge

def ask_rag(user_question, config):
    """
    config: dict ที่เก็บ db_key, api_key, local_api_url, base_url ไว้
    """
    client = MongoClient(config['db_key'])
    collection = client['Knowledge_hub']['Data_project']
    
    kku_client = OpenAI(api_key=config['api_key'], base_url=config['base_url'])

    # Step 1: Retrieval (ดึงผ่าน Vector Search)
    query_vector = get_embedding(user_question, config['local_api_url'])
    
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_vector,
                "path": "embedding",
                "numCandidates": 100,
                "limit": 10 
            }
        },
        {"$project": {"_id": 0, "text": 1}}
    ]
    initial_docs = list(collection.aggregate(pipeline))
    
    if not initial_docs:
        return "ขออภัย ไม่พบข้อมูลที่เกี่ยวข้อง"

    # Step 2: Reranking (ส่งไปคัดที่เครื่อง Local)
    docs_text = [doc['text'] for doc in initial_docs]
    scores = get_rerank_scores(user_question, docs_text, config['local_api_url'])
    
    for i in range(len(initial_docs)):
        initial_docs[i]['rerank_score'] = scores[i]
    
    reranked_docs = sorted(initial_docs, key=lambda x: x['rerank_score'], reverse=True)
    top_docs = reranked_docs[:5]

    # Step 3: Generation (LLM)
    context_text = "\n\n".join([f"[แหล่งข้อมูลที่ {i+1}]: {d['text']}" for i, d in enumerate(top_docs)])
    
    system_instruction = (
        "คุณคือผู้ช่วยอัจฉริยะที่แม่นยำที่สุด หากพบข้อมูลที่คล้ายกันจากหลายแหล่ง "
        "จงสรุปและเปรียบเทียบเป็นข้อๆ (1, 2, 3...) และทำให้คำตอบของคุณมีความชัดเจนและกระชับที่สุด โดยเข้าใจง่ายที่สุด และจัดการให้คำตอบมีความสะอาดที่สุดเท่าที่จะเป็นไปได้ โดยพยายามหลีกเลี่ยงการใช้เครื่องหมาย * ตอบ"
    )

    response = kku_client.chat.completions.create(
        model="gemini-3-pro-preview", 
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"ข้อมูลประกอบ:\n{context_text}\n\nคำถาม: {user_question}"},
        ],
        temperature=0.2
    )
    return response.choices[0].message.content