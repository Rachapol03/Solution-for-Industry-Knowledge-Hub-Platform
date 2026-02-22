from pymongo import MongoClient

def save_to_mongodb(documents, mongo_uri, db_name, coll_name):
    """
    ฟังก์ชันสำหรับบันทึกข้อมูลที่ทำ Embedding แล้วลง MongoDB
    :param documents: List ของเอกสารพร้อม Vector
    """
    if not documents:
        print("ไม่มีข้อมูลที่จะบันทึก")
        return 0

    # เชื่อมต่อ MongoDB Atlas
    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[coll_name]
    
    # บันทึกข้อมูล
    result = collection.insert_many(documents)
    total_inserted = len(result.inserted_ids)
    
    print(f"บันทึกข้อมูลเข้า MongoDB เรียบร้อยแล้ว ทั้งหมด {total_inserted} รายการ")
    
    client.close()
    return total_inserted