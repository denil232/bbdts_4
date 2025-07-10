from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db = client["comerciotech"]
coleccion = db["clientes"]

@app.route('/crear', methods=['POST'])
def crear_cliente():
    datos = request.json
    datos["fecha_registro"] = datetime.now()
    try:
        coleccion.insert_one(datos)
        return "Cliente creado", 200
    except Exception as e:
        return str(e), 400

@app.route('/leer', methods=['GET'])
def leer_clientes():
    clientes = list(coleccion.find({}, {"_id": 1, "nombre": 1, "apellidos": 1, "direccion": 1}))
    for c in clientes:
        c["_id"] = str(c["_id"])
    return jsonify(clientes)

@app.route('/actualizar', methods=['PUT'])
def actualizar_cliente():
    datos = request.json
    resultado = coleccion.update_one({"_id": datos["_id"]}, {"$set": {"nombre": datos["nombre"]}})
    if resultado.modified_count:
        return "Cliente actualizado", 200
    else:
        return "No se encontró el cliente", 404

@app.route('/eliminar/<int:cliente_id>', methods=['DELETE'])
def eliminar_cliente(cliente_id):
    resultado = coleccion.delete_one({"_id": cliente_id})
    if resultado.deleted_count:
        return "Cliente eliminado", 200
    else:
        return "No se encontró el cliente", 404

if __name__ == '__main__':
    app.run(debug=True)
