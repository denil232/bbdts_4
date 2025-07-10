from pymongo import MongoClient
from bson import ObjectId

# Conexión a MongoDB
cliente = MongoClient("mongodb://localhost:27017/")
db = cliente["comerciotech"]

# ========================
# CRUD Clientes
# ========================

def crear_cliente(nombre, apellidos, calle, numero, ciudad, fecha):
    cliente = {
        "nombre": nombre,
        "apellidos": apellidos,
        "direccion": {
            "calle": calle,
            "numero": numero,
            "ciudad": ciudad
        },
        "fechaRegistro": fecha
    }
    return db.clientes.insert_one(cliente).inserted_id

def buscar_clientes_por_ciudad(ciudad):
    return list(db.clientes.find({"direccion.ciudad": ciudad}))

def buscar_clientes_por_fecha(fecha):
    return list(db.clientes.find({"fechaRegistro": fecha}))

def actualizar_cliente(cliente_id, nuevos_datos):
    db.clientes.update_one({"_id": ObjectId(cliente_id)}, {"$set": nuevos_datos})

def eliminar_cliente(cliente_id):
    db.clientes.delete_one({"_id": ObjectId(cliente_id)})

# ========================
# CRUD Productos
# ========================

def crear_producto(codigo, nombre, precio, stock, estado):
    producto = {
        "codigo": codigo,
        "nombre": nombre,
        "precio": precio,
        "stock": stock,
        "estado": estado
    }
    return db.productos.insert_one(producto).inserted_id

def buscar_producto_por_codigo(codigo):
    return db.productos.find_one({"codigo": codigo})

# ========================
# CRUD Pedidos
# ========================

def crear_pedido(codigo, id_cliente, fecha, lista_productos, metodo_pago):
    total_compra = sum(p["total_comprado"] for p in lista_productos)
    pedido = {
        "codigo": codigo,
        "cliente": ObjectId(id_cliente),
        "fecha": fecha,
        "productos": lista_productos,
        "total_compra": total_compra,
        "metodo_pago": metodo_pago
    }
    return db.pedidos.insert_one(pedido).inserted_id

def ver_pedidos_cliente(id_cliente):
    return list(db.pedidos.find({"cliente": ObjectId(id_cliente)}))

# ========================
# PRUEBAS
# ========================

# Crear cliente
id_cliente = crear_cliente("Mario", "Rojas", "Los Alerces", 45, "Concepción", "2025-07-07")

# Crear producto
crear_producto("PRD001", "Tablet X", 150000, 30, "activo")

# Buscar producto
producto = buscar_producto_por_codigo("PRD001")

# Crear pedido
productos_pedido = [{
    "codigo": producto["codigo"],
    "nombre": producto["nombre"],
    "cantidad": 1,
    "precio_unitario": producto["precio"],
    "total_comprado": producto["precio"]
}]
crear_pedido("PED001", id_cliente, "2025-07-07", productos_pedido, "Tarjeta")

# Consultar clientes por ciudad
print("Clientes en Concepción:")
for c in buscar_clientes_por_ciudad("Concepción"):
    print(c)

# Consultar pedidos del cliente
print("Pedidos del cliente:")
for p in ver_pedidos_cliente(id_cliente):
    print(p)
