from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)  # Permitir CORS para todas las rutas

client = MongoClient('mongodb://localhost:27017/')
db = client['comerciotech']

clientes_col = db['clientes']
productos_col = db['productos']
pedidos_col = db['pedidos']

@app.route('/existe_id/<string:id_cliente>', methods=['GET'])
def existe_id(id_cliente):
    existe = clientes_col.find_one({"_id": id_cliente}) is not None
    return jsonify({"existe": existe})

@app.route('/crear', methods=['POST'])
def crear_cliente():
    data = request.get_json()
    if clientes_col.find_one({"_id": data['_id']}):
        return "Cliente con ese ID ya existe", 400
    clientes_col.insert_one(data)
    return "Cliente creado exitosamente"

@app.route('/leer', methods=['GET'])
def leer_clientes():
    clientes = list(clientes_col.find({}, {'_id': 1, 'nombre': 1, 'apellidos': 1, 'direccion': 1, 'fechaRegistro': 1}))
    for c in clientes:
        c['_id'] = str(c['_id'])
    return jsonify(clientes)

@app.route('/eliminar/<string:id_cliente>', methods=['DELETE'])
def eliminar_cliente(id_cliente):
    res = clientes_col.delete_one({"_id": id_cliente})
    if res.deleted_count == 0:
        return "Cliente no encontrado", 404
    return "Cliente eliminado"

@app.route('/crear_producto', methods=['POST'])
def crear_producto():
    data = request.get_json()
    if productos_col.find_one({"_id": data['_id']}):
        return "Producto con ese ID ya existe", 400
    productos_col.insert_one(data)
    return "Producto creado exitosamente"

@app.route('/leer_productos', methods=['GET'])
def leer_productos():
    productos = list(productos_col.find({}, {'_id': 1, 'codigo': 1, 'nombre': 1, 'precio': 1, 'stock': 1, 'estado': 1}))
    for p in productos:
        p['_id'] = str(p['_id'])
    return jsonify(productos)

@app.route('/eliminar_producto/<string:id_producto>', methods=['DELETE'])
def eliminar_producto(id_producto):
    res = productos_col.delete_one({"_id": id_producto})
    if res.deleted_count == 0:
        return "Producto no encontrado", 404
    return "Producto eliminado"

@app.route('/crear_pedido', methods=['POST'])
def crear_pedido():
    data = request.get_json()
    # Validar cliente existe
    if not clientes_col.find_one({"_id": data['cliente_id']}):
        return "Cliente no existe", 400
    # Validar pedido ID único
    if pedidos_col.find_one({"_id": data['_id']}):
        return "Pedido con ese ID ya existe", 400
    # Validar productos existen y calcular total
    total = 0
    for p in data['productos']:
        prod = productos_col.find_one({"_id": p['id']})
        if not prod:
            return f"Producto con ID {p['id']} no existe", 400
        total += prod.get('precio', 0)
    data['total_compra'] = total
    pedidos_col.insert_one(data)
    return "Pedido creado exitosamente"

@app.route('/leer_pedidos', methods=['GET'])
def leer_pedidos():
    pedidos = list(pedidos_col.find({}, {'_id': 1, 'cliente_id': 1, 'fecha_pedido': 1, 'productos': 1, 'total_compra': 1, 'metodo_pago': 1}))
    for p in pedidos:
        p['_id'] = str(p['_id'])
    return jsonify(pedidos)

@app.route('/eliminar_pedido/<string:id_pedido>', methods=['DELETE'])
def eliminar_pedido(id_pedido):
    res = pedidos_col.delete_one({"_id": id_pedido})
    if res.deleted_count == 0:
        return "Pedido no encontrado", 404
    return "Pedido eliminado"

if __name__ == '__main__':
    app.run(debug=True)
