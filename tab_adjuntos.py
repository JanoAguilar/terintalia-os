import streamlit as st
import base64
from datetime import datetime
# Hemos eliminado 'os' porque ya no guardaremos nada en carpetas locales, todo irá seguro a la nube.

def render(db, id_pac):
    st.markdown("<h4 style='color: #164032; font-size: 16px;'>Expediente Externo (Estudios, Recetas, Derivaciones)</h4>", unsafe_allow_html=True)
    
    with st.form("form_adjunto", clear_on_submit=True):
        # Nota de auditor: Se recomienda 1MB máximo porque es el límite de los documentos en Firestore.
        archivo = st.file_uploader("Subir Archivo Externo (Recomendado: Archivos ligeros / Máx 1MB)", type=["pdf", "jpg", "jpeg", "png"])
        descripcion = st.text_input("Breve descripción (Ej. Examen de sangre Q.S. 6 elementos)").upper()
        
        if st.form_submit_button("💾 SUBIR ADJUNTO", type="primary", use_container_width=True):
            if archivo and descripcion:
                # 1. Transformamos el archivo a código Base64 para hacerlo inmortal en la base de datos
                archivo_bytes = archivo.getvalue()
                archivo_b64 = base64.b64encode(archivo_bytes).decode('utf-8')
                tipo_archivo = archivo.type # Identifica automáticamente si es PDF o Imagen
                
                try:
                    # 2. Guardamos el archivo directamente en Firebase
                    db.collection("pacientes").document(id_pac).collection("adjuntos").add({
                        "descripcion": descripcion,
                        "archivo": archivo.name,
                        "tipo": tipo_archivo,
                        "datos_b64": archivo_b64,
                        "subido_por": st.session_state.get("nombre", "Especialista"),
                        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
                    st.success("Documento adjunto guardado permanentemente en la nube.")
                    st.rerun()
                except Exception as e:
                    # Si suben una radiografía de 10MB, Firebase lo frenará. 
                    st.error("🚨 Error al subir: El archivo es demasiado pesado. Comprímalo para que pese menos de 1 MB.")
            else:
                st.error("Por favor, suba un archivo y agregue una descripción.")

    st.markdown("---")
    adjuntos = db.collection("pacientes").document(id_pac).collection("adjuntos").order_by("fecha", direction="DESCENDING").get()
    
    if not adjuntos:
        st.info("No hay documentos externos adjuntados.")
    else:
        for adj in adjuntos:
            a = adj.to_dict()
            doc_id = adj.id
            
            with st.container(border=True):
                # Usamos 3 columnas: Información | Botón Visualizar | Botón Descargar
                col_info, col_vis, col_desc = st.columns([3, 1, 1])
                with col_info:
                    st.write(f"📎 **{a.get('descripcion', 'Documento sin título')}**")
                    st.caption(f"`{a.get('archivo', 'Desconocido')}` | Por: {a.get('subido_por', '')} el {a.get('fecha', '')}")
                
                # Verificamos si el archivo se guardó con el nuevo método inmortal (Base64)
                if "datos_b64" in a:
                    datos_b64 = a.get("datos_b64")
                    tipo_archivo = a.get("tipo", "application/pdf")
                    archivo_bytes = base64.b64decode(datos_b64)
                    
                    # --- BOTÓN DE VISUALIZACIÓN FLOTANTE ---
                    with col_vis:
                        with st.popover("👁️ Visualizar", use_container_width=True):
                            if "image" in tipo_archivo:
                                st.image(archivo_bytes, caption=a.get('descripcion', ''))
                            elif "pdf" in tipo_archivo:
                                # Visor nativo de PDF incrustado en HTML
                                pdf_display = f'<iframe src="data:application/pdf;base64,{datos_b64}" width="100%" height="450" type="application/pdf"></iframe>'
                                st.markdown(pdf_display, unsafe_allow_html=True)
                            else:
                                st.warning("Formato no soportado para previsualización directa.")
                    
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
                    # Manejo de errores para los archivos "fantasma" que intentaste subir ayer
                    with col_vis:
                        st.button("👁️ N/A", key=f"vis_err_{doc_id}", disabled=True, use_container_width=True)
                    with col_desc:
                        st.error("Archivo local caducado")
