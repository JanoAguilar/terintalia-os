import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

def conectar_db():
    if not firebase_admin._apps:
        # 1. INTENTO DE CONEXIÓN EN LA NUBE (Seguro)
        if "firebase" in st.secrets:
            # Si detecta que estamos en la nube, saca las llaves de la bóveda
            cert_dict = dict(st.secrets["firebase"])
            cred = credentials.Certificate(cert_dict)
            
        # 2. CONEXIÓN LOCAL (Tu computadora)
        else:
            # Si no hay bóveda, asume que estás en tu PC y usa el archivo JSON local
            nombre_llave = "terintalia-expedientes-firebase-adminsdk-fbsvc-879cea1af8.json"
            cred = credentials.Certificate(nombre_llave)
            
        # 3. INICIALIZACIÓN CON PERMISO DE DISCO DURO (STORAGE)
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'terintalia-expedientes.firebasestorage.app'
        })
    
    return firestore.client()
