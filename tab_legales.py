import streamlit as st
import os
import base64
from datetime import datetime

def render(db, paciente, id_pac, rol):
    roles_permitidos = ["ADMINISTRADOR", "ADMIN", "DIRECTOR", "RECEPCIONISTA", "RECEPCIÓN"]
    puede_ver_docs = str(rol).upper() in roles_permitidos
    
    tipo = paciente.get("tipo_terapia", "Individual")
    edad = int(paciente.get("edad", 0))
    es_menor = edad < 18

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

    asignados_ref = db.collection("pacientes").document(id_pac).collection("docs_asignados_extra").get()
    docs_extra_asignados = [d.id for d in asignados_ref]
    lista_total_docs = docs_requeridos + docs_extra_asignados

    docs_cargados_ref = db.collection("pacientes").document(id_pac).collection("documentos_legales").get()
    diccionario_cargados = {doc.id: doc.to_dict() for doc in docs_cargados_ref}

    st.markdown("<h4 style='color: #E67E22; font-size: 15px;'>📋 Documentos Obligatorios del Expediente</h4>", unsafe_allow_html=True)
    
    with st.container(border=True):
        for doc_esperado in lista_total_docs:
            c1, c2, c3, c4 = st.columns([6, 2, 1, 1])
            c1.markdown(f"<p style='margin-bottom: 0px; font-size: 13px; padding-top: 5px;'><b>{doc_esperado}</b></p>", unsafe_allow_html=True)
            
            if doc_esperado in diccionario_cargados:
                datos_doc = diccionario_cargados[doc_esperado]
                c2.markdown(f"<p style='margin-bottom: 0px; color: green; font-size: 12px; padding-top: 5px;'>✅ Firmado</p>", unsafe_allow_html=True)
                
                if puede_ver_docs:
                    b64_pdf = datos_doc.get("archivo_b64", "")
                    if b64_pdf:
                        pdf_bytes = base64.b64decode(b64_pdf)
                        c3.download_button("📥", data=pdf_bytes, file_name=f"{doc_esperado}_Firmado.pdf", mime="application/pdf", key=f"dl_{doc_esperado}", help="Descargar PDF Firmado", use_container_width=True)
                else:
                    c3.markdown("<p style='font-size: 14px; padding-top: 5px;'>🔒</p>", unsafe_allow_html=True)
            else:
                c2.markdown("<p style='margin-bottom: 0px; color: #D35400; font-size: 12px; padding-top: 5px;'>⏳ Pendiente</p>", unsafe_allow_html=True)
                
                if puede_ver_docs:
                    ruta_plantilla = os.path.join("documentos_legales", f"{doc_esperado}.pdf")
                    if os.path.exists(ruta_plantilla):
                        with open(ruta_plantilla, "rb") as f:
                            c3.download_button("📄", data=f, file_name=f"{doc_esperado}_En_Blanco.pdf", mime="application/pdf", key=f"bl_{doc_esperado}", help="Descargar plantilla en blanco", use_container_width=True)
                    else:
                        c3.button("⚠️", key=f"bl_err_{doc_esperado}", help="Falta el archivo", disabled=True, use_container_width=True)

                    with c4.popover("📤", use_container_width=True):
                        st.caption(f"Subir firmado: **{doc_esperado}**")
                        archivo_subido = st.file_uploader("Seleccionar PDF", type=["pdf"], label_visibility="collapsed", key=f"file_{doc_esperado}")
                        if archivo_subido:
                            if st.button("💾 Guardar", key=f"btn_{doc_esperado}", type="primary", use_container_width=True):
                                pdf_b64 = base64.b64encode(archivo_subido.read()).decode('utf-8')
                                db.collection("pacientes").document(id_pac).collection("documentos_legales").document(doc_esperado).set({
                                    "nombre_documento": doc_esperado,
                                    "archivo_b64": pdf_b64,
                                    "fecha_carga": datetime.now().strftime("%d/%m/%Y %H:%M"),
                                    "cargado_por": st.session_state.get("nombre", "Sistema")
                                })
                                st.rerun()
                else:
                    c3.markdown("<p style='font-size: 12px; color: gray; padding-top: 5px;'>Falta firma</p>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 4px 0px; border-top: 1px solid #eee;'>", unsafe_allow_html=True)

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