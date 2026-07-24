import streamlit as st
import os
import base64
from datetime import datetime, timedelta
import time
from firebase_admin import storage

# =========================================================
# MODAL PARA ARCHIVOS VIEJOS (RETROCOMPATIBILIDAD BASE64)
# =========================================================
@st.dialog("Visor Legal (Legado)", width="large")
def modal_visualizador_b64(datos_b64, descripcion):
    st.markdown(f"**Documento:** {descripcion}")
    st.markdown("---")
    st.info("💡 Por políticas de Streamlit, si el PDF se ve en gris, ciérralo y usa el botón de descarga.")
    pdf_html = f'<iframe src="data:application/pdf;base64,{datos_b64}" width="100%" height="650px" style="border: none;"></iframe>'
    st.markdown(pdf_html, unsafe_allow_html=True)
    if st.button("Cerrar Visor", use_container_width=True):
        st.rerun()

# =========================================================
# RENDERIZADO PRINCIPAL
# =========================================================
def render(db, paciente, id_pac, rol):
    roles_permitidos = ["ADMINISTRADOR", "ADMIN", "DIRECTOR", "RECEPCIONISTA", "RECEPCIÓN"]
    puede_ver_docs = str(rol).upper() in roles_permitidos
    
    tipo = paciente.get("tipo_terapia", "Individual")
    edad = int(paciente.get("edad", 0))
    es_menor = edad < 18

    # Definición de documentos requeridos según terapia
    docs_requeridos = ["CARATULA DATOS GENERALES", "AVISO DE PRIVACIDAD"]
    if tipo == "De Pareja":
        docs_requeridos.extend(["CONSENTIMIENTO INFORMADO – TERAPIA DE PAREJA", "CONTRATO – TERAPIA DE PAREJA"])
    elif tipo == "Familiar":
        docs_requeridos.extend(["CONSENTIMIENTO INFORMADO GENERAL", "CONTRATO TERAPEÚTICO ADULTOS"])
    else:
        docs_requeridos.append("CONSENTIMIENTO INFORMADO GENERAL")
        if es_menor:
            docs_requeridos.append("CONTRATO TERAPÉUTICO INFANTOJUVENIL")
        else:
            docs_requeridos.append("CONTRATO TERAPEÚTICO ADULTOS")

    # Documentos extra asignados
    asignados_ref = db.collection("pacientes").document(id_pac).collection("docs_asignados_extra").get()
    docs_extra_asignados = [d.id for d in asignados_ref]
    lista_total_docs = docs_requeridos + docs_extra_asignados

    # Documentos que ya se subieron
    docs_cargados_ref = db.collection("pacientes").document(id_pac).collection("documentos_legales").get()
    diccionario_cargados = {doc.id: doc.to_dict() for doc in docs_cargados_ref}

    st.markdown("<h4 style='color: #E67E22; font-size: 15px;'>📋 Documentos Obligatorios del Expediente</h4>", unsafe_allow_html=True)
    
    with st.container(border=True):
        for doc_esperado in lista_total_docs:
            # Ajustamos columnas para acomodar los nuevos botones
            c1, c2, c3, c4 = st.columns([4.5, 2, 2, 1.5])
            
            c1.markdown(f"<p style='margin-bottom: 0px; font-size: 13px; padding-top: 10px;'><b>{doc_esperado}</b></p>", unsafe_allow_html=True)
            
            if doc_esperado in diccionario_cargados:
                datos_doc = diccionario_cargados[doc_esperado]
                c2.markdown(f"<p style='margin-bottom: 0px; color: green; font-size: 12px; padding-top: 10px;'>✅ Firmado</p>", unsafe_allow_html=True)
                
                if puede_ver_docs:
                    # 1. ARCHIVOS EN STORAGE (SISTEMA NUEVO)
                    if "storage_path" in datos_doc:
                        ruta_blob = datos_doc.get("storage_path")
                        try:
                            bucket = storage.bucket()
                            blob = bucket.blob(ruta_blob)
                            url_segura = blob.generate_signed_url(version="v4", expiration=timedelta(minutes=60), method="GET", response_disposition="inline")
                            
                            with c3:
                                st.markdown("<div style='margin-top: 4px;'></div>", unsafe_allow_html=True)
                                btn_pdf = f'''
                                <a href="{url_segura}" target="_blank" style="
                                    display: block; text-align: center; background-color: #FFFFFF; 
                                    padding: 4px 0px; border: 1px solid #94A3B8; border-radius: 6px; 
                                    text-decoration: none; color: #334155; font-size: 12px; font-weight: 600;">
                                    👁️ Abrir PDF
                                </a>
                                '''
                                st.markdown(btn_pdf, unsafe_allow_html=True)
                            
                            with c4:
                                st.markdown("<div style='margin-top: 4px;'></div>", unsafe_allow_html=True)
                                btn_descarga = f'''
                                <a href="{url_segura}" target="_blank" download style="
                                    display: block; text-align: center; background-color: #FFFFFF; 
                                    padding: 4px 0px; border: 1px solid #94A3B8; border-radius: 6px; 
                                    text-decoration: none; color: #334155; font-size: 12px; font-weight: 600;">
                                    ⬇️ Bajar
                                </a>
                                '''
                                st.markdown(btn_descarga, unsafe_allow_html=True)
                        except Exception:
                            c3.error("Error URL")
                            c4.error("N/A")
                            
                    # 2. ARCHIVOS EN BASE64 (SISTEMA VIEJO)
                    elif "archivo_b64" in datos_doc:
                        b64_pdf = datos_doc.get("archivo_b64", "")
                        if b64_pdf:
                            with c3:
                                st.markdown("<div style='margin-top: 4px;'></div>", unsafe_allow_html=True)
                                if st.button("👁️ Ver", key=f"vis_leg_{doc_esperado}", use_container_width=True):
                                    modal_visualizador_b64(b64_pdf, doc_esperado)
                            with c4:
                                st.markdown("<div style='margin-top: 4px;'></div>", unsafe_allow_html=True)
                                pdf_bytes = base64.b64decode(b64_pdf)
                                st.download_button("⬇️ Bajar", data=pdf_bytes, file_name=f"{doc_esperado}_Firmado.pdf", mime="application/pdf", key=f"dl_leg_{doc_esperado}", use_container_width=True)
                else:
                    c3.markdown("<p style='font-size: 14px; padding-top: 10px;'>🔒 Bloqueado</p>", unsafe_allow_html=True)
            
            else:
                c2.markdown("<p style='margin-bottom: 0px; color: #D35400; font-size: 12px; padding-top: 10px;'>⏳ Pendiente</p>", unsafe_allow_html=True)
                
                if puede_ver_docs:
                    # Descarga de plantilla en blanco
                    ruta_plantilla = os.path.join("documentos_legales", f"{doc_esperado}.pdf")
                    with c3:
                        st.markdown("<div style='margin-top: 4px;'></div>", unsafe_allow_html=True)
                        if os.path.exists(ruta_plantilla):
                            with open(ruta_plantilla, "rb") as f:
                                st.download_button("📄 Plantilla", data=f, file_name=f"{doc_esperado}_En_Blanco.pdf", mime="application/pdf", key=f"bl_{doc_esperado}", help="Descargar plantilla en blanco", use_container_width=True)
                        else:
                            st.button("⚠️ Falta PDF", key=f"bl_err_{doc_esperado}", disabled=True, use_container_width=True)

                    # Popover para subir documento firmado
                    with c4:
                        st.markdown("<div style='margin-top: 4px;'></div>", unsafe_allow_html=True)
                        with st.popover("📤 Subir", use_container_width=True):
                            st.caption(f"Subir firmado: **{doc_esperado}**")
                            archivo_subido = st.file_uploader("Seleccionar PDF (Max 10MB)", type=["pdf"], label_visibility="collapsed", key=f"file_{doc_esperado}")
                            
                            if archivo_subido:
                                if st.button("💾 Guardar y Sellar", key=f"btn_{doc_esperado}", type="primary", use_container_width=True):
                                    if archivo_subido.size > 10 * 1024 * 1024:
                                        st.error("🚨 Archivo muy pesado (Max 10MB).")
                                    else:
                                        with st.spinner("Subiendo a Storage..."):
                                            bucket = storage.bucket()
                                            ruta_blob = f"legales/{id_pac}/{int(time.time())}_{doc_esperado}.pdf"
                                            blob = bucket.blob(ruta_blob)
                                            blob.upload_from_string(archivo_subido.getvalue(), content_type=archivo_subido.type)
                                            
                                            db.collection("pacientes").document(id_pac).collection("documentos_legales").document(doc_esperado).set({
                                                "nombre_documento": doc_esperado,
                                                "storage_path": ruta_blob,
                                                "tipo": archivo_subido.type,
                                                "fecha_carga": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                                "cargado_por": st.session_state.get("nombre", "Sistema")
                                            })
                                        st.toast(f"✅ ¡{doc_esperado} guardado exitosamente!")
                                        time.sleep(1)
                                        st.rerun()
                else:
                    c3.markdown("<p style='font-size: 12px; color: gray; padding-top: 10px;'>Falta firma</p>", unsafe_allow_html=True)
            
            st.markdown("<hr style='margin: 4px 0px; border-top: 1px solid #eee;'>", unsafe_allow_html=True)

    # --- SECCIÓN: FORMATOS ADICIONALES ---
    st.write("")
    if puede_ver_docs:
        st.markdown("<h4 style='color: #2980B9; font-size: 15px;'>➕ Asignar Formato Adicional del Repositorio</h4>", unsafe_allow_html=True)
        repo_docs = []
        if os.path.exists("documentos_legales"):
            repo_docs = [f.replace(".pdf", "") for f in os.listdir("documentos_legales") if f.endswith(".pdf")]
        
        opciones_disponibles = [d for d in repo_docs if d not in lista_total_docs]
        
        if opciones_disponibles:
            with st.container(border=True):
                col_sel, col_btn = st.columns([3, 1])
                doc_sel = col_sel.selectbox("Seleccionar plantilla:", ["-- Elegir documento --"] + opciones_disponibles, label_visibility="collapsed")
                
                if col_btn.button("Añadir al Checklist", use_container_width=True):
                    if doc_sel != "-- Elegir documento --":
                        db.collection("pacientes").document(id_pac).collection("docs_asignados_extra").document(doc_sel).set({
                            "asignado_el": datetime.now().strftime("%d/%m/%Y %H:%M"),
                            "asignado_por": st.session_state.get("nombre", "Sistema")
                        })
                        st.rerun()
        else:
            st.info("Todos los documentos de tu carpeta ya están asignados a este paciente.")
