import streamlit as st
import base64
from datetime import datetime, timedelta
import time
from firebase_admin import storage

# =========================================================
# MODAL PARA ARCHIVOS NUEVOS (FIREBASE STORAGE / URLs FIRMADAS)
# =========================================================
@st.dialog("Visor de Documentos Clínicos", width="large")
def modal_visualizador_url(url, tipo_archivo, descripcion):
    st.markdown(f"**Documento:** {descripcion}")
    st.markdown("---")
    
    if "image" in tipo_archivo:
        st.image(url, use_container_width=True)
    elif "pdf" in tipo_archivo:
        # TRUCO 1: Usamos HTML puro (st.markdown) en lugar de components.html 
        # Esto evita que Streamlit envuelva el PDF en un sandbox de seguridad extra
        pdf_html = f'''
            <iframe src="{url}" width="100%" height="680px" style="border: none;"></iframe>
        '''
        st.markdown(pdf_html, unsafe_allow_html=True)
    else:
        st.warning("Formato no soportado para previsualización directa.")
    
    if st.button("Cerrar Visor", use_container_width=True):
        st.rerun()

# =========================================================
# MODAL PARA ARCHIVOS VIEJOS (RETROCOMPATIBILIDAD BASE64)
# =========================================================
@st.dialog("Visor de Documentos Clínicos (Legado)", width="large")
def modal_visualizador_b64(datos_b64, tipo_archivo, descripcion):
    st.markdown(f"**Documento:** {descripcion}")
    st.markdown("---")
    
    if "image" in tipo_archivo:
        archivo_bytes = base64.b64decode(datos_b64)
        st.image(archivo_bytes, use_container_width=True)
    elif "pdf" in tipo_archivo:
        pdf_html = f'''
            <iframe src="data:application/pdf;base64,{datos_b64}" width="100%" height="680px" style="border: none;"></iframe>
        '''
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
                    st.error("🚨 ARCHIVO MUY PESADO: El límite actual es de 10 MB. Comprímelo e intenta de nuevo.")
                else:
                    with st.spinner("Subiendo al disco duro de Firebase Storage..."):
                        bucket = storage.bucket()
                        ruta_blob = f"expedientes/{id_pac}/{int(time.time())}_{archivo.name}"
                        blob = bucket.blob(ruta_blob)
                        
                        # Subimos asignando explicitamente que es un PDF/Imagen
                        blob.upload_from_string(archivo.getvalue(), content_type=archivo.type)
                        
                        db.collection("pacientes").document(id_pac).collection("adjuntos").add({
                            "descripcion": descripcion,
                            "archivo": archivo.name,
                            "tipo": archivo.type,
                            "storage_path": ruta_blob,
                            "subido_por": st.session_state.get("nombre", "Especialista"),
                            "fecha": datetime.now().strftime("%d/%m/%Y %H:%M")
                        })
                    
                    st.toast("✅ ¡Documento guardado exitosamente en Cloud Storage!", icon="🎉")
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
                
                # ARCHIVOS EN CLOUD STORAGE (SISTEMA NUEVO)
                if "storage_path" in a:
                    ruta_blob = a.get("storage_path")
                    tipo_archivo = a.get("tipo", "application/pdf")
                    
                    try:
                        bucket = storage.bucket()
                        blob = bucket.blob(ruta_blob)
                        
                        # TRUCO 2: Generamos URL segura con la instrucción de abrir "en linea" (inline)
                        url_segura = blob.generate_signed_url(
                            version="v4", 
                            expiration=timedelta(minutes=60), 
                            method="GET",
                            response_disposition="inline"
                        )
                        
                        with col_vis:
                            if st.button("👁️ Visualizar", key=f"vis_{doc_id}", use_container_width=True):
                                modal_visualizador_url(url_segura, tipo_archivo, a.get("descripcion", ""))
                        
                        with col_desc:
                            enlace_descarga = f'''
                            <a href="{url_segura}" target="_blank" download style="
                                display: block; text-align: center; background-color: #f0f2f6; 
                                padding: 6px; border-radius: 5px; text-decoration: none; 
                                color: black; font-size: 14px; margin-top: 3px;">
                                ⬇️ Descargar
                            </a>
                            '''
                            st.markdown(enlace_descarga, unsafe_allow_html=True)
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
                
                # ARCHIVOS CADUCADOS LOCALES
                else:
                    with col_vis:
                        st.button("👁️ N/A", key=f"vis_err_{doc_id}", disabled=True, use_container_width=True)
                    with col_desc:
                        st.error("Caducado")
