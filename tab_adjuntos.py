import streamlit as st
import os
from datetime import datetime

def render(db, id_pac):
    CARPETA_PACIENTES = "archivos_pacientes"
    if not os.path.exists(CARPETA_PACIENTES):
        os.makedirs(CARPETA_PACIENTES)

    st.markdown("<h4 style='color: #164032; font-size: 16px;'>Expediente Externo (Estudios, Recetas, Derivaciones)</h4>", unsafe_allow_html=True)
    
    with st.form("form_adjunto", clear_on_submit=True):
        archivo = st.file_uploader("Subir Archivo Externo", type=["pdf", "jpg", "png"])
        descripcion = st.text_input("Breve descripción (Ej. Examen de sangre Q.S. 6 elementos)").upper()
        
        if st.form_submit_button("💾 SUBIR ADJUNTO", type="primary", use_container_width=True):
            if archivo and descripcion:
                ruta = os.path.join(CARPETA_PACIENTES, f"{id_pac}_adj_{archivo.name}")
                with open(ruta, "wb") as f:
                    f.write(archivo.getbuffer())
                    
                db.collection("pacientes").document(id_pac).collection("adjuntos").add({
                    "descripcion": descripcion,
                    "archivo": archivo.name,
                    "ruta": ruta,
                    "subido_por": st.session_state.get("nombre", "Especialista"),
                    "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
                st.success("Documento adjunto guardado en el servidor local.")
                st.rerun()
            else:
                st.error("Por favor, suba un archivo y agregue una descripción.")

    st.markdown("---")
    adjuntos = db.collection("pacientes").document(id_pac).collection("adjuntos").order_by("fecha", direction="DESCENDING").get()
    
    if not adjuntos:
        st.info("No hay documentos externos adjuntados.")
    else:
        for adj in adjuntos:
            a = adj.to_dict()
            with st.container(border=True):
                col_i, col_d = st.columns([4, 1])
                with col_i:
                    st.write(f"📎 **{a.get('descripcion', '')}** (`{a.get('archivo', '')}`)")
                    st.caption(f"Subido por: {a.get('subido_por', '')} el {a.get('fecha', '')}")
                with col_d:
                    ruta = a.get('ruta', '')
                    if os.path.exists(ruta):
                        with open(ruta, "rb") as f:
                            st.download_button("⬇️ Abrir", f, file_name=a.get('archivo', ''), key=f"dwn_{adj.id}")
                    else:
                        st.error("Archivo no encontrado.")