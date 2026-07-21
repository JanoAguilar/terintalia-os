import streamlit as st
import base64
from datetime import datetime
import time

# =========================================================
# FUNCIÓN MODAL PARA VISUALIZACIÓN EN PANTALLA COMPLETA
# =========================================================
@st.dialog("Visualizador de Documentos Clínicos", width="large")
def modal_visualizador(datos_b64, tipo_archivo, descripcion):
    st.markdown(f"**Documento:** {descripcion}")
    st.markdown("---")
    
    if "image" in tipo_archivo:
        # Extrae la imagen y la ajusta al ancho completo de la ventana
        archivo_bytes = base64.b64decode(datos_b64)
        st.image(archivo_bytes, use_container_width=True)
    elif "pdf" in tipo_archivo:
        # Usamos <embed> que es más resistente a los bloqueos de navegador que el <iframe>
        pdf_display = f'<embed type="application/pdf" src="data:application/pdf;base64,{datos_b64}" width="100%" height="700">'
        st.markdown(pdf_display, unsafe_allow_html=True)
    else:
        st.warning("Formato no soportado para previsualización directa.")
    
    if st.button("Cerrar Visor", use_container_width=True):
        st.rerun()

# =========================================================
# RENDERIZADO PRINCIPAL
# =========================================================
def render(db, id_pac):
    st.markdown("<h4 style='color: #164032; font-size: 16px;'>Expediente Externo (Estudios, Recetas, Derivaciones)</h4>", unsafe_allow_html=True)
    
    with st.form("form_adjunto", clear_on_submit=True):
        # Aclaramos el límite real en el título para que ignoren el 200MB de Streamlit
        archivo = st.file_uploader("📎 Subir Archivo (IGNORA AVISO DE 200MB -> TU LÍMITE REAL ES DE 1 MB)", type=["pdf", "jpg", "jpeg", "png"])
        descripcion = st.text_input("Breve descripción (Ej. Examen de sangre Q.S. 6 elementos)").upper()
        
        if st.form_submit_button("💾 SUBIR ADJUNTO", type="primary", use_container_width=True):
            if archivo and descripcion:
                # CANDADO ESTRICTO DE 1 MEGABYTE (1 MB = 1,048,576 bytes)
                if archivo.size > 1048576:
                    st.error("🚨 ARCHIVO DEMASIADO PESADO: Tu documento supera el límite de 1 MB. Por favor, comprímelo o bájale la resolución antes de subirlo.")
                else:
                    # ANIMACIÓN DE CARGA PARA EL USUARIO
                    with st.spinner("Cifrando y guardando en la nube..."):
                        archivo_bytes = archivo.getvalue()
                        archivo_b64 = base64.b64encode(archivo_bytes).decode('utf-8')
                        tipo_archivo = archivo.type
                        
                        db.collection("pacientes").document(id_pac).collection("adjuntos").add({
                            "descripcion": descripcion,
                            "archivo": archivo.name,
                            "tipo": tipo_archivo,
                            "datos_b64": archivo_b64,
                            "subido_por": st.session_state.get("nombre", "Especialista"),
                            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
                        })
                    
                    # MENSAJE FLOTANTE Y PAUSA PARA QUE SE LOGRE LEER
                    st.toast("✅ ¡Documento guardado exitosamente en el expediente!", icon="🎉")
                    time.sleep(1.5)
                    st.rerun()
            else:
                st.error("⚠️ Por favor, suba un archivo y agregue una descripción.")

    st.markdown("---")
    adjuntos = db.collection("pacientes").document(id_pac).collection("adjuntos").order_by("fecha", direction="DESCENDING").get()
    
    if not adjuntos:
        st.info("No hay documentos externos adjuntados.")
    else:
        for adj in adjuntos:
            a = adj.to_dict()
            doc_id = adj.id
            
            with st.container(border=True):
                col_info, col_vis, col_desc = st.columns([3, 1, 1])
                with col_info:
                    st.write(f"📎 **{a.get('descripcion', 'Documento sin título')}**")
                    st.caption(f"`{a.get('archivo', 'Desconocido')}` | Por: {a.get('subido_por', '')} el {a.get('fecha', '')}")
                
                if "datos_b64" in a:
                    datos_b64 = a.get("datos_b64")
                    tipo_archivo = a.get("tipo", "application/pdf")
                    archivo_bytes = base64.b64decode(datos_b64)
                    
                    # --- BOTÓN QUE DISPARA LA VENTANA GIGANTE (MODAL) ---
                    with col_vis:
                        if st.button("👁️ Visualizar", key=f"vis_{doc_id}", use_container_width=True):
                            modal_visualizador(datos_b64, tipo_archivo, a.get("descripcion", ""))
                    
                    # --- BOTÓN DE DESCARGA NATIVO ---
                    with col_desc:
                        st.download_button(
                            label="⬇️ Descargar",
                            data=archivo_bytes,
                            file_name=a.get('archivo', 'adjunto_clinico'),
                            mime=tipo_archivo,
                            key=f"dwn_{doc_id}",
                            use_container_width=True
                        )
                else:
                    with col_vis:
                        st.button("👁️ N/A", key=f"vis_err_{doc_id}", disabled=True, use_container_width=True)
                    with col_desc:
                        st.error("Archivo caducado")
