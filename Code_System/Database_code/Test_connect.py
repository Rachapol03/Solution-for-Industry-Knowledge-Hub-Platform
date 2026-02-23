try:
    # 1. ทดสอบเชื่อมต่อ
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    client.admin.command('ping')
    print("✅ เชื่อมต่อ Server สำเร็จ!")

    # 2. ทดสอบเขียนข้อมูล
    db = client["Knowledge_hub"]
    col = db["Document"]
    test_id = col.insert_one({"test": "connection", "status": "success"}).inserted_id
    print(f"✅ เขียนข้อมูลสำเร็จ! ID: {test_id}")

except Exception as e:
    print(f"❌ เกิดข้อผิดพลาด: {e}")