import streamlit as st
from datetime import datetime
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER

# ==========================================
# MAPEO MAESTRO PARA ORDEN Y NOMBRES DE CAMPOS
# ==========================================
ORDEN_CAMPOS = {
    "PSICOLOGÍA ADULTOS": [
        ("ad_motivo_principal", "Motivo Principal de Consulta"),
        ("ad_sintomas", "Síntomas Actuales"),
        ("ad_expectativas", "Expectativas del Paciente"),
        ("ad_inicio", "Inicio del Problema"),
        ("ad_curso", "Curso o Evolución"),
        ("ad_eventos", "Eventos Significativos Asociados"),
        ("ad_factores", "Factores Desencadenantes/Agravantes"),
        ("ad_impacto", "Impacto (Personal, Familiar, Social, Laboral)"),
        ("ad_ant_medicos", "Antecedentes Médicos Relevantes"),
        ("ad_ant_psiq", "Tratamiento Psiquiátrico Previo"),
        ("ad_ant_psico", "Tratamientos Psicológicos Previos"),
        ("ad_meds", "Medicaciones Actuales"),
        ("ad_riesgo_suicida", "Riesgo Suicida o Autolesiones"),
        ("ad_sustancias", "Consumo de Sustancias"),
        ("ad_trauma", "Eventos Traumáticos"),
        ("ad_fam_comp", "1. Composición Familiar Actual"),
        ("ad_fam_origen", "2. Familia de Origen y Crianza"),
        ("ad_fam_relacion", "3. Relación con Figuras Parentales"),
        ("ad_fam_dinamica", "4. Dinámica Familiar durante el Desarrollo"),
        ("ad_fam_socioemocional", "5. Historia Socioemocional y Adaptación"),
        ("ad_fam_adversidades", "6. Pérdidas, Separaciones y Adversidades"),
        ("ad_fam_ant", "7. Antecedentes Familiares de Salud Mental"),
        ("ad_sueno", "Sueño"),
        ("ad_alimentacion", "Alimentación/Apetito"),
        ("ad_fisica", "Actividad Física"),
        ("ad_social", "Área Social y Red de Apoyo"),
        ("ad_emocional", "Autoestima y Regulación Emocional"),
        ("ad_apariencia", "Apariencia y Actitud"),
        ("ad_animo", "Estado de Ánimo y Afecto"),
        ("ad_pensamiento", "Pensamiento, Percepción y Cognición"),
        ("ad_juicio", "Juicio e Introspección"),
        ("ad_clinimetria", "Clinimetría (Pruebas Aplicadas)"),
        ("ad_predisponentes", "Factores Predisponentes"),
        ("ad_precipitantes", "Factores Precipitantes"),
        ("ad_mantenedores", "Factores Mantenedores"),
        ("ad_protectores", "Factores Protectores"),
        ("ad_hipotesis", "Hipótesis Clínica Inicial"),
        ("ad_dx", "Diagnóstico(s) DSM-5/CIE-11 y Severidad"),
        ("ad_plan", "Plan de Intervención y Objetivos"),
        ("ad_psiquiatria", "Necesidad de Evaluación Psiquiátrica")
    ],
    "PSICOLOGÍA INFANTOJUVENIL": [
        ("ij_padre", "Datos del Padre"),
        ("ij_madre", "Datos de la Madre"),
        ("ij_acompanante", "Persona que Acompaña"),
        ("ij_motivo_padres", "Motivo Referido por Padres"),
        ("ij_motivo_menor", "Motivo Referido por el Menor"),
        ("ij_sintomas", "Conductas/Síntomas y Evolución"),
        ("ij_impacto", "Impacto (Familiar, Escolar, Social)"),
        ("ij_hist_inicio", "Inicio del Problema"),
        ("ij_estrategias", "Estrategias Utilizadas Previamente"),
        ("ij_embarazo", "Antecedentes de Embarazo"),
        ("ij_parto", "Antecedentes de Parto"),
        ("ij_desarrollo", "Desarrollo Temprano"),
        ("ij_apego", "Apego Temprano / Cuidadores Principales"),
        ("ij_medicos", "Enfermedades Médicas y Tratamientos"),
        ("ij_psi", "Tratamientos Psicológicos/Psiquiátricos Previos"),
        ("ij_riesgos", "Riesgos (Autolesiones/Trauma/Sustancias)"),
        ("ij_fam_comp", "1. Composición Familiar Actual"),
        ("ij_fam_origen", "2. Familia de Origen y Crianza"),
        ("ij_fam_relacion", "3. Relación con Figuras Parentales"),
        ("ij_fam_dinamica", "4. Dinámica Familiar durante el Desarrollo"),
        ("ij_fam_socioemocional", "5. Historia Socioemocional y Adaptación"),
        ("ij_fam_adversidades", "6. Pérdidas, Separaciones y Adversidades"),
        ("ij_fam_ant", "7. Antecedentes Familiares de Salud Mental"),
        ("ij_sueno", "Sueño y Alimentación"),
        ("ij_emocional", "Regulación Emocional y Conducta en Casa"),
        ("ij_social", "Relaciones y Recreación"),
        ("ij_esc_desempeno", "Desempeño Académico y Conducta en Aula"),
        ("ij_esc_social", "Relación con Profesores y Compañeros"),
        ("ij_mental", "Estado Mental General"),
        ("ij_clinimetria", "Clinimetría (Pruebas Aplicadas)"),
        ("ij_formulacion", "Formulación Clínica"),
        ("ij_dx", "Diagnóstico DSM-5/CIE-11 y Riesgos"),
        ("ij_plan", "Plan de Intervención y Trabajo con Padres")
    ],
    "TERAPIA DE PAREJA": [
        ("p_tiempos", "Tiempo de Relación / Convivencia / Hijos"),
        ("p_motivo_pareja", "Motivo Principal Referido por la Pareja"),
        ("p_expectativas", "Expectativas del Proceso Terapéutico"),
        ("p_historia", "Historia de la Relación"),
        ("p_fortalezas", "Fortalezas de la Relación"),
        ("p_conflictos", "Principales Conflictos y Temas Recurrentes"),
        ("p_fam_comp", "1. Composición Familiar Actual"),
        ("p_fam_origen", "2. Familias de Origen"),
        ("p_fam_relacion", "3. Relación con Figuras Parentales"),
        ("p_fam_dinamica", "4. Dinámicas Familiares de Origen (Patrones)"),
        ("p_fam_socioemocional", "5. Historia Socioemocional de Cada Uno"),
        ("p_fam_adversidades", "6. Pérdidas y Experiencias Adversas"),
        ("p_fam_ant", "7. Antecedentes Familiares de Salud Mental"),
        ("p_patrones", "Patrones de Interacción en el Conflicto"),
        ("p_violencia", "Evaluación de Violencia y Seguridad"),
        ("p_plan", "Plan de Intervención")
    ],
    "NUTRICIÓN": [
        ("nut_motivo", "Motivo de Consulta"),
        ("nut_sintomas_gi_lista", "Síntomas Gastrointestinales Presentes"),
        ("nut_sintomas_gi_obs_opcional", "Observaciones Gastrointestinales"),
        ("nut_signos_fisicos", "Signos Físicos Generales"),
        ("nut_medicos", "Antecedentes Médicos y Quirúrgicos"),
        ("nut_meds", "Medicamentos, Suplementos, Sustancias"),
        ("nut_heredofamiliares", "Antecedentes Heredofamiliares Relevantes"),
        ("nut_contexto_fam", "Contexto Familiar-Alimentario"),
        ("nut_tca_fam", "Antecedentes Familiares de TCA o Alteraciones"),
        ("nut_tca_fam_cual", "Parentesco y Especificación de TCA"),
        ("nut_agua_rango", "Rango de Consumo de Agua"),
        ("nut_aceite", "Tipo de Aceite Utilizado"),
        ("nut_aceite_otro_opcional", "Otro Aceite Específico"),
        ("nut_sal", "Consumo de Sal Estimado"),
        ("nut_sal_obs_opcional", "Observaciones sobre Consumo de Sal"),
        ("nut_pref_si", "Alimentos Preferidos"),
        ("nut_pref_no", "Alimentos Evitados / No Preferidos"),
        ("nut_intolerancias", "Intolerancias Alimentarias"),
        ("nut_alergias_alim", "Alergias Alimentarias Conocidas"),
        ("nut_horarios", "Comidas al Día, Horarios y Lugares"),
        ("nut_frecuencia", "Frecuencia de Consumo de Grupos de Alimentos"),
        ("nut_rec24", "Recordatorio de 24 Horas"),
        ("nut_actividad", "Actividad Física"),
        ("nut_emocional", "Estado Emocional y Relación con Comida"),
        ("nut_sueno", "Calidad de Sueño"),
        ("nut_peso", "Peso (kg)"),
        ("nut_talla", "Estatura (cm)"),
        ("nut_imc", "IMC"),
        ("nut_grasa", "% Grasa / Músculo"),
        ("nut_cintura", "Circunferencias"),
        ("nut_objetivos", "Objetivos del Paciente"),
        ("nut_plan", "Plan Nutricional Inicial")
    ],
    "FISIOTERAPIA": [
        ("f_motivo", "Problema Principal y Zona Afectada"),
        ("f_evolucion", "Tiempo de Evolución"),
        ("f_mecanismo", "Mecanismo de Lesión"),
        ("f_tratamientos", "Tratamientos Previos y Estudios"),
        ("f_ant_medicos", "Enfermedades, Cirugías y Lesiones Previas"),
        ("f_dolor_eva", "Escala de Dolor (EVA)"),
        ("f_dolor_tipo", "Tipo de Dolor"),
        ("f_factores", "Factores Agravantes o Atenuantes"),
        ("f_fam_comp", "1. Composición Familiar Actual"),
        ("f_fam_origen", "2. Familia de Origen"),
        ("f_fam_relacion", "3. Relación con Cuidadores"),
        ("f_fam_dinamica", "4. Dinámica Familiar"),
        ("f_fam_socioemocional", "5. Historia Socioemocional y Adaptación"),
        ("f_fam_adversidades", "6. Experiencias Adversas"),
        ("f_fam_ant", "7. Antecedentes Familiares Generales"),
        ("f_exploracion", "Exploración Física y Rango de Movimiento"),
        ("f_pruebas", "Pruebas Especiales y Limitaciones"),
        ("f_dx", "Diagnóstico Fisioterapéutico"),
        ("f_plan", "Plan de Intervención y Frecuencia")
    ]
}

