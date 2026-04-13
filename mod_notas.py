import streamlit as st
from datetime import datetime
from google.cloud import firestore

def render_notas(db, rol, user_id):
    st.header("📝 NOTAS DE EVOLUCIÓN CLÍNICA")

    # 1. FILTRADO DE PACIENTES POR ROL
    if rol == "ESPECIALISTA":
        # Solo pacientes que tengan su ID en el campo 'med'
        pacientes_ref = db.collection("pacientes").where("med", "array_contains", user_id if "(" not in user_id else user_id).get()
        # Nota: Ajustamos la consulta dependiendo de cómo guardamos el string del médico
        query = db.collection("pacientes").get() 
        lista_p = [d.to_dict() for d in query if user_id in d.to_dict().get('med', '')]
    else:
        # El Director ve a todos
        query = db.collection("pacientes").get()
        lista_p = [d.to_dict() for d in query]

    if not lista_p:
        st.warning("No tienes pacientes asignados actualmente.")
        return

    # 2. SELECCIÓN DE PACIENTE
    nombres_p = {p['nombre']: p['id_p'] for p in lista_p}
    paciente_sel = st.selectbox("SELECCIONE PACIENTE:", list(nombres_p.keys()))
    id_p_actual = nombres_p[paciente_sel]

    st.divider()

    # 3. HISTORIAL DE SESIONES (Lectura)
    st.subheader(f"Historial de Sesiones - {id_p_actual}")
    notas_ref = db.collection("pacientes").document(id_p_actual).collection("notas_clinicas").order_by("num_sesion", direction=firestore.Query.DESCENDING).get()
    
    num_ultima_sesion = 0
    if notas_ref:
        for nota_doc in notas_ref:
            n = nota_doc.to_dict()
            with st.expander(f"SESIÓN #{n['num_sesion']} - {n['fecha']}"):
                st.write(n['contenido'])
                st.caption(f"Registrada por: {n['especialista']} | Estado: {n['estado']}")
            if n['num_sesion'] > num_ultima_sesion:
                num_ultima_sesion = n['num_sesion']
    else:
        st.info("No hay notas previas para este paciente.")

    st.divider()

    # 4. NUEVA NOTA (Escritura)
    if rol in ["DIRECTOR", "ESPECIALISTA"]:
        st.subheader(f"Nueva Nota: Sesión #{num_ultima_sesion + 1}")
        
        with st.form("nueva_nota_form", clear_on_submit=True):
            contenido = st.text_area("DESCRIPCIÓN DE LA SESIÓN", height=200, placeholder="Escriba aquí los avances y observaciones...")
            confirmar = st.checkbox("CERRAR SESIÓN (Una vez guardada, no podrá editarse)")
            
            btn_guardar = st.form_submit_button("💾 GUARDAR Y FIRMAR NOTA")

        if btn_guardar:
            if contenido and confirmar:
                nueva_nota = {
                    "num_sesion": num_ultima_sesion + 1,
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "contenido": contenido.upper(),
                    "especialista": user_id,
                    "estado": "CERRADA",
                    "timestamp": firestore.SERVER_TIMESTAMP
                }
                # Guardamos como sub-colección del paciente para que todo esté ordenado
                db.collection("pacientes").document(id_p_actual).collection("notas_clinicas").add(nueva_nota)
                st.success("Nota guardada e inmunizada correctamente.")
                st.rerun()
            elif not confirmar:
                st.error("Debe marcar la casilla de 'CERRAR SESIÓN' para finalizar.")
            else:
                st.error("La nota no puede estar vacía.")