import streamlit as st
import os

CARPETA_REPO = "repositorio_archivos"

def render_repositorio(rol):
    # CSS AVANZADO: Aislando los estilos para no romper el cargador de archivos
    st.markdown("""
        <style>
        /* --- 1. RESCATE DEL FILE UPLOADER (Browse Files) --- */
        [data-testid="stFileUploaderDropzone"] button {
            width: auto !important;
            height: auto !important;
            min-height: 32px !important;
            padding: 4px 16px !important;
            border-radius: 8px !important;
            background-color: #FFFFFF !important;
            color: #4E342E !important;
            border: 1px solid #D1D5DB !important;
            font-size: 14px !important;
            display: inline-flex !important;
            margin-top: 10px !important;
        }
        [data-testid="stFileUploaderDropzone"] button:hover {
            border-color: #E67E22 !important;
            color: #E67E22 !important;
        }

        /* --- 2. MICRO-BOTONES (Solo aplican dentro de las columnas de la lista) --- */
        /* Botón DOWNLOAD (Azul) */
        [data-testid="column"] div[data-testid="stDownloadButton"] button {
            background-color: #E1F5FE !important; 
            border: 1px solid #81D4FA !important; 
            border-radius: 6px !important;
            padding: 0px !important;
            width: 26px !important; 
            height: 26px !important; 
            min-height: 26px !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            margin-top: 4px !important;
        }
        [data-testid="column"] div[data-testid="stDownloadButton"] button p {
            font-size: 13px !important;
            margin: 0 !important;
            line-height: 1 !important;
        }
        [data-testid="column"] div[data-testid="stDownloadButton"] button:hover {
            background-color: #B3E5FC !important;
        }

        /* Botón DELETE (Rojo - Activa el Popover) */
        [data-testid="column"] button[kind="secondary"] {
            background-color: #FFEBEE !important; 
            border: 1px solid #EF9A9A !important;
            border-radius: 6px !important;
            padding: 0px !important;
            width: 26px !important;
            height: 26px !important;
            min-height: 26px !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            margin-top: 4px !important;
        }
        [data-testid="column"] button[kind="secondary"] p {
            font-size: 13px !important;
            margin: 0 !important;
            line-height: 1 !important;
        }
        [data-testid="column"] button[kind="secondary"]:hover {
            background-color: #FFCDD2 !important;
        }

        /* --- 3. DISEÑO DEL BOTÓN DE CONFIRMACIÓN (Dentro del Popover) --- */
        div[data-testid="stPopoverBody"] button {
            width: 100% !important;
            height: auto !important;
            padding: 8px !important;
            background-color: #D32F2F !important; /* Rojo Alerta */
            color: white !important;
            border-radius: 8px !important;
            font-size: 14px !important;
            border: none !important;
        }
        div[data-testid="stPopoverBody"] button p {
            color: white !important;
            font-size: 14px !important;
        }

        /* --- 4. AJUSTE DE FILAS Y TEXTO --- */
        div[data-testid="stHorizontalBlock"] {
            align-items: center !important;
            padding-bottom: 0px !important;
            margin-bottom: -18px !important; 
        }
        .texto-archivo {
            font-size: 13px !important;
            font-weight: 500 !important;
            color: #4E342E;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis; 
            padding-top: 8px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("### 📁 Repositorio Institucional")

    if not os.path.exists(CARPETA_REPO):
        os.makedirs(CARPETA_REPO)

    # ==========================================
    # 1. ZONA DE CARGA
    # ==========================================
    if rol in ["DIRECTOR", "RECEPCIONISTA"]:
        with st.expander("📤 Cargar Nuevo Documento Oficial", expanded=False):
            # Ahora el botón "Browse files" se verá normal y estético
            archivo_subido = st.file_uploader("Formatos permitidos: Word, PDF, Excel", type=["pdf", "doc", "docx", "xls", "xlsx"], label_visibility="collapsed")
            if archivo_subido is not None:
                if st.button("💾 Guardar Formato", type="primary", use_container_width=True, key="btn_guardar_repo"): 
                    ruta = os.path.join(CARPETA_REPO, archivo_subido.name)
                    with open(ruta, "wb") as f:
                        f.write(archivo_subido.getbuffer())
                    st.success("Guardado exitosamente.")
                    st.rerun()

    st.markdown("#### 📥 Documentos Clínicos")
    busqueda = st.text_input("🔍 Buscar documento...", placeholder="Escribe el nombre del archivo...")
    st.write("") 

    # ==========================================
    # 2. LISTA COMPACTA DE DESCARGA Y ELIMINACIÓN
    # ==========================================
    archivos = sorted(os.listdir(CARPETA_REPO))
    
    if busqueda:
        archivos = [f for f in archivos if busqueda.lower() in f.lower()]

    if len(archivos) == 0:
        if busqueda:
            st.caption("No se encontraron documentos con ese nombre.")
        else:
            st.caption("No hay documentos en el servidor.")
    else:
        c_tit1, c_tit2, c_tit3 = st.columns([8.5, 0.75, 0.75])
        c_tit1.caption("**Nombre del Formato**")
        st.markdown("<hr style='margin: 0px; padding: 0px; border-top: 1px solid #E5E7EB;'>", unsafe_allow_html=True)
        
        for archivo in archivos:
            ruta_archivo = os.path.join(CARPETA_REPO, archivo)
            
            icono = "📄"
            if archivo.endswith(".pdf"): icono = "📕"
            elif archivo.endswith((".docx", ".doc")): icono = "📘"
            elif archivo.endswith((".xlsx", ".xls")): icono = "📗"
            
            c1, c2, c3 = st.columns([8.5, 0.75, 0.75])
            
            with c1:
                st.markdown(f"<div class='texto-archivo'>{icono} {archivo}</div>", unsafe_allow_html=True)
                
            with c2:
                with open(ruta_archivo, "rb") as f:
                    st.download_button("📥", data=f, file_name=archivo, key=f"dwn_{archivo}")
            
            with c3:
                if rol == "DIRECTOR":
                    # EL SEGURO DE VIDA: st.popover crea un menú flotante al hacer clic
                    with st.popover("🗑️"):
                        st.markdown("**⚠️ ¿Eliminar archivo?**")
                        st.caption(f"Se borrará: `{archivo}`")
                        
                        # Si presionan este botón dentro del menú, ahora sí se borra
                        if st.button("Sí, eliminar definitivamente", key=f"conf_{archivo}"):
                            os.remove(ruta_archivo)
                            st.rerun()