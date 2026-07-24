import streamlit as st
import base64
from datetime import datetime, timedelta
import time
from firebase_admin import storage

# =========================================================
# MODAL SOLO PARA IMÁGENES (FIREBASE STORAGE)
# =========================================================
@st.dialog("Visor de Documentos Clínicos", width="large")
def modal_visualizador_url(url, tipo_archivo, descripcion):
    st.markdown(f"**Documento:** {descripcion}")
    st.markdown("---")
    st.image(url, use_container_width=True)
    if st.button("Cerrar Visor", use_container_width=True):
        st.rerun()

# =========================================================
# MODAL PARA ARCHIVOS VIEJOS (RETROCOMPATIBILIDAD BASE64)
# =========================================================
@st.dialog("Visor de Documentos (Legado)", width="large")
def modal_visualizador_b64(datos_b64, tipo_archivo, descripcion):
    st.markdown(f"**Documento:** {descripcion}")
    st.markdown("---")
    
    if "image" in tipo_archivo:
        archivo_bytes = base64.b64decode(datos_b64)
        st.image(archivo_bytes, use_container_width=True)
    elif "pdf" in tipo_archivo:
        st.info("💡 Por bloqueos de Streamlit Cloud, si el PDF se ve en gris, ciérralo y usa el botón '⬇️ Descargar'.")
        pdf_html = f'<iframe src="data:application/pdf;base64,{datos_b64}" width="100%" height="650px" style="border: none;"></iframe>'
        st.markdown(pdf_html, unsafe_allow_html=True)
    
    if st.button("Cerrar Visor", use_container_width=True):
        st.rerun()

# =========================================================
# RENDERIZADO PRINCIPAL
# =========================================================
def render(db, id_pac):
    st.markdown("<h4 style='color: #164032; font-size: 16px;'>Expediente Externo (Estudios, Recetas, Derivaciones)</h4>", unsafe_allow_html=True)
    
    with st.form("form_adjunto", clear_on_submit=True):
        archivo = st.file_uploader("📎 Subir Archivo (Límite: 10 MB)", type=["pdf", "jpg", "jpeg", "png"])
        descripcion = st.text_input("Breve descripción (Ej. Examen de sangre Q.S. 6 elementos)").upper()
        
        if st.form_submit_button("💾 SUBIR ADJUNTO", type="primary", use_container_width=True):
            if archivo and descripcion:
                if archivo.size > 10 * 1024 * 1024:
                    st.error("🚨 ARCHIVO MUY PESADO: El límite actual es de 10 MB.")
                else:
                    with st.spinner("Subiendo al disco duro de Firebase Storage..."):
                        bucket = storage.bucket()
                        ruta_blob = f"expedientes/{id_pac}/{int(time.time())}_{archivo.name}"
                        blob = bucket.blob(ruta_blob)
                        blob.upload_from_string(archivo.getvalue(), content_type=archivo.type)
                        
                        db.collection("pacientes").document(id_pac).collection("adjuntos").add({
                            "descripcion": descripcion,
                            "archivo": archivo.name,
                            "tipo": archivo.type,
                            "storage_path": ruta_blob,
                            "subido_por": st.session_state.get("nombre", "Especialista"),
                            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
                        })
                    
                    st.toast("✅ ¡Documento guardado exitosamente!", icon="🎉")
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
                
                # ARCHIVOS EN CLOUD STORAGE (NUEVOS)
                if "storage_path" in a:
                    ruta_blob = a.get("storage_path")
                    tipo_archivo = a.get("tipo", "application/pdf")
                    
                    try:
                        bucket = storage.bucket()
                        blob = bucket.blob(ruta_blob)
                        url_segura = blob.generate_signed_url(version="v4", expiration=timedelta(minutes=60), method="GET", response_disposition="inline")
                        
                        # --- COLUMNA DE VISUALIZACIÓN ---
                        with col_vis:
                            if "pdf" in tipo_archivo:
                                # HTML Link para saltar el bloqueo de Streamlit en PDFs
                                btn_pdf = f'''
                                <a href="{url_segura}" target="_blank" style="
                                    display: block; text-align: center; background-color: #FFFFFF; 
                                    padding: 6px 0px; border: 1px solid #94A3B8; border-radius: 8px; 
                                    text-decoration: none; color: #334155; font-size: 14px; font-weight: 600;">
                                    👁️ Abrir PDF
                                </a>
                                '''
                                st.markdown(btn_pdf, unsafe_allow_html=True)
                            else:
                                # Botón normal de Streamlit para imágenes (abre Modal)
                                if st.button("👁️ Visualizar", key=f"vis_{doc_id}", use_container_width=True):
                                    modal_visualizador_url(url_segura, tipo_archivo, a.get("descripcion", ""))
                        
                        # --- COLUMNA DE DESCARGA ---
                        with col_desc:
                            # Botón HTML para descargar directamente desde Firebase
                            btn_descarga = f'''
                            <a href="{url_segura}" target="_blank" download style="
                                display: block; text-align: center; background-color: #FFFFFF; 
                                padding: 6px 0px; border: 1px solid #94A3B8; border-radius: 8px; 
                                text-decoration: none; color: #334155; font-size: 14px; font-weight: 600;">
                                ⬇️ Descargar
                            </a>
                            '''
                            st.markdown(btn_descarga, unsafe_allow_html=True)
                            
                    except Exception as e:
                        with col_vis:
                            st.error("Error URL")
                        with col_desc:
                            st.error("No disponible")
                
                # ARCHIVOS VIEJOS (BASE64)
                elif "datos_b64" in a:
                    datos_b64 = a.get("datos_b64")
                    tipo_archivo = a.get("tipo", "application/pdf")
                    
                    with col_vis:
                        if st.button("👁️ Visualizar", key=f"vis_b64_{doc_id}", use_container_width=True):
                            modal_visualizador_b64(datos_b64, tipo_archivo, a.get("descripcion", ""))
                    
                    with col_desc:
                        archivo_bytes = base64.b64decode(datos_b64)
                        st.download_button("⬇️ Descargar", data=archivo_bytes, file_name=a.get('archivo', 'adjunto'), mime=tipo_archivo, key=f"dwn_b64_{doc_id}", use_container_width=True)
                
                else:
                    with col_vis:
                        st.button("👁️ N/A", key=f"vis_err_{doc_id}", disabled=True, use_container_width=True)
                    with col_desc:
                        st.error("Caducado")
