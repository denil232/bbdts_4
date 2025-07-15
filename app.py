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

# ------------ CLIENTES ---------------

@app.route('/existe_id/<string:id_cliente>', methods=['GET'])
def existe_id(id_cliente):
    existe = clientes_col.find_one({"_id": id_cliente}) is not None
    return jsonify({"existe": existe})

@app.route('/crear', methods=['POST'])
def crear_cliente():
    data = request.get_json()
    if clientes_col.find_one({"_id": data['_id']}):
        return jsonify({"error": "Cliente con ese ID ya existe"}), 400
    clientes_col.insert_one(data)
    return jsonify({"mensaje": "Cliente creado exitosamente"}), 201

@app.route('/leer', methods=['GET'])
def leer_clientes():
    clientes = list(clientes_col.find({}, {'_id': 1, 'nombre': 1, 'apellidos': 1, 'direccion': 1, 'fechaRegistro': 1}))
    for c in clientes:
        c['_id'] = str(c['_id'])
    return jsonify(clientes)

@app.route('/cliente/<string:id_cliente>', methods=['GET'])
def obtener_cliente(id_cliente):
    cliente = clientes_col.find_one({"_id": id_cliente})
    if not cliente:
        return jsonify({"error": "Cliente no encontrado"}), 404
    cliente['_id'] = str(cliente['_id'])
    return jsonify(cliente)

@app.route('/editar_cliente/<string:id_cliente>', methods=['PUT'])
def editar_cliente(id_cliente):
    data = request.get_json()
    resultado = clientes_col.update_one({"_id": id_cliente}, {"$set": data})
    if resultado.matched_count == 0:
        return jsonify({"error": "Cliente no encontrado"}), 404
    return jsonify({"mensaje": "Cliente actualizado exitosamente"})

@app.route('/eliminar/<string:id_cliente>', methods=['DELETE'])
def eliminar_cliente(id_cliente):
    res = clientes_col.delete_one({"_id": id_cliente})
    if res.deleted_count == 0:
        return jsonify({"error": "Cliente no encontrado"}), 404
    return jsonify({"mensaje": "Cliente eliminado"}), 200

# ------------ PRODUCTOS -------------

@app.route('/crear_producto', methods=['POST'])
def crear_producto():
    data = request.get_json()
    if productos_col.find_one({"_id": data['_id']}):
        return jsonify({"error": "Producto con ese ID ya existe"}), 400
    productos_col.insert_one(data)
    return jsonify({"mensaje": "Producto creado exitosamente"}), 201

@app.route('/leer_productos', methods=['GET'])
def leer_productos():
    productos = list(productos_col.find({}, {'_id': 1, 'codigo': 1, 'nombre': 1, 'precio': 1, 'stock': 1, 'estado': 1}))
    for p in productos:
        p['_id'] = str(p['_id'])
    return jsonify(productos)

@app.route('/producto/<string:id_producto>', methods=['GET'])
def obtener_producto(id_producto):
    producto = productos_col.find_one({"_id": id_producto})
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404
    producto['_id'] = str(producto['_id'])
    return jsonify(producto)

@app.route('/editar_producto/<string:id_producto>', methods=['PUT'])
def editar_producto(id_producto):
    data = request.get_json()
    resultado = productos_col.update_one({"_id": id_producto}, {"$set": data})
    if resultado.matched_count == 0:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify({"mensaje": "Producto actualizado exitosamente"})

@app.route('/eliminar_producto/<string:id_producto>', methods=['DELETE'])
def eliminar_producto(id_producto):
    res = productos_col.delete_one({"_id": id_producto})
    if res.deleted_count == 0:
        return jsonify({"error": "Producto no encontrado"}), 404
    return jsonify({"mensaje": "Producto eliminado"}), 200

# ------------ PEDIDOS -------------

@app.route('/crear_pedido', methods=['POST'])
def crear_pedido():
    data = request.get_json()
    if not clientes_col.find_one({"_id": data['cliente_id']}):
        return jsonify({"error": "Cliente no existe"}), 400

    if pedidos_col.find_one({"_id": data['_id']}):
        return jsonify({"error": "Pedido con ese ID ya existe"}), 400

    total = 0
    for p in data['productos']:
        prod = productos_col.find_one({"_id": p['producto_id']})
        if not prod:
            return jsonify({"error": f"Producto con ID {p['producto_id']} no existe"}), 400
        if prod.get('stock', 0) < p['cantidad']:
            return jsonify({"error": f"Stock insuficiente para producto {prod['nombre']}"}), 400
        total += prod.get('precio', 0) * p['cantidad']
    data['total_compra'] = total

    pedidos_col.insert_one(data)
    return jsonify({"mensaje": "Pedido creado exitosamente"}), 201

@app.route('/leer_pedidos', methods=['GET'])
def leer_pedidos():
    pedidos = list(pedidos_col.find({}, {'_id': 1, 'cliente_id': 1, 'fecha_pedido': 1, 'productos': 1, 'total_compra': 1, 'metodo_pago': 1}))
    for p in pedidos:
        p['_id'] = str(p['_id'])
    return jsonify(pedidos)

@app.route('/pedido/<string:id_pedido>', methods=['GET'])
def obtener_pedido(id_pedido):
    pedido = pedidos_col.find_one({"_id": id_pedido})
    if not pedido:
        return jsonify({"error": "Pedido no encontrado"}), 404
    pedido['_id'] = str(pedido['_id'])
    return jsonify(pedido)

@app.route('/editar_pedido/<string:id_pedido>', methods=['PUT'])
def editar_pedido(id_pedido):
    data = request.get_json()
    if not clientes_col.find_one({"_id": data.get('cliente_id')}):
        return jsonify({"error": "Cliente no existe"}), 400

    total = 0
    for p in data.get('productos', []):
        prod = productos_col.find_one({"_id": p.get('producto_id')})
        if not prod:
            return jsonify({"error": f"Producto con ID {p.get('producto_id')} no existe"}), 400
        if prod.get('stock', 0) < p.get('cantidad', 0):
            return jsonify({"error": f"Stock insuficiente para producto {prod.get('nombre')}"}), 400
        total += prod.get('precio', 0) * p.get('cantidad', 0)
    data['total_compra'] = total

    resultado = pedidos_col.update_one({"_id": id_pedido}, {"$set": data})
    if resultado.matched_count == 0:
        return jsonify({"error": "Pedido no encontrado"}), 404
    return jsonify({"mensaje": "Pedido actualizado exitosamente"})

@app.route('/eliminar_pedido/<string:id_pedido>', methods=['DELETE'])
def eliminar_pedido(id_pedido):
    res = pedidos_col.delete_one({"_id": id_pedido})
    if res.deleted_count == 0:
        return jsonify({"error": "Pedido no encontrado"}), 404
    return jsonify({"mensaje": "Pedido eliminado"}), 200

if __name__ == '__main__':
    app.run(debug=True)
