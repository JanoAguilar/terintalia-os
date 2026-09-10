import streamlit as st
from datetime import datetime
from google.cloud import firestore

# --- FUNCIONES AUXILIARES ---
def obtener_siguiente_id(db):
    prefijo = f"TER{datetime.now().strftime('%Y%m')}"
    docs = db.collection("especialistas").where("especialista_id_interno", ">=", prefijo).get()
    contador = 1
    for doc in docs:
        if prefijo in doc.to_dict().get("especialista_id_interno", ""):
            contador += 1
    return f"{prefijo}-#{contador}"

def generar_correo(nombre, apellido):
    if not nombre or not apellido:
        return ""
    nom = nombre.strip().split()[0].lower()
    ape = apellido.strip().split()[0].lower()
    return f"{nom}.{ape}@terintalia.com"

def render_alta_especialistas(db):
    st.markdown("<h2 style='color: #164032; font-weight: 600; font-size: 26px; margin-bottom: 0px;'>Gestión de Especialistas</h2>", unsafe_allow_html=True)
    st.caption("Añada profesionales de la salud al directorio institucional y genere sus credenciales de acceso.")
    st.write("")

    if 'confirmando' not in st.session_state:
        st.session_state.confirmando = False

    # --- PASO 1: CAPTURA DE DATOS ---
    if not st.session_state.confirmando:
        
        # BLOQUE 1: DATOS PERSONALES Y CONTACTO
        with st.container(border=True):
            st.markdown("<h4 style='color: #164032; font-size: 15px; margin-bottom: 5px;'>👤 Datos Personales y Contacto</h4>", unsafe_allow_html=True)
            
            f1_c1, f1_c2 = st.columns(2)
            with f1_c1: nombre = st.text_input("Nombre(s)").upper()
            with f1_c2: apellido = st.text_input("Apellido(s)").upper()

            f2_c1, f2_c2 = st.columns(2)
            with f2_c1: contacto = st.text_input("Teléfono celular (10 dígitos)", max_chars=10)
            with f2_c2: correo_input = st.text_input("Correo institucional/profesional", placeholder="Si se deja vacío, se autogenerará").lower()

        # BLOQUE 2: FORMACIÓN ACADÉMICA
        with st.container(border=True):
            st.markdown("<h4 style='color: #2980B9; font-size: 15px; margin-bottom: 5px;'>🎓 Formación Académica y Legal</h4>", unsafe_allow_html=True)
            
            f3_c1, f3_c2 = st.columns(2)
            with f3_c1: profesion_base = st.text_input("Profesión base (Ej. Lic. en Psicología)").upper()
            with f3_c2: cedula_base = st.text_input("Cédula profesional base").upper()

            f4_c1, f4_c2 = st.columns(2)
            with f4_c1: posgrado = st.text_input("Especialidad / posgrado habilitante (Opcional)").upper()
            with f4_c2: cedula_posgrado = st.text_input("Cédula de especialidad o posgrado (Opcional)").upper()

        # BLOQUE 3: PERFIL CLÍNICO Y ACCESO
        with st.container(border=True):
            st.markdown("<h4 style='color: #E67E22; font-size: 15px; margin-bottom: 5px;'>🏥 Perfil Clínico y Acceso al Sistema</h4>", unsafe_allow_html=True)
            
            f5_c1, f5_c2 = st.columns(2)
            with f5_c1:
                esp_opcion = st.selectbox("Área de atención dentro de Terintalia", ["Psicología", "Nutrición", "Fisioterapia", "Otra"])
                especialidad_final = esp_opcion.upper()
                if esp_opcion == "Otra":
                    especialidad_manual = st.text_input("Especifique el área de atención").upper()
                    especialidad_final = especialidad_manual
            
            with f5_c2:
                opciones_poblacion = ["Niños", "Adolescentes", "Adultos", "Parejas", "Familias", "Adultos Mayores"]
                poblacion = st.multiselect("Tipo de población que atiende", opciones_poblacion)

            password = st.text_input("Contraseña inicial de acceso", type="password")

        st.write("")
        if st.button("🔍 REVISAR REGISTRO", use_container_width=True):
            # Asignación de correo (Toma el escrito, o genera uno si está vacío)
            correo_final = correo_input if correo_input else generar_correo(nombre, apellido)

            # Validaciones de campos obligatorios
            if especialidad_final == "DIRECTOR":
                st.error("⚠️ 'DIRECTOR' no es una especialidad válida para registro clínico.")
            elif nombre and apellido and profesion_base and cedula_base and contacto and password and poblacion:
                if len(contacto) != 10 or not contacto.isdigit():
                    st.error("⚠️ El teléfono debe contener exactamente 10 dígitos numéricos.")
                else:
                    st.session_state.temp_datos = {
                        "id_doc": obtener_siguiente_id(db),
                        "nombre_completo": f"{nombre} {apellido}".strip(),
                        "profesion_base": profesion_base,
                        "cedula_base": cedula_base,
                        "posgrado": posgrado,
                        "cedula_posgrado": cedula_posgrado,
                        "contacto": contacto,
                        "correo": correo_final,
                        "area_atencion": especialidad_final,
                        "poblacion": poblacion, # Guardado como lista
                        "password": password
                    }
                    st.session_state.confirmando = True
                    st.rerun()
            else:
                st.error("⚠️ Por favor, rellena todos los campos obligatorios (Profesión, Cédula, Población, etc.) para continuar.")

    # --- PASO 2: CONFIRMACIÓN ---
    else:
        datos = st.session_state.temp_datos
        st.info("✨ **Verifique la información antes de generar el expediente del especialista**")
        
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"👤 **Nombre:** {datos['nombre_completo']}")
                st.write(f"🎓 **Profesión Base:** {datos['profesion_base']} (Céd. {datos['cedula_base']})")
                if datos['posgrado']:
                    st.write(f"🏅 **Posgrado:** {datos['posgrado']} (Céd. {datos['cedula_posgrado']})")
                st.write(f"🏥 **Área de Atención:** {datos['area_atencion']}")
                
            with c2:
                st.write(f"👥 **Población:** {', '.join(datos['poblacion'])}")
                st.write(f"📞 **Contacto:** {datos['contacto']}")
                st.write(f"📧 **Correo Asignado:** `{datos['correo']}`")
                st.write(f"🆔 **ID Interno:** `{datos['id_doc']}`")

        st.markdown("<h4 style='color: #164032; font-size: 15px;'>¿Crear Perfil del Especialista?</h4>", unsafe_allow_html=True)
        col_si, col_no = st.columns(2)
        with col_si:
            if st.button("✅ SÍ, GUARDAR Y CREAR ACCESO", type="primary", use_container_width=True):
                # Guardado en Firestore con los nuevos campos
                db.collection("especialistas").document(datos['id_doc']).set({
                    "especialista_id_interno": datos['id_doc'],
                    "nombre_completo": datos['nombre_completo'],
                    "profesion_base": datos['profesion_base'],
                    "cedula_base": datos['cedula_base'],
                    "posgrado": datos['posgrado'],
                    "cedula_posgrado": datos['cedula_posgrado'],
                    "area_atencion": datos['area_atencion'],
                    "especialidad": datos['area_atencion'], # Mantenemos esta llave por retrocompatibilidad con el resto del sistema
                    "poblacion_atiende": datos['poblacion'],
                    "correo_corporativo": datos['correo'],
                    "contacto": datos['contacto'],
                    "telefono": datos['contacto'], # Por retrocompatibilidad
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
