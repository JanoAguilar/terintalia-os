import streamlit as st
from datetime import datetime
from google.cloud import firestore

# --- FUNCIONES ORIGINALES (INTACTAS) ---
def obtener_siguiente_id(db):
    prefijo = f"TER{datetime.now().strftime('%Y%m')}"
    docs = db.collection("especialistas").where("especialista_id_interno", ">=", prefijo).get()
    contador = 1
    for doc in docs:
        if prefijo in doc.to_dict().get("especialista_id_interno", ""):
            contador += 1
    return f"{prefijo}-#{contador}"

def generar_correo(nombre, apellido):
    nom = nombre.strip().split()[0].lower()
    ape = apellido.strip().split()[0].lower()
    return f"{nom}.{ape}@terintalia.com"

def render_alta_especialistas(db):
    # Título elegante y minimalista
    st.markdown("<h2 style='color: #164032; font-weight: 600; font-size: 26px; margin-bottom: 0px;'>Gestión de Especialistas</h2>", unsafe_allow_html=True)
    st.caption("Añada profesionales de la salud al directorio institucional y genere sus credenciales de acceso.")
    st.write("")

    if 'confirmando' not in st.session_state:
        st.session_state.confirmando = False

    # --- PASO 1: CAPTURA DE DATOS ---
    if not st.session_state.confirmando:
        
        # Quitamos el st.form temporalmente para que el campo "OTRA" aparezca mágicamente al instante
        # BLOQUE 1: DATOS DEL PROFESIONAL
        with st.container(border=True):
            st.markdown("<h4 style='color: #164032; font-size: 15px; margin-bottom: 5px;'>👤 Datos del Profesional</h4>", unsafe_allow_html=True)
            
            f1_c1, f1_c2 = st.columns(2)
            with f1_c1: nombre = st.text_input("Nombre(s)").upper()
            with f1_c2: apellido = st.text_input("Apellido(s)").upper()

            f2_c1, f2_c2 = st.columns(2)
            with f2_c1: cedula = st.text_input("Cédula profesional").upper()
            with f2_c2: contacto = st.text_input("Número de contacto celular (10 dígitos)", max_chars=10)

        # BLOQUE 2: ACCESO Y ESPECIALIDAD
        with st.container(border=True):
            st.markdown("<h4 style='color: #E67E22; font-size: 15px; margin-bottom: 5px;'>🔐 Perfil y Acceso al Sistema</h4>", unsafe_allow_html=True)
            
            f3_c1, f3_c2 = st.columns(2)
            with f3_c1:
                esp_opcion = st.selectbox("Área de especialidad", ["Psicología", "Nutrición", "Fisioterapia", "Otra"])
                
                # Lógica reactiva para "OTRA"
                especialidad_final = esp_opcion.upper()
                if esp_opcion == "Otra":
                    especialidad_manual = st.text_input("Especifique la especialidad").upper()
                    especialidad_final = especialidad_manual

            with f3_c2:
                password = st.text_input("Contraseña inicial", type="password")

        st.write("")
        if st.button("🔍 REVISAR REGISTRO", use_container_width=True):
            # TUS VALIDACIONES ORIGINALES
            if especialidad_final == "DIRECTOR":
                st.error("⚠️ 'DIRECTOR' no es una especialidad válida para registro clínico.")
            elif nombre and apellido and cedula and contacto and password:
                if len(contacto) != 10 or not contacto.isdigit():
                    st.error("⚠️ El teléfono debe contener exactamente 10 dígitos numéricos.")
                else:
                    st.session_state.temp_datos = {
                        "id_doc": obtener_siguiente_id(db),
                        "nombre_completo": f"{nombre} {apellido}".strip(),
                        "cedula": cedula,
                        "contacto": contacto,
                        "especialidad": especialidad_final,
                        "correo": generar_correo(nombre, apellido),
                        "password": password
                    }
                    st.session_state.confirmando = True
                    st.rerun()
            else:
                st.error("⚠️ Por favor, rellena todos los campos para continuar.")

    # --- PASO 2: CONFIRMACIÓN ---
    else:
        datos = st.session_state.temp_datos
        st.info("✨ **Verifique la información antes de generar el usuario**")
        
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"👤 **Nombre:** {datos['nombre_completo']}")
                st.write(f"🎓 **Especialidad:** {datos['especialidad']}")
                st.write(f"📇 **Cédula:** {datos['cedula']}")
            with c2:
                st.write(f"📞 **Contacto:** {datos['contacto']}")
                st.write(f"🆔 **ID Interno:** `{datos['id_doc']}`")
                st.write(f"📧 **Correo Asignado:** `{datos['correo']}`")

        st.markdown("<h4 style='color: #164032; font-size: 15px;'>¿Crear Perfil del Especialista?</h4>", unsafe_allow_html=True)
        col_si, col_no = st.columns(2)
        with col_si:
            if st.button("✅ SÍ, GUARDAR Y CREAR ACCESO", type="primary", use_container_width=True):
                # TU GUARDADO ORIGINAL EN FIREBASE
                db.collection("especialistas").document(datos['id_doc']).set({
                    "especialista_id_interno": datos['id_doc'],
                    "nombre_completo": datos['nombre_completo'],
                    "correo_corporativo": datos['correo'],
                    "cedula": datos['cedula'],
                    "contacto": datos['contacto'],
                    "especialidad": datos['especialidad'],
                    "password": datos['password'],
                    "rol": "ESPECIALISTA", 
                    "estatus": "ACTIVO",
                    "fecha_registro": firestore.SERVER_TIMESTAMP
                })
                st.success(f"¡El especialista {datos['nombre_completo']} ha sido registrado con éxito!")
                st.balloons()
                st.session_state.confirmando = False
        with col_no:
            if st.button("❌ REGRESAR Y CORREGIR", use_container_width=True):
                st.session_state.confirmando = False
                st.rerun()