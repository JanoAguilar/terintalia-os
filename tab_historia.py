import streamlit as st
import os
from datetime import datetime
from fpdf import FPDF

# =========================================================
# CONFIGURACIÓN ESPECÍFICA DE MAPEO PARA EL REPORTE PDF
# =========================================================
MAPEO_PLANTILLAS = {
    "PSICOLOGÍA ADULTOS": [
        ("II. Motivo de Consulta e III. Historia del Problema", [
            ("ad_motivo_principal", "Motivo principal de consulta"),
            ("ad_sintomas", "Síntomas actuales"),
            ("ad_expectativas", "Expectativas del paciente"),
            ("ad_inicio", "Inicio del problema"),
            ("ad_curso", "Curso o evolución"),
            ("ad_eventos", "Eventos significativos asociados"),
            ("ad_factores", "Factores desencadenantes o agravantes"),
            ("ad_impacto", "Impacto (Personal, Familiar, Social, Laboral)")
        ]),
        ("IV. Antecedentes Personales y V. Historia Familiar", [
            ("ad_ant_medicos", "Antecedentes médicos relevantes"),
            ("ad_ant_psiq", "Tratamiento psiquiátrico previo"),
            ("ad_ant_psico", "Tratamientos psicológicos previos"),
            ("ad_meds", "Medicaciones actuales"),
            ("ad_riesgo_suicida", "Intentos suicidas, autolesiones o ideación actual"),
            ("ad_sustancias", "Consumo de alcohol u otras sustancias"),
            ("ad_trauma", "Eventos traumáticos (abuso, negligencia, violencia)"),
            ("ad_fam_comp", "Composición familiar actual"),
            ("ad_fam_relacion", "Relación con figuras parentales"),
            ("ad_fam_ant", "Antecedentes familiares (salud mental, adicciones)")
        ]),
        ("VI. Funcionamiento Actual y VII. Estado Mental", [
            ("ad_sueno", "Sueño"),
            ("ad_alimentacion", "Alimentación y Apetito"),
            ("ad_fisica", "Actividad física"),
            ("ad_social", "Área social y Red de apoyo"),
            ("ad_emocional", "Autoestima y Regulación emocional"),
            ("ad_apariencia", "Apariencia y actitud"),
            ("ad_animo", "Estado de ánimo y afecto"),
            ("ad_pensamiento", "Lenguaje, pensamiento, percepción y cognición"),
            ("ad_juicio", "Juicio, introspección y signos de disociación")
        ]),
        ("VIII. Clinimetría", [
            ("ad_clinimetria", "Registro de Pruebas aplicadas (Prueba, Fecha, Resultado)")
        ]),
        ("IX. Formulación, X. Diagnóstico y XI. Plan", [
            ("ad_predisponentes", "Factores predisponentes"),
            ("ad_precipitantes", "Factores precipitantes"),
            ("ad_mantenedores", "Factores mantenedores"),
            ("f_protectores", "Factores protectores"),
            ("ad_hipotesis", "Hipótesis clínica inicial"),
            ("ad_dx", "Diagnóstico(s) DSM-5/CIE-11 y Severidad"),
            ("ad_plan", "Plan de intervención, modelos y objetivos"),
            ("ad_psiquiatria", "¿Necesidad de evaluación psiquiátrica?")
        ])
    ],
    "PSICOLOGÍA INFANTOJUVENIL": [
        ("II. Datos de Padres/Tutores e III. Motivo", [
            ("ij_padre", "Datos del Padre (Nombre, Edad, Ocupación, Tel)"),
            ("ij_madre", "Datos de la Madre (Nombre, Edad, Ocupación, Tel)"),
            ("ij_acompanante", "Persona que acompaña al menor"),
            ("ij_motivo_padres", "Motivo referido por padres o cuidadores"),
            ("ij_motivo_menor", "Motivo referido por el menor"),
            ("ij_sintomas", "Conductas/síntomas observados y tiempo de evolución"),
            ("ij_impacto", "Impacto (Familiar, Escolar, Social)")
        ]),
        ("IV. Historia y V. Perinatales/Desarrollo", [
            ("ij_hist_inicio", "Inicio del problema y eventos asociados"),
            ("ij_estrategias", "Estrategias utilizadas previamente"),
            ("ij_embarazo", "Embarazo (Planeado, complicaciones)"),
            ("ij_parto", "Parto (Natural/Cesárea, complicaciones)"),
            ("ij_desarrollo", "Desarrollo temprano (Palabras, marcha, esfínteres)"),
            ("ij_apego", "Apego temprano y cuidadores principales")
        ]),
        ("VI. Ant. Médicos y VII. Historia Familiar", [
            ("ij_medicos", "Enfermedades médicas y tratamientos actuales"),
            ("ij_psi", "Tratamientos previos y trauma"),
            ("ij_riesgos", "Intentos autolesivos / Sustancias / Trauma"),
            ("ij_fam_comp", "Composición familiar y personas con quien vive"),
            ("ij_fam_dinamica", "Relación parental y estilo de crianza"),
            ("ij_fam_ant", "Antecedentes familiares relevantes")
        ]),
        ("VIII. Funcionamiento Actual y IX. Escolar", [
            ("ij_sueno", "Sueño y Alimentación"),
            ("ij_emocional", "Regulación emocional y conducta en casa"),
            ("ij_social", "Relaciones (Hermanos, Pares) y Recreación"),
            ("ij_esc_desempeno", "Desempeño académico y conducta en aula"),
            ("ij_esc_social", "Relación con profesores y compañeros")
        ]),
        ("X. Estado Mental y XI. Clinimetría", [
            ("ij_mental", "Estado mental (Apariencia, afecto, juego)"),
            ("ij_clinimetria", "Clinimetría (Pruebas, Resultados e Interpretación)")
        ]),
        ("XII. Formulación, XIII. Diagnóstico y XIV. Plan", [
            ("ij_formulacion", "Formulación clínica (Predisponentes, protectores)"),
            ("ij_dx", "Diagnóstico DSM-5/CIE-11 y Riesgos"),
            ("ij_plan", "Plan de intervención, trabajo con padres y objetivos")
        ])
    ],
    "TERAPIA DE PAREJA": [
        ("II. Datos de Identificación de la Relación y Motivo", [
            ("p_tiempos", "Tiempo de relación / Convivencia / Hijos"),
            ("p_motivo_pareja", "Motivo principal referido por la pareja"),
            ("p_expectativas", "Expectativas del proceso terapéutico")
        ]),
        ("III. Historia y IV. Dinámica Actual", [
            ("p_historia", "Historia de la relación (Inicio, hitos significativos)"),
            ("p_fortalezas", "Fortalezas de la relación"),
            ("p_conflictos", "Principales conflictos y temas recurrentes")
        ]),
        ("V. Patrones, VI. Violencia y VII. Plan", [
            ("p_patrones", "Patrones de interacción y escalada de conflictos"),
            ("p_violencia", "Presencia de violencia (Física, Psicológica, Económica)"),
            ("p_plan", "Plan de intervención (Modelo y Frecuencia)")
        ])
    ],
    "NUTRICIÓN": [
        ("II. Motivo y III. Antecedentes Personales", [
            ("nut_motivo", "Motivo de consulta"),
            ("nut_medicos", "Antecedentes Médicos, Quirúrgicos y Familiares"),
            ("nut_alergias", "Alergias, Intolerancias y Signos físicos"),
            ("nut_meds", "Medicamentos, Suplementos, Tabaco o Drogas")
        ]),
        ("IV. Hábitos Alimenticios y Recordatorio 24h", [
            ("nut_horarios", "Comidas al día, Horarios y Lugares de consumo"),
            ("nut_pref", "Preferencias y aversiones alimentarias"),
            ("nut_frecuencia", "Frecuencia de consumo por grupos alimenticios"),
            ("nut_rec24", "Recordatorio de 24 horas completo")
        ]),
        ("V. Actividad, VI. Emocional y VII. Sueño", [
            ("nut_actividad", "Actividad física (Tipo, frecuencia, intensidad)"),
            ("nut_emocional", "Estado emocional (Comer por estrés, atracones)"),
            ("nut_sueno", "Calidad del sueño y horas de descanso")
        ]),
        ("VIII. Antropometría, IX. Objetivos y X. Plan", [
            ("nut_peso", "Peso actual (kg)"),
            ("nut_talla", "Estatura / Talla (cm)"),
            ("nut_imc", "Índice de Masa Corporal (IMC)"),
            ("nut_grasa", "% Grasa / Masa Muscular"),
            ("nut_cintura", "Circunferencias corporales"),
            ("nut_objetivos", "Objetivos del paciente"),
            ("nut_plan", "Plan nutricional inicial y observaciones")
        ])
    ],
    "FISIOTERAPIA": [
        ("II. Motivo e III. Historia del Problema", [
            ("f_motivo", "Problema principal y Zona anatómica afectada"),
            ("f_evolucion", "Tiempo de evolución (Agudo, Subagudo, Crónico)"),
            ("f_mecanismo", "Inicio y Mecanismo de lesión"),
            ("f_tratamientos", "Tratamientos previos y Estudios médicos realizados")
        ]),
        ("IV. Antecedentes y V. Evaluación Funcional", [
            ("f_ant", "Enfermedades, cirugías, medicamentos y lesiones previas"),
            ("f_dolor_eva", "Dolor reportado (Escala EVA 0-10)"),
            ("f_dolor_tipo", "Tipo de dolor (punzante, opresivo, quemante)"),
            ("f_factores", "Factores que aumentan o alivian el dolor")
        ]),
        ("VI. Exploración, VII. Diagnóstico e VIII. Plan", [
            ("f_exploracion", "Inspección, Palpación, Rango de movimiento y Fuerza"),
            ("f_pruebas", "Pruebas especiales y Limitaciones funcionales"),
            ("f_dx", "Diagnóstico fisioterapéutico"),
            ("f_plan", "Objetivos, Intervenciones (manual, ejercicio) y Frecuencia")
        ])
    ]
}