def generar_pdf_historia(paciente, datos_hc, tipo_plantilla):
    """Genera un archivo PDF estructurado en memoria usando ReportLab"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(name="TitleStyle", parent=styles['Heading1'], alignment=TA_CENTER, fontSize=16, spaceAfter=20, textColor="#164032")
    heading_style = ParagraphStyle(name="HeadingStyle", parent=styles['Heading2'], fontSize=12, spaceAfter=8, textColor="#164032")
    sub_heading = ParagraphStyle(name="SubHeading", parent=styles['Heading3'], fontSize=10, spaceAfter=5, textColor="#2980B9")
    emergencia_style = ParagraphStyle(name="EmergenciaStyle", parent=styles['Heading3'], fontSize=10, spaceAfter=5, textColor="#D35400")
    normal_style = ParagraphStyle(name="NormalStyle", parent=styles['Normal'], fontSize=10, spaceAfter=15, leading=14)
    
    elements = []
    
    # --- 1. CABECERA Y TÍTULO ---
    elements.append(Paragraph("HISTORIA CLÍNICA OFICIAL - TERINTALIA OS", title_style))
    
    # --- 2. FICHA DE IDENTIFICACIÓN ---
    elements.append(Paragraph("I. FICHA DE IDENTIFICACIÓN Y DATOS GENERALES", heading_style))
    
    nombre_pac = paciente.get('nombre_completo', paciente.get('nombre', 'N/A'))
    folio = paciente.get('id_p', 'N/A')
    inicio_tratamiento = paciente.get('fecha_inicio_tratamiento', 'N/A')
    
    info_expediente = f"""
    <b>Número de Expediente (Folio):</b> {folio}<br/>
    <b>Paciente:</b> {nombre_pac}<br/>
    <b>Fecha de Inicio de Tratamiento:</b> {inicio_tratamiento}<br/>
    <b>Fecha de Firma y Sello:</b> {datos_hc.get('fecha_firma', 'N/A')}<br/>
    <b>Especialista Firmante:</b> {datos_hc.get('firmado_por', 'N/A')}<br/>
    <b>Formato Clínico Aplicado:</b> {tipo_plantilla}
    """
    elements.append(Paragraph(info_expediente, normal_style))
    
    # Datos Personales
    elements.append(Paragraph("Datos Personales", sub_heading))
    datos_personales = f"""
    <b>Edad:</b> {paciente.get('edad', 'N/A')} años | <b>Sexo:</b> {paciente.get('sexo', paciente.get('genero', 'N/A'))} | <b>F. Nacimiento:</b> {paciente.get('fecha_nacimiento', paciente.get('fecha_nac', 'N/A'))}<br/>
    <b>Estado Civil:</b> {paciente.get('estado_civil', 'N/A')} | <b>Escolaridad:</b> {paciente.get('escolaridad', paciente.get('grado_estudios', 'N/A'))}<br/>
    <b>Ocupación:</b> {paciente.get('ocupacion', paciente.get('profesion', 'N/A'))} | <b>Religión:</b> {paciente.get('religion', paciente.get('creencia', 'N/A'))}
    """
    elements.append(Paragraph(datos_personales, normal_style))
    
    # Contacto y Dirección
    elements.append(Paragraph("Contacto y Dirección", sub_heading))
    contacto = f"""
    <b>Tel. Celular:</b> {paciente.get('telefono', paciente.get('celular', 'N/A'))} | <b>Tel. Casa:</b> {paciente.get('tel_casa', paciente.get('telefono_fijo', paciente.get('tel_fijo', 'N/A')))}<br/>
    <b>Correo:</b> {paciente.get('correo', paciente.get('email', 'N/A'))}<br/>
    <b>Domicilio:</b> {paciente.get('domicilio', paciente.get('direccion', 'N/A'))}
    """
    elements.append(Paragraph(contacto, normal_style))
    
    # Atención Clínica
    elements.append(Paragraph("Datos de Atención Clínica", sub_heading))
    atencion = f"""
    <b>Especialista Asignado:</b> {paciente.get('esp', paciente.get('especialista_asignado', 'N/A'))}<br/>
    <b>Tipo de Terapia:</b> {paciente.get('tipo_terapia', paciente.get('servicio', 'N/A'))} | <b>Modalidad:</b> {paciente.get('modalidad', 'N/A')}
    """
    elements.append(Paragraph(atencion, normal_style))
    
    # Emergencia
    elements.append(Paragraph("Contacto de Emergencia", emergencia_style))
    emergencia = f"""
    <b>Llamar a:</b> {paciente.get('contacto_emergencia_nom', paciente.get('contacto_emergencia', paciente.get('nombre_emergencia', 'N/A')))}<br/>
    <b>Parentesco:</b> {paciente.get('contacto_emergencia_par', paciente.get('parentesco_emergencia', paciente.get('parentesco', 'N/A')))} | <b>Teléfono:</b> {paciente.get('contacto_emergencia_tel', paciente.get('tel_emergencia', paciente.get('telefono_emergencia', 'N/A')))}
    """
    elements.append(Paragraph(emergencia, normal_style))
    
    elements.append(Spacer(1, 15))
    
    # --- 3. REGISTRO CLÍNICO ---
    elements.append(Paragraph("II. REGISTRO CLÍNICO DE EVALUACIÓN", heading_style))
    elements.append(Spacer(1, 5))
    
    for clave, titulo in ORDEN_CAMPOS.get(tipo_plantilla, []):
        valor = datos_hc.get(clave, "N/A")
        if isinstance(valor, list):
            valor = ", ".join(valor) if valor else "Ninguno"
            
        if str(valor).strip() and str(valor).strip() != "N/A":
            valor_limpio = str(valor).replace('\n', '<br />')
            elements.append(Paragraph(titulo, sub_heading))
            elements.append(Paragraph(valor_limpio, normal_style))
            
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

def render(db, paciente, id_pac):
    if 'conf_borrador' not in st.session_state: st.session_state.conf_borrador = False
    if 'conf_sello' not in st.session_state: st.session_state.conf_sello = False
    if 'tmp_hc' not in st.session_state: st.session_state.tmp_hc = {}

    ref_hc = db.collection("pacientes").document(id_pac).collection("historia_clinica").document("unica")
    doc_hc = ref_hc.get()
    
    datos_hc = doc_hc.to_dict() if doc_hc.exists else {}
    bloqueado = datos_hc.get("bloqueado", False)

    # ==========================================
    # RUTEO INTELIGENTE DE PLANTILLAS
    # ==========================================
    esp_upper = paciente.get("esp", "").upper()
    terapia = paciente.get("tipo_terapia", "")
    edad = int(paciente.get("edad", 0))

    if "FISIO" in esp_upper:
        tipo_plantilla = "FISIOTERAPIA"
    elif "NUTRI" in esp_upper:
        tipo_plantilla = "NUTRICIÓN"
    elif terapia == "De Pareja":
        tipo_plantilla = "TERAPIA DE PAREJA"
    elif edad < 18:
        tipo_plantilla = "PSICOLOGÍA INFANTOJUVENIL"
    else:
        tipo_plantilla = "PSICOLOGÍA ADULTOS"

    # =========================================================
    # APARTADO I: FICHA DE IDENTIFICACIÓN ESTILO BENTO GRID
    # =========================================================
    c_tit, c_pdf = st.columns([2.8, 1.2])
    with c_tit:
        st.markdown(f"""
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
                <span style="background:#EFF6FF; color:#1D4ED8; font-weight:800; font-size:12px; padding:4px 10px; border-radius:8px;">SECCIÓN I</span>
                <h4 style="color:#0F172A; margin:0; font-size:18px; font-weight:800;">Ficha de Identificación y Datos Generales</h4>
            </div>
        """, unsafe_allow_html=True)
    with c_pdf:
        if bloqueado:
            pdf_data = generar_pdf_historia(paciente, datos_hc, tipo_plantilla)
            st.download_button(
                label="📥 Exportar Historia (PDF)",
                data=pdf_data,
                file_name=f"Historia_Clinica_{paciente.get('nombre', 'Paciente')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
        else:
            st.button("🔒 Requiere Sello para PDF", disabled=True, use_container_width=True)

    # Variables seguras para la tarjeta Bento Grid
    nom_p = paciente.get('nombre_completo', paciente.get('nombre', 'N/A'))
    edad_p = paciente.get('edad', 'N/A')
    sexo_p = paciente.get('sexo', paciente.get('genero', 'N/A'))
    fnac_p = paciente.get('fecha_nacimiento', paciente.get('fecha_nac', 'N/A'))
    eciv_p = paciente.get('estado_civil', 'N/A')
    esc_p = paciente.get('escolaridad', paciente.get('grado_estudios', 'N/A'))
    ocu_p = paciente.get('ocupacion', paciente.get('profesion', 'N/A'))
    
    tel_p = paciente.get('telefono', paciente.get('celular', 'N/A'))
    tcasa_p = paciente.get('tel_casa', paciente.get('telefono_fijo', paciente.get('tel_fijo', 'N/A')))
    mail_p = paciente.get('correo', paciente.get('email', 'N/A'))
    dir_p = paciente.get('domicilio', paciente.get('direccion', 'N/A'))
    
    esp_p = paciente.get('med', paciente.get('esp', 'N/A'))
    serv_p = paciente.get('tipo_terapia', paciente.get('servicio', 'N/A'))
    mod_p = paciente.get('modalidad', 'N/A')
    ini_p = paciente.get('fecha_inicio_tratamiento', 'N/A')
    
    em_nom = paciente.get('contacto_emergencia_nom', paciente.get('contacto_emergencia', paciente.get('nombre_emergencia', 'N/A')))
    em_par = paciente.get('contacto_emergencia_par', paciente.get('parentesco_emergencia', paciente.get('parentesco', 'N/A')))
    em_tel = paciente.get('contacto_emergencia_tel', paciente.get('tel_emergencia', paciente.get('telefono_emergencia', 'N/A')))

    st.markdown(f"""
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 14px; margin-bottom: 22px;">
            <!-- TARJETA 1: DATOS DEMOGRÁFICOS -->
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 16px 18px; box-shadow: 0 2px 6px rgba(15,23,42,0.02);">
                <div style="font-size: 12px; font-weight: 700; color: #1E3A8A; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>👤 Perfil Demográfico</span>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;">
                    <div><span style="color:#64748B;">Nacimiento:</span> <b style="color:#0F172A;">{fnac_p}</b></div>
                    <div><span style="color:#64748B;">Edad/Sexo:</span> <b style="color:#0F172A;">{edad_p}a • {sexo_p}</b></div>
                    <div><span style="color:#64748B;">Est. Civil:</span> <b style="color:#0F172A;">{eciv_p}</b></div>
                    <div><span style="color:#64748B;">Escolaridad:</span> <b style="color:#0F172A;">{esc_p}</b></div>
                    <div style="grid-column: span 2;"><span style="color:#64748B;">Ocupación:</span> <b style="color:#0F172A;">{ocu_p}</b></div>
                </div>
            </div>
            <!-- TARJETA 2: CONTACTO Y DOMICILIO -->
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 16px 18px; box-shadow: 0 2px 6px rgba(15,23,42,0.02);">
                <div style="font-size: 12px; font-weight: 700; color: #059669; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>📞 Contacto y Domicilio</span>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;">
                    <div><span style="color:#64748B;">Celular:</span> <b style="color:#0F172A;">{tel_p}</b></div>
                    <div><span style="color:#64748B;">Tel. Casa:</span> <b style="color:#0F172A;">{tcasa_p if tcasa_p else 'N/A'}</b></div>
                    <div style="grid-column: span 2;"><span style="color:#64748B;">Correo:</span> <b style="color:#0F172A;">{mail_p if mail_p else 'N/A'}</b></div>
                    <div style="grid-column: span 2; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;"><span style="color:#64748B;">Domicilio:</span> <b style="color:#0F172A;">{dir_p}</b></div>
                </div>
            </div>
            <!-- TARJETA 3: ASIGNACIÓN CLÍNICA -->
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 16px 18px; box-shadow: 0 2px 6px rgba(15,23,42,0.02);">
                <div style="font-size: 12px; font-weight: 700; color: #2563EB; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>🏥 Asignación y Tratamiento</span>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;">
                    <div style="grid-column: span 2;"><span style="color:#64748B;">Especialista:</span> <b style="color:#0F172A;">{esp_p}</b></div>
                    <div><span style="color:#64748B;">Servicio:</span> <b style="color:#0F172A;">{serv_p} ({mod_p})</b></div>
                    <div><span style="color:#64748B;">Inicio Trat.:</span> <b style="color:#059669;">{ini_p}</b></div>
                </div>
            </div>
            <!-- TARJETA 4: CONTACTO DE EMERGENCIA -->
            <div style="background: #FFF5F5; border: 1px solid #FED7D7; border-radius: 14px; padding: 16px 18px; box-shadow: 0 2px 6px rgba(220,38,38,0.03);">
                <div style="font-size: 12px; font-weight: 700; color: #DC2626; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 10px; display:flex; align-items:center; gap:6px;">
                    <span>🚨 En Caso de Emergencia</span>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; font-size: 13px;">
                    <div style="grid-column: span 2;"><span style="color:#991B1B;">Contactar a:</span> <b style="color:#7F1D1D;">{em_nom if em_nom else 'No especificado'}</b></div>
                    <div><span style="color:#991B1B;">Parentesco:</span> <b style="color:#7F1D1D;">{em_par if em_par else 'N/A'}</b></div>
                    <div><span style="color:#991B1B;">Teléfono:</span> <b style="color:#7F1D1D;">{em_tel if em_tel else 'N/A'}</b></div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ==========================================
    # VISTA DE LECTURA (CUANDO YA ESTÁ SELLADO)
    # ==========================================
    if bloqueado:
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ECFDF5 0%, #D1FAE5 100%); border: 1px solid #6EE7B7; border-radius: 14px; padding: 16px 20px; margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <div style="color: #065F46; font-weight: 800; font-size: 15px;">🔒 HISTORIA CLÍNICA CERRADA Y SELLADA LEGALMENTE</div>
                    <div style="color: #047857; font-size: 12.5px; margin-top: 2px;">Firmado por: <b>{datos_hc.get('firmado_por')}</b> el {datos_hc.get('fecha_firma')}</div>
                </div>
                <span style="background: #FFFFFF; color: #059669; font-weight: 700; font-size: 12px; padding: 5px 12px; border-radius: 999px; border: 1px solid #A7F3D0;">Formato: {tipo_plantilla}</span>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("<h5 style='color: #0F172A; margin-bottom: 16px;'>📋 Registro Clínico de Evaluación</h5>", unsafe_allow_html=True)
            
            for clave, titulo in ORDEN_CAMPOS.get(tipo_plantilla, []):
                valor = datos_hc.get(clave, "N/A")
                if isinstance(valor, list):
                    valor = ", ".join(valor) if valor else "Ninguno"
                
                if str(valor).strip() and str(valor).strip() != "N/A":
                    st.markdown(f"""
                        <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 4px solid #2563EB; border-radius: 10px; padding: 12px 16px; margin-bottom: 10px;">
                            <div style="font-size: 12px; font-weight: 700; color: #1E3A8A; text-transform: uppercase; letter-spacing: 0.4px; margin-bottom: 4px;">{titulo}</div>
                            <div style="font-size: 14px; color: #1E293B; line-height: 1.5; white-space: pre-wrap;">{valor}</div>
                        </div>
                    """, unsafe_allow_html=True)

    # ==========================================
    # MODO EDICIÓN (BORRADOR ACTIVO)
    # ==========================================
    else:
        if not st.session_state.conf_borrador and not st.session_state.conf_sello:
            st.markdown(f"""
                <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 12px; padding: 12px 18px; margin-bottom: 14px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                    <div style="color: #1E3A8A; font-size: 13.5px; font-weight: 600;">📝 <b>MODO EDICIÓN (Borrador Activo)</b> — Complete los apartados desplegables. Si un campo no aplica, escriba <b>'N/A'</b>.</div>
                    <span style="background: #DBEAFE; color: #1D4ED8; font-size: 11.5px; font-weight: 700; padding: 4px 10px; border-radius: 999px;">Plantilla: {tipo_plantilla}</span>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("form_hc"):
                payload = {}
                
                # ---------------------------------------------------------
                # 1. PLANTILLA: PSICOLOGÍA ADULTOS
                # ---------------------------------------------------------
                if tipo_plantilla == "PSICOLOGÍA ADULTOS":
                    with st.expander("II. Motivo de Consulta e III. Historia del Problema", expanded=True):
                        payload["ad_motivo_principal"] = st.text_area("Motivo principal de consulta:", value=datos_hc.get("ad_motivo_principal", ""))
                        payload["ad_sintomas"] = st.text_area("Síntomas actuales:", value=datos_hc.get("ad_sintomas", ""))
                        payload["ad_expectativas"] = st.text_area("Expectativas del paciente:", value=datos_hc.get("ad_expectativas", ""))
                        c1, c2 = st.columns(2)
                        payload["ad_inicio"] = c1.text_area("Inicio del problema:", value=datos_hc.get("ad_inicio", ""))
                        payload["ad_curso"] = c2.text_area("Curso o evolución:", value=datos_hc.get("ad_curso", ""))
                        payload["ad_eventos"] = st.text_area("Eventos significativos asociados:", value=datos_hc.get("ad_eventos", ""))
                        payload["ad_factores"] = st.text_area("Factores desencadenantes/agravantes:", value=datos_hc.get("ad_factores", ""))
                        payload["ad_impacto"] = st.text_area("Impacto (Personal, Familiar, Social, Laboral):", value=datos_hc.get("ad_impacto", ""))

                    with st.expander("IV. Antecedentes Personales (Médicos, Psiquiátricos y Trauma)"):
                        c1, c2 = st.columns(2)
                        payload["ad_ant_medicos"] = c1.text_area("Antecedentes médicos relevantes:", value=datos_hc.get("ad_ant_medicos", ""))
                        payload["ad_ant_psiq"] = c2.text_area("Tratamiento psiquiátrico previo:", value=datos_hc.get("ad_ant_psiq", ""))
                        c3, c4 = st.columns(2)
                        payload["ad_ant_psico"] = c3.text_area("Tratamientos psicológicos previos:", value=datos_hc.get("ad_ant_psico", ""))
                        payload["ad_meds"] = c4.text_area("Medicaciones actuales:", value=datos_hc.get("ad_meds", ""))
                        payload["ad_riesgo_suicida"] = st.text_area("Intentos suicidas, autolesiones o ideación actual:", value=datos_hc.get("ad_riesgo_suicida", ""))
                        payload["ad_sustancias"] = st.text_area("Consumo de alcohol u otras sustancias:", value=datos_hc.get("ad_sustancias", ""))
                        payload["ad_trauma"] = st.text_area("Eventos traumáticos (abuso, negligencia, violencia):", value=datos_hc.get("ad_trauma", ""))

                    with st.expander("V. Historia familiar, evolutiva y relacional"):
                        payload["ad_fam_comp"] = st.text_area("1. Composición familiar actual (¿Con quién vive? Parentesco, edades, cambios recientes):", value=datos_hc.get("ad_fam_comp", ""))
                        payload["ad_fam_origen"] = st.text_area("2. Familia de origen y contexto de crianza (Con quién creció, cuidadores principales, migraciones):", value=datos_hc.get("ad_fam_origen", ""))
                        payload["ad_fam_relacion"] = st.text_area("3. Relación con figuras parentales o cuidadores (Disponibilidad emocional, protección, límites, rechazo):", value=datos_hc.get("ad_fam_relacion", ""))
                        payload["ad_fam_dinamica"] = st.text_area("4. Dinámica familiar durante el desarrollo (Comunicación, resolución de conflictos, violencia, inestabilidad):", value=datos_hc.get("ad_fam_dinamica", ""))
                        payload["ad_fam_socioemocional"] = st.text_area("5. Historia socioemocional y adaptación (Adaptación escolar, pares, aislamiento, bullying):", value=datos_hc.get("ad_fam_socioemocional", ""))
                        payload["ad_fam_adversidades"] = st.text_area("6. Pérdidas, separaciones y experiencias adversas (Duelos, abandonos, hospitalizaciones, abuso):", value=datos_hc.get("ad_fam_adversidades", ""))
                        payload["ad_fam_ant"] = st.text_area("7. Antecedentes familiares de salud mental y adicciones (Trastornos conocidos, suicidio, adicciones):", value=datos_hc.get("ad_fam_ant", ""))

                    with st.expander("VI. Funcionamiento Actual y VII. Estado Mental"):
                        c1, c2, c3 = st.columns(3)
                        payload["ad_sueno"] = c1.text_area("Sueño:", value=datos_hc.get("ad_sueno", ""))
                        payload["ad_alimentacion"] = c2.text_area("Alimentación/Apetito:", value=datos_hc.get("ad_alimentacion", ""))
                        payload["ad_fisica"] = c3.text_area("Actividad física:", value=datos_hc.get("ad_fisica", ""))
                        payload["ad_social"] = st.text_area("Área social y Red de apoyo:", value=datos_hc.get("ad_social", ""))
                        payload["ad_emocional"] = st.text_area("Autoestima y Regulación emocional:", value=datos_hc.get("ad_emocional", ""))
                        st.markdown("---")
                        c4, c5 = st.columns(2)
                        payload["ad_apariencia"] = c4.text_area("Apariencia y actitud:", value=datos_hc.get("ad_apariencia", ""))
                        payload["ad_animo"] = c5.text_area("Estado de ánimo y afecto:", value=datos_hc.get("ad_animo", ""))
                        payload["ad_pensamiento"] = st.text_area("Lenguaje, pensamiento, percepción y cognición:", value=datos_hc.get("ad_pensamiento", ""))
                        payload["ad_juicio"] = st.text_area("Juicio, introspección y signos de disociación:", value=datos_hc.get("ad_juicio", ""))

                    with st.expander("VIII. Clinimetría"):
                        payload["ad_clinimetria"] = st.text_area("Registro de Pruebas aplicadas (Prueba, Fecha, Resultado, Interpretación):", value=datos_hc.get("ad_clinimetria", ""))

                    with st.expander("IX. Formulación, X. Diagnóstico y XI. Plan"):
                        c1, c2 = st.columns(2)
                        payload["ad_predisponentes"] = c1.text_area("Factores predisponentes:", value=datos_hc.get("ad_predisponentes", ""))
                        payload["ad_precipitantes"] = c2.text_area("Factores precipitantes:", value=datos_hc.get("ad_precipitantes", ""))
                        c3, c4 = st.columns(2)
                        payload["ad_mantenedores"] = c3.text_area("Factores mantenedores:", value=datos_hc.get("ad_mantenedores", ""))
                        payload["ad_protectores"] = c4.text_area("Factores protectores:", value=datos_hc.get("ad_protectores", ""))
                        payload["ad_hipotesis"] = st.text_area("Hipótesis clínica inicial:", value=datos_hc.get("ad_hipotesis", ""))
                        st.markdown("---")
                        payload["ad_dx"] = st.text_area("Diagnóstico(s) DSM-5/CIE-11 y Severidad:", value=datos_hc.get("ad_dx", ""))
                        payload["ad_plan"] = st.text_area("Plan de intervención, modelos y objetivos:", value=datos_hc.get("ad_plan", ""))
                        payload["ad_psiquiatria"] = st.selectbox("¿Necesidad de evaluación psiquiátrica?", ["", "Sí", "No"], index=["", "Sí", "No"].index(datos_hc.get("ad_psiquiatria", "")))

                # ---------------------------------------------------------
                # 2. PLANTILLA: INFANTO-JUVENIL
                # ---------------------------------------------------------
                elif tipo_plantilla == "PSICOLOGÍA INFANTOJUVENIL":
                    with st.expander("II. Datos de Padres/Tutores e III. Motivo", expanded=True):
                        c1, c2 = st.columns(2)
                        payload["ij_padre"] = c1.text_area("Datos del Padre (Nombre, Edad, Ocupación, Tel):", value=datos_hc.get("ij_padre", ""))
                        payload["ij_madre"] = c2.text_area("Datos de la Madre (Nombre, Edad, Ocupación, Tel):", value=datos_hc.get("ij_madre", ""))
                        payload["ij_acompanante"] = st.text_area("Persona que acompaña al menor:", value=datos_hc.get("ij_acompanante", ""))
                        st.markdown("---")
                        payload["ij_motivo_padres"] = st.text_area("Motivo referido por padres/cuidadores:", value=datos_hc.get("ij_motivo_padres", ""))
                        payload["ij_motivo_menor"] = st.text_area("Motivo referido por menor (si aplica):", value=datos_hc.get("ij_motivo_menor", ""))
                        payload["ij_sintomas"] = st.text_area("Conductas/síntomas observados y Tiempo de evolución:", value=datos_hc.get("ij_sintomas", ""))
                        payload["ij_impacto"] = st.text_area("Impacto (Familiar, Escolar, Social):", value=datos_hc.get("ij_impacto", ""))

                    with st.expander("IV. Historia y V. Perinatales/Desarrollo"):
                        payload["ij_hist_inicio"] = st.text_area("Inicio del problema y eventos asociados:", value=datos_hc.get("ij_hist_inicio", ""))
                        payload["ij_estrategias"] = st.text_area("Estrategias utilizadas previamente:", value=datos_hc.get("ij_estrategias", ""))
                        st.markdown("---")
                        c1, c2 = st.columns(2)
                        payload["ij_embarazo"] = c1.text_area("Embarazo (Planeado, complicaciones):", value=datos_hc.get("ij_embarazo", ""))
                        payload["ij_parto"] = c2.text_area("Parto (Natural/Cesárea, complicaciones):", value=datos_hc.get("ij_parto", ""))
                        payload["ij_desarrollo"] = st.text_area("Desarrollo temprano (Palabras, marcha, esfínteres):", value=datos_hc.get("ij_desarrollo", ""))
                        payload["ij_apego"] = st.text_area("Apego temprano / Cuidadores principales:", value=datos_hc.get("ij_apego", ""))

                    with st.expander("VI. Antecedentes Médicos y Psiquiátricos"):
                        payload["ij_medicos"] = st.text_area("Enfermedades médicas y tratamientos actuales:", value=datos_hc.get("ij_medicos", ""))
                        payload["ij_psi"] = st.text_area("Tratamientos psico/psiquiátricos previos y trauma:", value=datos_hc.get("ij_psi", ""))
                        payload["ij_riesgos"] = st.text_area("Intentos autolesivos / Sustancias / Trauma / ASI:", value=datos_hc.get("ij_riesgos", ""))
                    
                    with st.expander("VII. Historia familiar, evolutiva y relacional"):
                        payload["ij_fam_comp"] = st.text_area("1. Composición familiar actual (¿Con quién vive? Parentesco, edades, cambios recientes):", value=datos_hc.get("ij_fam_comp", ""))
                        payload["ij_fam_origen"] = st.text_area("2. Familia de origen y contexto de crianza (Con quién creció, cuidadores, migraciones):", value=datos_hc.get("ij_fam_origen", ""))
                        payload["ij_fam_relacion"] = st.text_area("3. Relación con figuras parentales o cuidadores (Disponibilidad emocional, protección, límites):", value=datos_hc.get("ij_fam_relacion", ""))
                        payload["ij_fam_dinamica"] = st.text_area("4. Dinámica familiar durante el desarrollo (Comunicación, resolución de conflictos, inestabilidad):", value=datos_hc.get("ij_fam_dinamica", ""))
                        payload["ij_fam_socioemocional"] = st.text_area("5. Historia socioemocional y adaptación (Adaptación escolar, pares, aislamiento, bullying):", value=datos_hc.get("ij_fam_socioemocional", ""))
                        payload["ij_fam_adversidades"] = st.text_area("6. Pérdidas, separaciones y experiencias adversas (Duelos, abandonos, abuso, accidentes):", value=datos_hc.get("ij_fam_adversidades", ""))
                        payload["ij_fam_ant"] = st.text_area("7. Antecedentes familiares de salud mental y adicciones (Ansiedad, depresión, sustancias, etc.):", value=datos_hc.get("ij_fam_ant", ""))

                    with st.expander("VIII. Funcionamiento Actual y IX. Escolar"):
                        c1, c2 = st.columns(2)
                        payload["ij_sueno"] = c1.text_area("Sueño y Alimentación:", value=datos_hc.get("ij_sueno", ""))
                        payload["ij_emocional"] = c2.text_area("Regulación emocional y Conducta en casa:", value=datos_hc.get("ij_emocional", ""))
                        payload["ij_social"] = st.text_area("Relaciones (Hermanos, Pares) y Recreación/Pantallas:", value=datos_hc.get("ij_social", ""))
                        st.markdown("---")
                        payload["ij_esc_desempeno"] = st.text_area("Desempeño académico y Conducta en aula:", value=datos_hc.get("ij_esc_desempeno", ""))
                        payload["ij_esc_social"] = st.text_area("Relación con profesores y compañeros:", value=datos_hc.get("ij_esc_social", ""))

                    with st.expander("X. Estado Mental y XI. Clinimetría"):
                        payload["ij_mental"] = st.text_area("Estado mental (Apariencia, afecto, cognición, juego simbólico):", value=datos_hc.get("ij_mental", ""))
                        payload["ij_clinimetria"] = st.text_area("Clinimetría (Pruebas, Fechas, Resultados e Interpretación):", value=datos_hc.get("ij_clinimetria", ""))

                    with st.expander("XII. Formulación, XIII. Diagnóstico y XIV. Plan"):
                        payload["ij_formulacion"] = st.text_area("Formulación clínica (Predisponentes, precipitantes, protectores, hipótesis):", value=datos_hc.get("ij_formulacion", ""))
                        payload["ij_dx"] = st.text_area("Diagnóstico DSM-5/CIE-11 y Riesgos:", value=datos_hc.get("ij_dx", ""))
                        payload["ij_plan"] = st.text_area("Plan de intervención, trabajo con padres y objetivos:", value=datos_hc.get("ij_plan", ""))

                # ---------------------------------------------------------
                # 3. PLANTILLA: TERAPIA DE PAREJA
                # ---------------------------------------------------------
                elif tipo_plantilla == "TERAPIA DE PAREJA":
                    with st.expander("II. Datos de Identificación de la Relación y Motivo", expanded=True):
                        payload["p_tiempos"] = st.text_area("Tiempo de relación / Convivencia / Hijos:", value=datos_hc.get("p_tiempos", ""))
                        payload["p_motivo_pareja"] = st.text_area("Motivo principal referido por la pareja:", value=datos_hc.get("p_motivo_pareja", ""))
                        payload["p_expectativas"] = st.text_area("Expectativas del proceso terapéutico:", value=datos_hc.get("p_expectativas", ""))

                    with st.expander("III. Historia y IV. Dinámica Actual"):
                        payload["p_historia"] = st.text_area("Historia de relación (Cómo se conocieron, inicio, momentos significativos):", value=datos_hc.get("p_historia", ""))
                        st.markdown("---")
                        payload["p_fortalezas"] = st.text_area("Fortalezas de la relación:", value=datos_hc.get("p_fortalezas", ""))
                        payload["p_conflictos"] = st.text_area("Principales conflictos y temas recurrentes:", value=datos_hc.get("p_conflictos", ""))

                    with st.expander("V. Historia familiar, evolutiva y relacional (De ambos integrantes)"):
                        st.info("💡 Describa de manera integrada o separada los aspectos relevantes de ambos integrantes en cada rubro.")
                        payload["p_fam_comp"] = st.text_area("1. Composición familiar actual (Hijos, dependientes, cohabitantes):", value=datos_hc.get("p_fam_comp", ""))
                        payload["p_fam_origen"] = st.text_area("2. Familias de origen y contexto de crianza de cada uno:", value=datos_hc.get("p_fam_origen", ""))
                        payload["p_fam_relacion"] = st.text_area("3. Relación con figuras parentales o cuidadores de cada uno:", value=datos_hc.get("p_fam_relacion", ""))
                        payload["p_fam_dinamica"] = st.text_area("4. Dinámicas familiares de origen (Patrones aprendidos):", value=datos_hc.get("p_fam_dinamica", ""))
                        payload["p_fam_socioemocional"] = st.text_area("5. Historia socioemocional y relaciones pasadas de cada uno:", value=datos_hc.get("p_fam_socioemocional", ""))
                        payload["p_fam_adversidades"] = st.text_area("6. Pérdidas, separaciones y experiencias adversas previas a la relación:", value=datos_hc.get("p_fam_adversidades", ""))
                        payload["p_fam_ant"] = st.text_area("7. Antecedentes familiares de salud mental y adicciones en ambos lados:", value=datos_hc.get("p_fam_ant", ""))

                    with st.expander("VI. Patrones, VII. Violencia y VIII. Plan"):
                        payload["p_patrones"] = st.text_area("Patrones de interacción (Inicio del conflicto, reacciones, escalada, reparación):", value=datos_hc.get("p_patrones", ""))
                        st.markdown("---")
                        st.warning("⚠️ **Evaluación de Violencia y Seguridad**")
                        payload["p_violencia"] = st.text_area("Evaluar presencia de violencia (Física, Psicológica, Económica, Control coercitivo):", value=datos_hc.get("p_violencia", ""))
                        st.markdown("---")
                        payload["p_plan"] = st.text_area("Plan de intervención (Modelo y Frecuencia):", value=datos_hc.get("p_plan", ""))

                # ---------------------------------------------------------
                # 4. PLANTILLA: NUTRICIÓN
                # ---------------------------------------------------------
                elif tipo_plantilla == "NUTRICIÓN":
                    with st.expander("II. Motivo y Síntomas", expanded=True):
                        payload["nut_motivo"] = st.text_area("Motivo de consulta:", value=datos_hc.get("nut_motivo", ""))
                        st.markdown("<h5 style='color: #2980B9; font-size: 14px; margin-bottom: 5px;'>Síntomas Gastrointestinales</h5>", unsafe_allow_html=True)
                        opciones_gi = ["Reflujo", "Gastritis / ardor estomacal", "Náusea", "Vómito", "Distensión abdominal", "Dolor abdominal", "Estreñimiento", "Diarrea", "Colitis / intestino irritable referido", "Gases / flatulencia", "Saciedad temprana", "Otro"]
                        payload["nut_sintomas_gi_lista"] = st.multiselect("Seleccione los síntomas presentes (Opcional):", opciones_gi, default=datos_hc.get("nut_sintomas_gi_lista", []))
                        payload["nut_sintomas_gi_obs_opcional"] = st.text_area("Observaciones sobre síntomas gastrointestinales (Opcional):", value=datos_hc.get("nut_sintomas_gi_obs_opcional", ""))
                        st.markdown("---")
                        payload["nut_signos_fisicos"] = st.text_area("Signos físicos generales (Piel, uñas, cabello, etc.):", value=datos_hc.get("nut_signos_fisicos", ""))

                    with st.expander("III. Antecedentes Médicos Personales"):
                        payload["nut_medicos"] = st.text_area("Antecedentes Médicos y Quirúrgicos:", value=datos_hc.get("nut_medicos", ""))
                        payload["nut_meds"] = st.text_area("Medicamentos, Suplementos, Sustancias:", value=datos_hc.get("nut_meds", ""))
                        st.markdown("---")
                        payload["nut_heredofamiliares"] = st.text_area("Antecedentes heredofamiliares relevantes:", value=datos_hc.get("nut_heredofamiliares", ""))

                    with st.expander("IV. Hábitos Alimenticios y Recordatorio 24h"):
                        payload["nut_contexto_fam"] = st.text_area("Contexto familiar-alimentario:", value=datos_hc.get("nut_contexto_fam", ""))
                        
                        c_tca1, c_tca2 = st.columns(2)
                        opciones_tca = ["", "Sí", "No", "Se desconoce"]
                        payload["nut_tca_fam"] = c_tca1.selectbox("Antecedentes familiares de TCA o alteraciones de la conducta alimentaria:", opciones_tca, index=opciones_tca.index(datos_hc.get("nut_tca_fam", "")) if datos_hc.get("nut_tca_fam", "") in opciones_tca else 0)
                        payload["nut_tca_fam_cual"] = c_tca2.text_input("¿Cuál y parentesco?", value=datos_hc.get("nut_tca_fam_cual", ""))
                        
                        st.markdown("---")
                        opciones_agua = ["", "<500 mL/día", "500–999 mL/día", "1–1.49 L/día", "1.5–1.99 L/día", "2–2.49 L/día", "2.5–2.99 L/día", "≥3 L/día"]
                        payload["nut_agua_rango"] = st.selectbox("Consumo de agua (Rango diario):", opciones_agua, index=opciones_agua.index(datos_hc.get("nut_agua_rango", "")) if datos_hc.get("nut_agua_rango", "") in opciones_agua else 0)
                        
                        st.markdown("---")
                        c_ace1, c_ace2 = st.columns(2)
                        opciones_aceite = ["", "Aceite vegetal", "Aceite de oliva", "Aceite de canola", "Aceite de aguacate", "Manteca", "Mantequilla", "No utiliza aceite", "Otro"]
                        payload["nut_aceite"] = c_ace1.selectbox("Tipo de aceite con el que cocina:", opciones_aceite, index=opciones_aceite.index(datos_hc.get("nut_aceite", "")) if datos_hc.get("nut_aceite", "") in opciones_aceite else 0)
                        payload["nut_aceite_otro_opcional"] = c_ace2.text_input("Si eligió 'Otro' en aceite, especifique (Opcional):", value=datos_hc.get("nut_aceite_otro_opcional", ""))
                        
                        c_sal1, c_sal2 = st.columns(2)
                        opciones_sal = ["", "Bajo", "Moderado", "Alto", "No sabe / no identifica"]
                        payload["nut_sal"] = c_sal1.selectbox("Consumo de sal al día:", opciones_sal, index=opciones_sal.index(datos_hc.get("nut_sal", "")) if datos_hc.get("nut_sal", "") in opciones_sal else 0)
                        payload["nut_sal_obs_opcional"] = c_sal2.text_input("Observaciones sobre la sal (Opcional):", value=datos_hc.get("nut_sal_obs_opcional", ""))
                        
                        st.markdown("---")
                        c_pref1, c_pref2 = st.columns(2)
                        payload["nut_pref_si"] = c_pref1.text_area("Alimentos preferidos:", value=datos_hc.get("nut_pref_si", ""))
                        payload["nut_pref_no"] = c_pref2.text_area("Alimentos no preferidos o que evita:", value=datos_hc.get("nut_pref_no", ""))
                        
                        c_alerg1, c_alerg2 = st.columns(2)
                        payload["nut_intolerancias"] = c_alerg1.text_area("Intolerancias alimentarias referidas:", value=datos_hc.get("nut_intolerancias", ""))
                        payload["nut_alergias_alim"] = c_alerg2.text_area("Alergias alimentarias conocidas:", value=datos_hc.get("nut_alergias_alim", ""))

                        st.markdown("---")
                        c_hor1, c_hor2 = st.columns(2)
                        payload["nut_horarios"] = c_hor1.text_area("Comidas al día, Horarios y Lugares:", value=datos_hc.get("nut_horarios", ""))
                        payload["nut_frecuencia"] = c_hor2.text_area("Frecuencia (Frutas, verduras, cereales, etc.):", value=datos_hc.get("nut_frecuencia", ""))
                        payload["nut_rec24"] = st.text_area("Recordatorio de 24 horas:", value=datos_hc.get("nut_rec24", ""))

                    with st.expander("V. Actividad, VI. Emocional y VII. Sueño"):
                        payload["nut_actividad"] = st.text_area("Actividad física (Tipo, frecuencia, intensidad):", value=datos_hc.get("nut_actividad", ""))
                        payload["nut_emocional"] = st.text_area("Estado emocional (Comer por estrés, atracones, culpa):", value=datos_hc.get("nut_emocional", ""))
                        payload["nut_sueno"] = st.text_area("Calidad del sueño y horas:", value=datos_hc.get("nut_sueno", ""))

                    with st.expander("VIII. Antropometría, IX. Objetivos y X. Plan"):
                        c1, c2, c3, c4 = st.columns(4)
                        payload["nut_peso"] = c1.text_area("Peso (kg)", value=datos_hc.get("nut_peso", ""))
                        payload["nut_talla"] = c2.text_area("Estatura (cm)", value=datos_hc.get("nut_talla", ""))
                        payload["nut_imc"] = c3.text_area("IMC", value=datos_hc.get("nut_imc", ""))
                        payload["nut_grasa"] = c4.text_area("% Grasa / Músculo", value=datos_hc.get("nut_grasa", ""))
                        payload["nut_cintura"] = st.text_area("Circunferencias (Cintura, cadera, cuello, brazo):", value=datos_hc.get("nut_cintura", ""))
                        st.markdown("---")
                        payload["nut_objetivos"] = st.text_area("Objetivos del paciente:", value=datos_hc.get("nut_objetivos", ""))
                        payload["nut_plan"] = st.text_area("Plan inicial y observaciones:", value=datos_hc.get("nut_plan", ""))

                # ---------------------------------------------------------
                # 5. PLANTILLA: FISIOTERAPIA
                # ---------------------------------------------------------
                elif tipo_plantilla == "FISIOTERAPIA":
                    with st.expander("II. Motivo e III. Historia del Problema", expanded=True):
                        payload["f_motivo"] = st.text_area("Problema principal y Zona afectada:", value=datos_hc.get("f_motivo", ""))
                        payload["f_evolucion"] = st.selectbox("Tiempo de evolución:", ["", "Agudo", "Subagudo", "Crónico"], index=["", "Agudo", "Subagudo", "Crónico"].index(datos_hc.get("f_evolucion", "")))
                        payload["f_mecanismo"] = st.text_area("Inicio y Mecanismo de lesión (accidente, sobrecarga, etc.):", value=datos_hc.get("f_mecanismo", ""))
                        payload["f_tratamientos"] = st.text_area("Tratamientos previos y Estudios médicos:", value=datos_hc.get("f_tratamientos", ""))

                    with st.expander("IV. Antecedentes Médicos y V. Evaluación Funcional"):
                        payload["f_ant_medicos"] = st.text_area("Enfermedades, cirugías, medicamentos y lesiones previas:", value=datos_hc.get("f_ant_medicos", ""))
                        st.markdown("---")
                        c1, c2 = st.columns(2)
                        payload["f_dolor_eva"] = c1.text_area("Dolor (Escala EVA 0-10):", value=datos_hc.get("f_dolor_eva", ""))
                        payload["f_dolor_tipo"] = c2.text_area("Tipo de dolor (punzante, opresivo, quemante):", value=datos_hc.get("f_dolor_tipo", ""))
                        payload["f_factores"] = st.text_area("Factores que aumentan o alivian el dolor:", value=datos_hc.get("f_factores", ""))

                    with st.expander("VI. Historia familiar, evolutiva y relacional"):
                        payload["f_fam_comp"] = st.text_area("1. Composición familiar actual (¿Con quién vive?):", value=datos_hc.get("f_fam_comp", ""))
                        payload["f_fam_origen"] = st.text_area("2. Familia de origen y contexto de crianza:", value=datos_hc.get("f_fam_origen", ""))
                        payload["f_fam_relacion"] = st.text_area("3. Relación con figuras parentales o cuidadores:", value=datos_hc.get("f_fam_relacion", ""))
                        payload["f_fam_dinamica"] = st.text_area("4. Dinámica familiar durante el desarrollo:", value=datos_hc.get("f_fam_dinamica", ""))
                        payload["f_fam_socioemocional"] = st.text_area("5. Historia socioemocional y adaptación:", value=datos_hc.get("f_fam_socioemocional", ""))
                        payload["f_fam_adversidades"] = st.text_area("6. Pérdidas, separaciones y experiencias adversas:", value=datos_hc.get("f_fam_adversidades", ""))
                        payload["f_fam_ant"] = st.text_area("7. Antecedentes familiares de salud generales y/o adicciones:", value=datos_hc.get("f_fam_ant", ""))

                    with st.expander("VII. Exploración, VIII. Diagnóstico e IX. Plan"):
                        payload["f_exploracion"] = st.text_area("Inspección, Palpación, Rango de movimiento y Fuerza:", value=datos_hc.get("f_exploracion", ""))
                        payload["f_pruebas"] = st.text_area("Pruebas especiales y Limitaciones funcionales:", value=datos_hc.get("f_pruebas", ""))
                        st.markdown("---")
                        payload["f_dx"] = st.text_area("Diagnóstico fisioterapéutico:", value=datos_hc.get("f_dx", ""))
                        payload["f_plan"] = st.text_area("Objetivos, Intervenciones (manual, ejercicios, electro) y Frecuencia:", value=datos_hc.get("f_plan", ""))

                # --- BOTONES DE GUARDADO ---
                st.write("")
                st.markdown("<hr style='margin: 5px 0px;'>", unsafe_allow_html=True)
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    btn_borrador = st.form_submit_button("💾 GUARDAR BORRADOR (Editable)", use_container_width=True)
                with c_btn2:
                    btn_firmar = st.form_submit_button("🔐 FIRMAR Y SELLAR DEFINITIVAMENTE", type="primary", use_container_width=True)

            # --- LÓGICA DE VALIDACIÓN ---
            if btn_borrador:
                st.session_state.tmp_hc = payload
                st.session_state.conf_borrador = True
                st.rerun()
            
            if btn_firmar:
                campos_faltantes = []
                for k, v in payload.items():
                    if "opcional" in k.lower() or "_lista" in k.lower():
                        continue 
                    if str(v).strip() == "":
                        campos_faltantes.append(k.replace("_", " ").title())
                
                if campos_faltantes:
                    st.error(f"🚨 **NO SE PUEDE SELLAR EL EXPEDIENTE.**\n\nFaltan {len(campos_faltantes)} campos por llenar. Si no aplican, escriba 'N/A'.\nRevise todas las secciones desplegables.")
                else:
                    st.session_state.tmp_hc = payload
                    st.session_state.conf_sello = True
                    st.rerun()

        # ==========================================
        # PANTALLAS DE CONFIRMACIÓN
        # ==========================================
        elif st.session_state.conf_borrador:
            st.warning("⚠️ **ATENCIÓN:** Estás a punto de guardar los avances como **Borrador**. La Historia Clínica aún no tendrá validez legal completa. ¿Deseas continuar?")
            c1, c2 = st.columns(2)
            if c1.button("✅ SÍ, GUARDAR BORRADOR", use_container_width=True):
                payload_final = st.session_state.tmp_hc
                payload_final["bloqueado"] = False
                ref_hc.set(payload_final, merge=True)
                st.session_state.conf_borrador = False
                st.success("Borrador guardado exitosamente.")
                st.rerun()
            if c2.button("❌ CANCELAR Y REGRESAR", use_container_width=True):
                st.session_state.conf_borrador = False
                st.rerun()

        elif st.session_state.conf_sello:
            st.error("🚨 **ADVERTENCIA LEGAL:** Estás a punto de **SELLAR DEFINITIVAMENTE** la Historia Clínica. \n\nEsta acción es **IRREVERSIBLE** y el documento ya no podrá ser modificado bajo ninguna circunstancia. ¿Confirmas que todos los datos son correctos?")
            c1, c2 = st.columns(2)
            if c1.button("🔐 SÍ, ESTOY SEGURO, FIRMAR Y SELLAR", type="primary", use_container_width=True):
                payload_final = st.session_state.tmp_hc
                payload_final["bloqueado"] = True
                payload_final["firmado_por"] = st.session_state.get("nombre", "Especialista")
                payload_final["fecha_firma"] = datetime.now().strftime("%d/%m/%Y %H:%M")
                ref_hc.set(payload_final, merge=True)
                st.session_state.conf_sello = False
                st.success("Historia Clínica sellada y encriptada legalmente.")
                st.rerun()
            if c2.button("❌ CANCELAR Y REVISAR DATOS", use_container_width=True):
                st.session_state.conf_sello = False
                st.rerun()
