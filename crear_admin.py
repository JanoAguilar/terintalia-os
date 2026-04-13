from conexion import conectar_db
from datetime import datetime

db = conectar_db()

def inyectar_director():
    admin_data = {
        "especialista_id_interno": "DIR-001",
        "nombre_completo": "DIRECTOR GENERAL TERINTALIA",
        "correo_corporativo": "admin@terintalia.com",
        "password": "Admin2026", # Cambia esta clave por la que tú quieras
        "cedula": "00000000",
        "contacto": "0000000000",
        "especialidad": "DIRECTOR",
        "rol": "DIRECTOR",
        "estatus": "ACTIVO",
        "fecha_registro": datetime.now()
    }
    
    # Lo guardamos en la colección de especialistas
    db.collection("especialistas").document("DIR-001").set(admin_data)
    print("✅ Director creado con éxito. Ya puedes entrar con admin@terintalia.com")

inyectar_director()