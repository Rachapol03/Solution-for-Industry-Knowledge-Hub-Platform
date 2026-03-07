from pymongo import MongoClient
from embedding import get_batch_embeddings # เรียกใช้ตัว bridge

def create_embeddings_to_db(texts_to_embed, raw_chunks, page_ranges, local_api_url, client_url, db_name, collection_db):
    # ดึง Embedding จาก Local Server
    all_embeddings = get_batch_embeddings(texts_to_embed, local_api_url)

    final_docs = []
    for i in range(len(texts_to_embed)):
        chunk_data = raw_chunks[i] 
        chunk_pages = [pr['page'] for pr in page_ranges 
                       if not (chunk_data['end'] <= pr['start'] or chunk_data['start'] >= pr['end'])]

        doc = {
            "chunk_id": i,
            "text": texts_to_embed[i],
            "header": chunk_data['header'].replace('#', '').strip(),
            "pages": sorted(list(set(chunk_pages))),
            "embedding": all_embeddings[i]
        }
        final_docs.append(doc)

    if final_docs:
        with MongoClient(client_url) as client:
            collection = client[db_name][collection_db]
            collection.insert_many(final_docs)
            print(f"บันทึก {len(final_docs)} chunks ลง MongoDB สำเร็จ")
    
    return final_docs