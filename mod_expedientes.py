import streamlit as st
import os
from google.cloud import firestore

import tab_legales
import tab_historia
import tab_notas
import tab_evaluaciones
import tab_adjuntos

def render_expedientes(db, rol, user_id):
    # Encabezado moderno del módulo
    st.markdown("""
        <div style="margin-bottom: 18px;">
            <span style="background: #ECFDF5; color: #059669; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 999px; letter-spacing: 0.6px; text-transform: uppercase;">Módulo Central</span>
            <h2 style="color: #0F172A; font-weight: 800; font-size: 26px; margin: 6px 0 2px 0;">📂 Expediente Clínico Digital</h2>
            <p style="color: #64748B; font-size: 13.5px; margin: 0;">Consulta, documentación y sellado legal de sesiones terapéuticas y clínicas.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # ==========================================
    # 1. OBTENER PACIENTES SEGÚN ROL
    # ==========================================
    docs_pacientes = db.collection("pacientes").where("status", "==", "ACTIVO").get()
    lista_pacientes_cruda = []
    
    es_admin_o_asistente = rol in ["DIRECTOR", "RECEPCIONISTA", "ASISTENTE CLÍNICO"]
    
    for doc in docs_pacientes:
        p = doc.to_dict()
        if es_admin_o_asistente:
            lista_pacientes_cruda.append(p)
        else:
            if user_id in p.get("med", ""):
                lista_pacientes_cruda.append(p)

    if not lista_pacientes_cruda:
        st.warning("⚠️ No hay expedientes activos disponibles para tu perfil.")
        return

    # ==========================================
    # 2. RENDERIZADO DEL BUSCADOR Y FILTRO
    # ==========================================
    with st.container(border=True):
        if es_admin_o_asistente:
            c_filtro, c_busca = st.columns([1, 2])
            especialidades = sorted(list(set([p.get("esp", "Sin Especialidad") for p in lista_pacientes_cruda])))
            
            with c_filtro:
                filtro_esp = st.selectbox("🎯 Filtrar por Especialidad:", ["Todas las Especialidades"] + especialidades)
                
            if filtro_esp != "Todas las Especialidades":
                lista_pacientes_filtrada = [p for p in lista_pacientes_cruda if p.get("esp", "Sin Especialidad") == filtro_esp]
            else:
                lista_pacientes_filtrada = lista_pacientes_cruda
                
            with c_busca:
                nombres_pac = {f"{p['nombre']} (Folio: {p['id_p']})": p for p in lista_pacientes_filtrada}
                if not nombres_pac:
                    st.info("No hay pacientes registrados bajo esta especialidad.")
                    return
                pac_sel = st.selectbox("🔍 Buscar y Seleccionar Expediente:", ["-- Seleccione un expediente --"] + list(nombres_pac.keys()), key="buscador_admin")
                
        else:
            lista_pacientes_filtrada = lista_pacientes_cruda
            nombres_pac = {f"{p['nombre']} (Folio: {p['id_p']})": p for p in lista_pacientes_filtrada}
            pac_sel = st.selectbox("🔍 Buscar y Seleccionar Expediente:", ["-- Seleccione un expediente --"] + list(nombres_pac.keys()), key="buscador_esp")

    # ==========================================
    # VALIDACIÓN DE SELECCIÓN
    # ==========================================
    if pac_sel == "-- Seleccione un expediente --":
        st.markdown("""
            <div style="background: #FFFFFF; border: 1px dashed #CBD5E1; border-radius: 16px; padding: 40px 24px; text-align: center; margin-top: 12px;">
                <div style="font-size: 36px; margin-bottom: 10px;">🗂️</div>
                <div style="font-weight: 700; color: #1E293B; font-size: 16px;">Ningún expediente abierto</div>
                <div style="color: #64748B; font-size: 13.5px; margin-top: 4px;">Utilice el buscador superior para desplegar la historia clínica, notas de evolución y anexos del paciente.</div>
            </div>
        """, unsafe_allow_html=True)
        return
        
    paciente = nombres_pac[pac_sel]
    id_pac = paciente['id_p']
    
    # Generar iniciales para el avatar del paciente
    palabras_nom = [w for w in paciente.get('nombre', 'P').replace("FAMILIA:", "").split() if w.isalpha()]
    iniciales_pac = "".join([w[0] for w in palabras_nom[:2]]).upper() if palabras_nom else "PT"
    
    # ==========================================
    # TARJETA DE PERFIL CLÍNICO PREMIUM
    # ==========================================
    st.markdown(f"""
        <div style="background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%); border: 1px solid #E2E8F0; border-radius: 18px; padding: 20px 24px; margin: 14px 0 20px 0; box-shadow: 0 8px 20px -6px rgba(15, 23, 42, 0.06);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px; border-bottom: 1px solid #F1F5F9; padding-bottom: 14px; margin-bottom: 14px;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div style="width: 48px; height: 48px; border-radius: 12px; background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%); color: white; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 17px; box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25);">
                        {iniciales_pac}
                    </div>
                    <div>
                        <div style="font-size: 19px; font-weight: 800; color: #0F172A; font-family: 'Plus Jakarta Sans', sans-serif; line-height: 1.2;">{paciente.get('nombre', 'N/A')}</div>
                        <div style="font-size: 12.5px; color: #64748B; margin-top: 3px;">Titular registrado • Tel: <b>{paciente.get('telefono', 'N/A')}</b></div>
                    </div>
                </div>
                <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                    <span style="background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; font-size: 12px; font-weight: 700; padding: 5px 12px; border-radius: 999px;">
                        🏥 {paciente.get('esp', 'CLÍNICA')}
                    </span>
                    <span style="background: #FFF7ED; color: #EA580C; border: 1px solid #FED7AA; font-size: 12px; font-weight: 700; padding: 5px 12px; border-radius: 999px;">
                        📄 Folio: {id_pac}
                    </span>
                    <span style="background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; font-size: 12px; font-weight: 700; padding: 5px 12px; border-radius: 999px;">
                        ● ACTIVO
                    </span>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 12px;">
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 10px 14px;">
                    <div style="font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase;">Edad / Sexo</div>
                    <div style="font-size: 14px; font-weight: 700; color: #1E293B; margin-top: 2px;">{paciente.get('edad', 'N/A')} años • {paciente.get('sexo', 'N/A')}</div>
                </div>
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 10px 14px;">
                    <div style="font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase;">Servicio y Modalidad</div>
                    <div style="font-size: 14px; font-weight: 700; color: #1E293B; margin-top: 2px;">{paciente.get('tipo_terapia', 'N/A')} ({paciente.get('modalidad', 'N/A')})</div>
                </div>
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 10px 14px;">
                    <div style="font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase;">Inicio de Tratamiento</div>
                    <div style="font-size: 14px; font-weight: 700; color: #059669; margin-top: 2px;">🗓️ {paciente.get('fecha_inicio_tratamiento', 'N/A')}</div>
                </div>
                <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: 10px 14px;">
                    <div style="font-size: 11px; color: #64748B; font-weight: 600; text-transform: uppercase;">Especialista Asignado</div>
                    <div style="font-size: 14px; font-weight: 700; color: #1E293B; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">👨‍⚕️ {paciente.get('med', 'N/A')}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

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

    with tab1: tab_legales.render(db, paciente, id_pac, rol)
    with tab2: tab_historia.render(db, paciente, id_pac)
    with tab3: tab_notas.render(db, id_pac)
    with tab4: tab_evaluaciones.render(db, id_pac)
    with tab5: tab_adjuntos.render(db, id_pac)