def limpiar_texto_pdf(texto):
    reemplazos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N', '¿': '', '📝': '', '🔒': '', '📋': ''
    }
    t_limpio = str(texto)
    for k, v in reemplazos.items():
        t_limpio = t_limpio.replace(k, v)
    return t_limpio.encode('latin-1', 'ignore').decode('latin-1')

# =========================================================
# FUNCIÓN: FABRICAR EL DOCUMENTO PDF CON LOGOTIPO
# =========================================================
def generar_documento_pdf(paciente, datos_hc, tipo_plantilla):
    pdf = FPDF()
    pdf.set_margins(20, 20, 20)
    pdf.add_page()
    
    # --- LOGOTIPO FLOTANTE SUPERIOR DERECHO ---
    # Coloca el archivo 'logo.png' alineado al margen derecho (ancho 30mm)
    if os.path.exists("logo.png"):
        pdf.image("logo.png", x=160, y=10, w=30)
    
    # 1. Encabezado Corporativo Principal
    pdf.set_font("helvetica", "B", 16)
    pdf.cell(w=0, h=10, txt=limpiar_texto_pdf("EXPEDIENTE CLÍNICO DIGITAL"), border=0, ln=1, align="C")
    pdf.ln(5)
    
    # 2. Apartado I: Ficha de Identificación
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(w=0, h=8, txt=limpiar_texto_pdf("I. Ficha de Identificación y Datos Generales"), border=0, ln=1)
    
    pdf.set_left_margin(25)
    pdf.set_font("helvetica", "", 10)
    
    info_general = (
        f"Nombre Completo: {paciente.get('nombre', 'N/A')}\n"
        f"Edad: {paciente.get('edad', 'N/A')} anos | Sexo: {paciente.get('sexo', 'N/A')} | Estado Civil: {paciente.get('estado_civil', 'N/A')}\n"
        f"Escolaridad: {paciente.get('escolaridad', 'N/A')} | Ocupación: {paciente.get('ocupacion', 'N/A')}\n"
        f"Teléfono Celular: {paciente.get('telefono', 'N/A')} | Teléfono Casa: {paciente.get('tel_casa', 'N/A')}\n"
        f"Correo Electrónico: {paciente.get('correo', 'N/A')}\n"
        f"Domicilio Completo: {paciente.get('direccion', 'N/A')}\n"
        f"Contacto de Emergencia: {paciente.get('contacto_emergencia_nom', 'N/A')} ({paciente.get('contacto_emergencia_par', 'N/A')}) - Tel: {paciente.get('contacto_emergencia_tel', 'N/A')}\n"
        f"Folio del Expediente: {paciente.get('id_p', 'N/A')} | Formato de Plantilla: {tipo_plantilla}"
    )
    pdf.multi_cell(w=165, h=5, txt=limpiar_texto_pdf(info_general))
    pdf.set_left_margin(20)
    pdf.ln(6)

    # 3. Apartados II en Adelante
    secciones = MAPEO_PLANTILLAS.get(tipo_plantilla, [])
    for titulo_seccion, campos in secciones:
        pdf.set_font("helvetica", "B", 12)
        pdf.cell(w=0, h=8, txt=limpiar_texto_pdf(titulo_seccion), border=0, ln=1)
        pdf.ln(1)
        
        for key, etiqueta_campo in campos:
            valor_campo = datos_hc.get(key, "")
            if not str(valor_campo).strip() and "tmp_hc" in st.session_state:
                valor_campo = st.session_state.tmp_hc.get(key, "")
            
            if not str(valor_campo).strip():
                valor_campo = "N/A"
                
            pdf.set_left_margin(25)
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(w=0, h=6, txt=limpiar_texto_pdf(f"{etiqueta_campo}:"), border=0, ln=1)
            
            pdf.set_left_margin(30)
            pdf.set_font("helvetica", "", 10)
            pdf.multi_cell(w=155, h=5, txt=limpiar_texto_pdf(valor_campo))
            pdf.ln(2)
            
        pdf.set_left_margin(20)
        pdf.ln(3)
                
    if datos_hc.get("bloqueado"):
        pdf.ln(10)
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(w=0, h=6, txt=limpiar_texto_pdf("--- DOCUMENTO FIRMADO Y SELLADO DIGITALMENTE ---"), border=0, ln=1, align="C")
        pdf.set_font("helvetica", "", 10)
        pdf.cell(w=0, h=6, txt=limpiar_texto_pdf(f"Firmado por: {datos_hc.get('firmado_por', '')}"), border=0, ln=1)
        pdf.cell(w=0, h=6, txt=limpiar_texto_pdf(f"Fecha y Hora de Cierre: {datos_hc.get('fecha_firma', '')}"), border=0, ln=1)

    salida = pdf.output(dest="S")
    if isinstance(salida, str):
        return salida.encode("latin-1")
    return bytes(salida)

