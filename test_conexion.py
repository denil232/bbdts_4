from pymongo import MongoClient

try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["comerciotech"]
    print("✅ Conexión exitosa a MongoDB.")
    print("Clientes:")
    for cliente in db.clientes.find():
        print(cliente)
except Exception as e:
    print("❌ Error de conexión:", e)
