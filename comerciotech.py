from pymongo import MongoClient
from datetime import datetime
import re

cliente = MongoClient("mongodb://localhost:27017/")
db = cliente["comerciotech"]

id_regex = re.compile(r'^[1-9][0-9]{0,5}$')
texto_regex = re.compile(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$')

def validar_id(id_str):
    return bool(id_regex.fullmatch(id_str.strip())) if isinstance(id_str, str) else False

def validar_texto(texto):
    return bool(texto_regex.fullmatch(texto.strip())) if isinstance(texto, str) else False

def validar_fecha(fecha_str):
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        return datetime(2000,1,1) <= fecha <= datetime.now()
    except:
        return False

def crear_cliente(id_cliente, nombre, apellidos, calle, numero, ciudad, fecha):
    if not validar_id(id_cliente):
        raise ValueError("ID inválido: debe ser numérico, 1-6 dígitos y empezar con 1-9")
    if not validar_texto(nombre):
        raise ValueError("Nombre inválido: solo letras y espacios permitidos")
    if not validar_texto(apellidos):
        raise ValueError("Apellidos inválidos: solo letras y espacios permitidos")
    if not validar_texto(ciudad):
        raise ValueError("Ciudad inválida: solo letras y espacios permitidos")
    if not validar_fecha(fecha):
        raise ValueError("Fecha inválida: debe estar entre 2000-01-01 y hoy")

    cliente = {
        "_id": id_cliente.strip(),
        "nombre": nombre.strip(),
        "apellidos": apellidos.strip(),
        "direccion": {
            "calle": calle.strip() if calle else "",
            "numero": numero,
            "ciudad": ciudad.strip()
        },
        "fechaRegistro": datetime.strptime(fecha, "%Y-%m-%d")
    }
    return db.clientes.insert_one(cliente).inserted_id

def actualizar_cliente(id_cliente, nuevos_datos):
    if not validar_id(id_cliente):
        raise ValueError("ID inválido para actualización")
    if 'nombre' in nuevos_datos and not validar_texto(nuevos_datos['nombre']):
        raise ValueError("Nombre inválido para actualización")
    if 'apellidos' in nuevos_datos and not validar_texto(nuevos_datos['apellidos']):
        raise ValueError("Apellidos inválidos para actualización")
    if 'direccion' in nuevos_datos and 'ciudad' in nuevos_datos['direccion']:
        if not validar_texto(nuevos_datos['direccion']['ciudad']):
            raise ValueError("Ciudad inválida para actualización")

    db.clientes.update_one({"_id": id_cliente.strip()}, {"$set": nuevos_datos})

def eliminar_cliente(id_cliente):
    if not validar_id(id_cliente):
        raise ValueError("ID inválido para eliminación")
    db.clientes.delete_one({"_id": id_cliente.strip()})