# =========================================================
# RENDERIZADO PRINCIPAL DE LA PESTAÑA
# =========================================================
def render(db, paciente, id_pac):
    if 'conf_borrador' not in st.session_state: st.session_state.conf_borrador = False
    if 'conf_sello' not in st.session_state: st.session_state.conf_sello = False
    if 'tmp_hc' not in st.session_state: st.session_state.tmp_hc = {}

    ref_hc = db.collection("pacientes").document(id_pac).collection("historia_clinica").document("unica")
    doc_hc = ref_hc.get()
    
    datos_hc = doc_hc.to_dict() if doc_hc.exists else {}
    bloqueado = datos_hc.get("bloqueado", False)

    # Ruteo Inteligente de Plantillas Clínicas
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

    # --- Cabecera de Control Fija con Menú Flotante para PDF ---
    c_tit, c_pdf = st.columns([3, 1])
    with c_tit:
        st.markdown("<h3 style='color: #164032; margin-top: 0px;'>🏥 Historia Clínica</h3>", unsafe_allow_html=True)
    with c_pdf:
        # Menú flotante compacto tipo popover
        with st.popover("📥 Exportar a PDF", use_container_width=True):
            st.markdown("<span style='font-size: 14px; font-weight: bold;'>¿Confirmas la descarga?</span>", unsafe_allow_html=True)
            st.caption("Se generará el reporte clínico.")
            archivo_pdf = generar_documento_pdf(paciente, datos_hc, tipo_plantilla)
            st.download_button(
                label="✅ SÍ, DESCARGAR",
                data=archivo_pdf,
                file_name=f"Expediente_{paciente.get('nombre', 'Paciente')}.pdf",
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )

    # ==========================================
    # VISTA DE LECTURA (EXPEDIENTE SELLADO)
    # ==========================================
    if bloqueado:
        with st.expander("I. Ficha de Identificación y Datos Generales", expanded=False):
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<span style='font-size:14px;'><b>Nombre Completo:</b> {paciente.get('nombre', 'N/A')}</span>", unsafe_allow_html=True)
            c2.markdown(f"<span style='font-size:14px;'><b>Edad:</b> {paciente.get('edad', 'N/A')} años</span>", unsafe_allow_html=True)
            c3.markdown(f"<span style='font-size:14px;'><b>Sexo:</b> {paciente.get('sexo', 'N/A')}</span>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<span style='font-size:14px;'><b>Estado Civil:</b> {paciente.get('estado_civil', 'N/A')}</span>", unsafe_allow_html=True)
            c2.markdown(f"<span style='font-size:14px;'><b>Escolaridad:</b> {paciente.get('escolaridad', 'N/A')}</span>", unsafe_allow_html=True)
            c3.markdown(f"<span style='font-size:14px;'><b>Teléfono Celular:</b> {paciente.get('telefono', 'N/A')}</span>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<span style='font-size:14px;'><b>Teléfono Casa:</b> {paciente.get('tel_casa', 'N/A')}</span>", unsafe_allow_html=True)
            c2.markdown(f"<span style='font-size:14px;'><b>Correo Electrónico:</b> {paciente.get('correo', 'N/A')}</span>", unsafe_allow_html=True)
            c3.markdown(f"<span style='font-size:14px;'><b>Domicilio Completo:</b> {paciente.get('direccion', 'N/A')}</span>", unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            c1.markdown(f"<span style='font-size:14px;'><b>Llamar a:</b> {paciente.get('contacto_emergencia_nom', 'N/A')}</span>", unsafe_allow_html=True)
            c2.markdown(f"<span style='font-size:14px;'><b>Parentesco:</b> {paciente.get('contacto_emergencia_par', 'N/A')}</span>", unsafe_allow_html=True)
            c3.markdown(f"<span style='font-size:14px;'><b>Tel. Emergencia:</b> {paciente.get('contacto_emergencia_tel', 'N/A')}</span>", unsafe_allow_html=True)

        st.write("")
        st.success("🔒 **HISTORIA CLÍNICA CERRADA Y FIRMADA LEGALMENTE**")
        st.caption(f"Sellado por: {datos_hc.get('firmado_por')} el {datos_hc.get('fecha_firma')} | Formato: {tipo_plantilla}")
        
        with st.container(border=True):
            st.markdown("<h5 style='color: #164032;'>Datos Registrados en el Expediente:</h5>", unsafe_allow_html=True)
            secciones_render = MAPEO_PLANTILLAS.get(tipo_plantilla, [])
            for titulo_sec, campos in secciones_render:
                st.markdown(f"**{titulo_sec}**")
                for key, etiqueta in campos:
                    val = datos_hc.get(key, "N/A")
                    st.markdown(f" * **{etiqueta}:** {val}")

    # ==========================================
    # MODO EDICIÓN (BORRADOR ACTIVO)
    # ==========================================
    else:
        if not st.session_state.conf_borrador and not st.session_state.conf_sello:
            st.info(f"📝 **MODO EDICIÓN (Borrador) | Formato: {tipo_plantilla}**")
            st.caption("Complete todos los campos. Si una pregunta no aplica, escriba 'N/A'.")
            
            with st.form("form_hc"):
                payload = {}
                
                # =========================================================
                # APARTADO I: FICHA DE IDENTIFICACIÓN (Escala Normalizada 14px)
                # =========================================================
                with st.expander("I. Ficha de Identificación y Datos Generales", expanded=False):
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"<span style='font-size:14px;'><b>Nombre Completo:</b> {paciente.get('nombre', 'N/A')}</span>", unsafe_allow_html=True)
                    c2.markdown(f"<span style='font-size:14px;'><b>Edad:</b> {paciente.get('edad', 'N/A')} años</span>", unsafe_allow_html=True)
                    c3.markdown(f"<span style='font-size:14px;'><b>Sexo:</b> {paciente.get('sexo', 'N/A')}</span>", unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"<span style='font-size:14px;'><b>Estado Civil:</b> {paciente.get('estado_civil', 'N/A')}</span>", unsafe_allow_html=True)
                    c2.markdown(f"<span style='font-size:14px;'><b>Escolaridad:</b> {paciente.get('escolaridad', 'N/A')}</span>", unsafe_allow_html=True)
                    c3.markdown(f"<span style='font-size:14px;'><b>Teléfono Celular:</b> {paciente.get('telefono', 'N/A')}</span>", unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"<span style='font-size:14px;'><b>Teléfono Casa:</b> {paciente.get('tel_casa', 'N/A')}</span>", unsafe_allow_html=True)
                    c2.markdown(f"<span style='font-size:14px;'><b>Correo Electrónico:</b> {paciente.get('correo', 'N/A')}</span>", unsafe_allow_html=True)
                    c3.markdown(f"<span style='font-size:14px;'><b>Domicilio Completo:</b> {paciente.get('direccion', 'N/A')}</span>", unsafe_allow_html=True)
                    
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"<span style='font-size:14px;'><b>Llamar a:</b> {paciente.get('contacto_emergencia_nom', 'N/A')}</span>", unsafe_allow_html=True)
                    c2.markdown(f"<span style='font-size:14px;'><b>Parentesco:</b> {paciente.get('contacto_emergencia_par', 'N/A')}</span>", unsafe_allow_html=True)
                    c3.markdown(f"<span style='font-size:14px;'><b>Tel. Emergencia:</b> {paciente.get('contacto_emergencia_tel', 'N/A')}</span>", unsafe_allow_html=True)
                
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

                    with st.expander("IV. Antecedentes Personales y V. Historia Familiar"):
                        c1, c2 = st.columns(2)
                        payload["ad_ant_medicos"] = c1.text_area("Antecedentes médicos relevantes:", value=datos_hc.get("ad_ant_medicos", ""))
                        payload["ad_ant_psiq"] = c2.text_area("Tratamiento psiquiátrico previo:", value=datos_hc.get("ad_ant_psiq", ""))
                        c3, c4 = st.columns(2)
                        payload["ad_ant_psico"] = c3.text_area("Tratamientos psicológicos previos:", value=datos_hc.get("ad_ant_psico", ""))
                        payload["ad_meds"] = c4.text_area("Medicaciones actuales:", value=datos_hc.get("ad_meds", ""))
                        payload["ad_riesgo_suicida"] = st.text_area("Intentos suicidas, autolesiones o ideación actual:", value=datos_hc.get("ad_riesgo_suicida", ""))
                        payload["ad_sustancias"] = st.text_area("Consumo de alcohol u otras sustancias:", value=datos_hc.get("ad_sustancias", ""))
                        payload["ad_trauma"] = st.text_area("Eventos traumáticos (abuso, negligencia, violencia):", value=datos_hc.get("ad_trauma", ""))
                        st.markdown("---")
                        payload["ad_fam_comp"] = st.text_area("Composición familiar actual:", value=datos_hc.get("ad_fam_comp", ""))
                        payload["ad_fam_relacion"] = st.text_area("Relación con figuras parentales:", value=datos_hc.get("ad_fam_relacion", ""))
                        payload["ad_fam_ant"] = st.text_area("Antecedentes familiares (salud mental, adicciones):", value=datos_hc.get("ad_fam_ant", ""))

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
                        payload["f_protectores"] = c4.text_area("Factores protectores:", value=datos_hc.get("f_protectores", ""))
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
                        # AQUI ESTÁ LA MAGIA: c1. y c2. devuelven las cajas a su lugar original
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

                    with st.expander("VI. Ant. Médicos y VII. Historia Familiar"):
                        payload["ij_medicos"] = st.text_area("Enfermedades médicas y tratamientos actuales:", value=datos_hc.get("ij_medicos", ""))
                        payload["ij_psi"] = st.text_area("Tratamientos phospho/psiquiátricos previos y trauma:", value=datos_hc.get("ij_psi", ""))
                        payload["ij_riesgos"] = st.text_area("Intentos autolesivos / Sustancias / Trauma / ASI:", value=datos_hc.get("ij_riesgos", ""))
                        st.markdown("---")
                        payload["ij_fam_comp"] = st.text_area("Composición familiar y personas con quien vive:", value=datos_hc.get("ij_fam_comp", ""))
                        payload["ij_fam_dinamica"] = st.text_area("Relación parental y estilo de crianza:", value=datos_hc.get("ij_fam_dinamica", ""))
                        payload["ij_fam_ant"] = st.text_area("Antecedentes familiares (Ansiedad, Depresión, Violencia, etc.):", value=datos_hc.get("ij_fam_ant", ""))

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

                    with st.expander("V. Patrones, VI. Violencia y VII. Plan"):
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
                    with st.expander("II. Motivo y III. Antecedentes Personales", expanded=True):
                        payload["nut_motivo"] = st.text_area("Motivo de consulta:", value=datos_hc.get("nut_motivo", ""))
                        c1, c2 = st.columns(2)
                        payload["nut_medicos"] = c1.text_area("Médicos, Quirúrgicos y Familiares:", value=datos_hc.get("nut_medicos", ""))
                        payload["nut_alergias"] = c2.text_area("Alergias, Intolerancias y Signos físicos:", value=datos_hc.get("nut_alergias", ""))
                        payload["nut_meds"] = st.text_area("Medicamentos, Suplementos, Tabaco/Drogas:", value=datos_hc.get("nut_meds", ""))

                    with st.expander("IV. Hábitos Alimenticios y Recordatorio 24h"):
                        c1, c2 = st.columns(2)
                        payload["nut_horarios"] = st.text_area("Comidas al día, Horarios y Lugares:", value=datos_hc.get("nut_horarios", ""))
                        payload["nut_pref"] = c2.text_area("Preferencias y aversiones:", value=datos_hc.get("nut_pref", ""))
                        payload["nut_frecuencia"] = st.text_area("Frecuencia (Frutas, verduras, cereales, lácteos, grasas, postres):", value=datos_hc.get("nut_frecuencia", ""))
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

                    with st.expander("IV. Antecedentes y V. Evaluación Funcional"):
                        payload["f_ant"] = st.text_area("Enfermedades, cirugías, medicamentos y lesiones previas:", value=datos_hc.get("f_ant", ""))
                        st.markdown("---")
                        c1, c2 = st.columns(2)
                        payload["f_dolor_eva"] = c1.text_area("Dolor (Escala EVA 0-10):", value=datos_hc.get("f_dolor_eva", ""))
                        payload["f_dolor_tipo"] = c2.text_area("Tipo de dolor (punzante, opresivo, quemante):", value=datos_hc.get("f_dolor_tipo", ""))
                        payload["f_factores"] = st.text_area("Factores que aumentan o alivian el dolor:", value=datos_hc.get("f_factores", ""))

                    with st.expander("VI. Exploración, VII. Diagnóstico e VIII. Plan"):
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
                campos_faltantes = [k.replace("_", " ").title() for k, v in payload.items() if str(v).strip() == ""]
                if campos_faltantes:
                    st.error(f"🚨 **NO SE PUEDE SELLAR EL EXPEDIENTE.**\n\nFaltan {len(campos_faltantes)} campos por llenar. Si no aplican, escriba 'N/A'.\nRevise todas las secciones desplegables.")
                else:
                    st.session_state.tmp_hc = payload
                    st.session_state.conf_sello = True
                    st.rerun()

        # ==========================================
        # PANTALLAS DE CONFIRMACIÓN DE SISTEMA
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
