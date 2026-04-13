import streamlit as st
import os
from google.cloud import firestore

# Importamos las pestañas que crearemos en el paso 3
import tab_legales
import tab_historia
import tab_notas
import tab_evaluaciones
import tab_adjuntos

def render_expedientes(db, rol, user_id):
    st.markdown("<h2 style='color: #164032; font-weight: 600; font-size: 26px; margin-bottom: 0px;'>📂 Expediente Clínico Digital</h2>", unsafe_allow_html=True)
    st.write("")
    
    # ==========================================
    # 1. SELECCIÓN DE PACIENTE
    # ==========================================
    docs_pacientes = db.collection("pacientes").where("status", "==", "ACTIVO").get()
    lista_pacientes = []
    
    for doc in docs_pacientes:
        p = doc.to_dict()
        if rol == "ESPECIALISTA":
            if user_id in p.get("med", ""):
                lista_pacientes.append(p)
        else:
            lista_pacientes.append(p)

    if not lista_pacientes:
        st.warning("⚠️ No hay expedientes activos disponibles para tu perfil.")
        return

    nombres_pac = {f"{p['nombre']} (Folio: {p['id_p']})": p for p in lista_pacientes}
    
    pac_sel = st.selectbox("🔍 Buscar y Seleccionar Expediente:", ["-- Seleccione un expediente --"] + list(nombres_pac.keys()), key="memoria_paciente")

    if pac_sel == "-- Seleccione un expediente --":
        st.info("Seleccione un paciente en el buscador superior para abrir su archivero clínico.")
        return
        
    paciente = nombres_pac[pac_sel]
    id_pac = paciente['id_p']
    
    # ==========================================
    # CINTILLA DE PERFIL MINIMALISTA
    # ==========================================
    with st.container(border=True):
        st.markdown(f"<div style='font-size: 15px;'><b style='color: #164032; font-size: 18px;'>{paciente['nombre']}</b> &nbsp;&nbsp;|&nbsp;&nbsp; Folio: <span style='color: #E67E22; font-weight: bold;'>{id_pac}</span></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size: 14px; color: #555; margin-top: 4px;'><b>Edad:</b> {paciente.get('edad', 'N/A')} años &nbsp;&nbsp;|&nbsp;&nbsp; <b>Servicio:</b> {paciente.get('tipo_terapia', 'N/A')} ({paciente.get('modalidad', 'N/A')}) &nbsp;&nbsp;|&nbsp;&nbsp; <b>Especialista:</b> {paciente.get('med', 'N/A')}</div>", unsafe_allow_html=True)

    st.write("")

    # ==========================================
    # NAVEGACIÓN POR PESTAÑAS (TABS)
    # ==========================================
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "⚖️ Consentimientos", 
        "🏥 Historia Clínica", 
        "✍️ Notas de Evolución", 
        "📊 Evaluaciones", 
        "📎 Adjuntos"
    ])

    # Le pasamos el control a cada archivo
    with tab1: tab_legales.render(db, paciente, id_pac, rol)
    with tab2: tab_historia.render(db, paciente, id_pac)
    with tab3: tab_notas.render(db, id_pac)
    with tab4: tab_evaluaciones.render(db, id_pac)
    with tab5: tab_adjuntos.render(db, id_pac)