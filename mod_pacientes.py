import streamlit as st
import os
from datetime import datetime
from google.cloud import firestore

# --- FUNCIÓN AUXILIAR PARA DESCARGAR PDFs DESDE LA CARPETA ---
def boton_descarga_pdf(nombre_archivo, etiqueta_boton, nombre_salida):
    ruta_archivo = os.path.join("documentos_legales", nombre_archivo)
    if os.path.exists(ruta_archivo):
        with open(ruta_archivo, "rb") as pdf_file:
            st.download_button(
                label=f"✅ {etiqueta_boton}",
                data=pdf_file,
                file_name=nombre_salida,
                mime="application/pdf",
                use_container_width=True,
                type="primary"
            )
    else:
        st.button(f"⚠️ Falta archivo en carpeta: {nombre_archivo}", use_container_width=True, disabled=True)

# --- CABECERA ESTILIZADA DE PASO (WIZARD) ---
def cabecera_paso(num, titulo, subtitulo, color_bg="#EFF6FF", color_txt="#1D4ED8"):
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid #F1F5F9;">
            <div style="background: {color_bg}; color: {color_txt}; font-weight: 800; font-size: 13px; padding: 6px 12px; border-radius: 10px; letter-spacing: 0.5px; font-family: 'Plus Jakarta Sans', sans-serif;">
                PASO {num}
            </div>
            <div>
                <div style="font-size: 16px; font-weight: 800; color: #0F172A; font-family: 'Plus Jakarta Sans', sans-serif;">{titulo}</div>
                <div style="font-size: 12.5px; color: #64748B;">{subtitulo}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- LÓGICA DE NOMENCLATURA INTELIGENTE ---
def obtener_codigo_especialidad(esp):
    esp = esp.upper()
    if "PSICOLOG" in esp: return "PSIC"
    if "PSIQUIAT" in esp: return "PSIQ"
    return esp[:3]

def generar_id_terintalia(db, especialidad, anio_elegido):
    codigo_esp = obtener_codigo_especialidad(especialidad)
    prefijo = f"TER{anio_elegido}{codigo_esp}"
    
    docs = db.collection("pacientes").get()
    max_consecutivo = 0
    
    for doc in docs:
        id_pac = doc.to_dict().get("id_p", "")
        if id_pac.startswith(prefijo):
            try:
                num = int(id_pac.replace(prefijo, ""))
                if num > max_consecutivo:
                    max_consecutivo = num
            except ValueError:
                pass
                
    consecutivo = max_consecutivo + 1
    return f"{prefijo}{consecutivo}"

def render_alta_pacientes(db):
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <span style="background: #EFF6FF; color: #1D4ED8; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 999px; letter-spacing: 0.6px; text-transform: uppercase;">Admisión Clínica</span>
            <h2 style="color: #0F172A; font-weight: 800; font-size: 26px; margin: 6px 0 2px 0;">📝 Registro de Nuevo Paciente</h2>
            <p style="color: #64748B; font-size: 13.5px; margin: 0;">Complete los pasos secuenciales para aperturar el expediente digital y generar el paquete legal.</p>
        </div>
    """, unsafe_allow_html=True)

    if 'confirmando_p' not in st.session_state:
        st.session_state.confirmando_p = False
    if 'paciente_guardado' not in st.session_state:
        st.session_state.paciente_guardado = None

    # ==========================================
    # PANTALLA DE ÉXITO Y PAQUETE LEGAL
    # ==========================================
    if st.session_state.paciente_guardado:
        p_guardado = st.session_state.paciente_guardado
        
        edad_paciente = int(p_guardado['edad'])
        es_adulto = edad_paciente >= 18
        tipo_servicio = p_guardado.get("tipo_terapia", "N/A")
        es_pareja = (tipo_servicio == "De Pareja")
        es_familiar = (tipo_servicio == "Familiar")

        if es_pareja:
            etiqueta_legal = "TERAPIA DE PAREJA"
        elif es_familiar:
            etiqueta_legal = "TERAPIA FAMILIAR"
        else:
            etiqueta_legal = "ADULTO (Mayor de 18 años)" if es_adulto else "INFANTO JUVENIL (Menor de edad)"

        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #059669 0%, #10B981 100%); border-radius: 18px; padding: 24px 28px; color: white; margin-bottom: 20px; box-shadow: 0 10px 25px -5px rgba(16, 185, 129, 0.35); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
                <div>
                    <span style="background: rgba(255,255,255,0.2); color: #FFFFFF; font-size: 11px; font-weight: 700; padding: 4px 12px; border-radius: 999px; letter-spacing: 0.6px;">✨ EXPEDIENTE APERTURADO</span>
                    <h3 style="color: #FFFFFF !important; margin: 8px 0 2px 0; font-size: 22px;">{p_guardado['nombre']}</h3>
                    <p style="color: #D1FAE5 !important; margin: 0; font-size: 13.5px;">Especialista: <b>{p_guardado['med']}</b> • Inicio: {p_guardado.get('fecha_inicio_tratamiento', 'N/A')}</p>
                </div>
                <div style="background: rgba(255,255,255,0.15); border: 1px solid rgba(255,255,255,0.3); border-radius: 14px; padding: 10px 18px; text-align: right;">
                    <div style="font-size: 11px; color: #D1FAE5; text-transform: uppercase;">Folio Asignado</div>
                    <div style="font-size: 20px; font-weight: 800; color: #FFFFFF;">{p_guardado['id_p']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown(f"<h4 style='color: #0F172A; font-size: 16px; margin-bottom: 12px;'>🖨️ Paquete Legal en Blanco a Imprimir: <span style='color:#2563EB;'>{etiqueta_legal}</span></h4>", unsafe_allow_html=True)
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                boton_descarga_pdf("CARATULA DATOS GENERALES.pdf", "1. Carátula Datos Generales", "Caratula_Vacia.pdf")
                if es_pareja:
                    boton_descarga_pdf("CONSENTIMIENTO INFORMADO – TERAPIA DE PAREJA.pdf", "2. Consentimiento de Pareja", "Consentimiento_Pareja.pdf")
                elif es_familiar:
                    boton_descarga_pdf("CONSENTIMIENTO INFORMADO GENERAL.pdf", "2. Consentimiento Familiar", "Consentimiento_Familiar.pdf")
                else:
                    boton_descarga_pdf("CONSENTIMIENTO INFORMADO GENERAL.pdf", "2. Consentimiento Informado", "Consentimiento_General.pdf")

            with col_btn2:
                if es_pareja:
                    boton_descarga_pdf("CONTRATO – TERAPIA DE PAREJA.pdf", "3. Contrato de Pareja", "Contrato_Pareja.pdf")
                elif es_familiar:
                    boton_descarga_pdf("CONTRATO TERAPEÚTICO ADULTOS.pdf", "3. Contrato Familiar", "Contrato_Familiar.pdf")
                elif es_adulto:
                    boton_descarga_pdf("CONTRATO TERAPEÚTICO ADULTOS.pdf", "3. Contrato Adulto", "Contrato_Adulto.pdf")
                else:
                    boton_descarga_pdf("CONTRATO TERAPÉUTICO INFANTOJUVENIL.pdf", "3. Contrato Infanto-Juvenil", "Contrato_IJ.pdf")
                
                boton_descarga_pdf("AVISO DE PRIVACIDAD.pdf", "4. Aviso de Privacidad", "Aviso_Privacidad.pdf")

        st.write("")
        if st.button("🔄 Limpiar formulario y registrar otro paciente", use_container_width=True):
            st.session_state.paciente_guardado = None
            st.rerun()
        return

    # ==========================================
    # OBTENER ESPECIALISTAS
    # ==========================================
    esp_docs = db.collection("especialistas").where("estatus", "==", "ACTIVO").get()
    dict_esp = {}
    for doc in esp_docs:
        d = doc.to_dict()
        area = d.get('especialidad', '').upper()
        if area == "DIRECTOR": continue
        nombre_id = f"{d['nombre_completo']} ({d['especialista_id_interno']})"
        if area not in dict_esp: dict_esp[area] = []
        dict_esp[area].append(nombre_id)

    # ==========================================
    # PANTALLA 1: CAPTURA DE DATOS (WIZARD)
    # ==========================================
    if not st.session_state.confirmando_p:
        
        with st.container(border=True):
            cabecera_paso("01", "Datos Personales del Titular", "Identificación demográfica básica y validación de mayoría de edad.")
            f1_c1, f1_c2 = st.columns(2)
            with f1_c1: nombre = st.text_input("Nombre(s)").upper()
            with f1_c2: apellido = st.text_input("Apellido(s)").upper()

            f2_c1, f2_c2, f2_c3 = st.columns([2, 1, 1])
            with f2_c1: 
                f_nac = st.date_input("Fecha de nacimiento", min_value=datetime(1920,1,1), max_value=datetime.now().date())
            with f2_c2: 
                hoy = datetime.now().date()
                edad_calculada = hoy.year - f_nac.year - ((hoy.month, hoy.day) < (f_nac.month, f_nac.day))
                st.text_input("Edad", value=f"{edad_calculada} años", disabled=True)
                edad = str(edad_calculada)
                es_menor = edad_calculada < 18

            with f2_c3: 
                sexo_opc = st.selectbox("Sexo", ["Masculino", "Femenino", "Otro"])
                sexo_manual = st.text_input("Especifique").upper() if sexo_opc == "Otro" else ""

            f_dem1, f_dem2, f_dem3 = st.columns(3)
            with f_dem1: estado_civil = st.selectbox("Estado civil", ["Soltero(a)", "Casado(a)", "Divorciado(a)", "Viudo(a)", "Unión Libre"])
            with f_dem2: escolaridad = st.selectbox("Escolaridad", ["Ninguna", "Primaria", "Secundaria", "Bachillerato", "Licenciatura", "Postgrado"])
            with f_dem3: ocupacion = st.text_input("Ocupación").upper()

            nombre_tutor = "N/A"
            if es_menor:
                st.markdown("<hr style='margin: 12px 0; border: 0; border-top: 1px dashed #CBD5E1;'/>", unsafe_allow_html=True)
                st.markdown("<span style='color: #EA580C; font-weight: 700; font-size: 13.5px;'>📌 Requisito Legal Obligatorio: Paciente Menor de Edad</span>", unsafe_allow_html=True)
                nombre_tutor = st.text_input("Nombre Completo del Padre, Madre o Tutor Legal").upper()

        with st.container(border=True):
            cabecera_paso("02", "Información de Contacto y Domicilio", "Medios de localización oficial del paciente titular.", "#ECFDF5", "#059669")
            f3_c1, f3_c2 = st.columns(2)
            with f3_c1: tel = st.text_input("Teléfono celular (10 dígitos)", max_chars=10)
            with f3_c2: tel_casa = st.text_input("Teléfono de casa / fijo", max_chars=10)
            
            f3_c3, f3_c4 = st.columns(2)
            with f3_c3: correo = st.text_input("Correo electrónico").lower()
            with f3_c4: dir_com = st.text_input("Domicilio completo").upper()

        with st.container(border=True):
            cabecera_paso("03", "Contacto de Emergencia", "Persona de referencia inmediata en caso de eventualidad médica.", "#FEF2F2", "#DC2626")
            ce_c1, ce_c2, ce_c3 = st.columns(3)
            with ce_c1: ce_nombre = st.text_input("Llamar a (Nombre Completo)").upper()
            with ce_c2: ce_parentesco = st.text_input("Parentesco").upper()
            with ce_c3: ce_tel = st.text_input("Tel. de emergencia (10 dígitos)", max_chars=10)

        with st.container(border=True):
            cabecera_paso("04", "Asignación Clínica y Folio", "Definición de área médica, especialista tratante y fecha de inicio.", "#FFF7ED", "#EA580C")
            
            c_hist1, c_hist2, c_hist3 = st.columns(3)
            with c_hist1: 
                es_historico = st.toggle("¿Es un registro histórico?")
            with c_hist2:
                anio_actual = datetime.now().year
                anio_registro = st.number_input("Año del registro (Folio)", min_value=2000, max_value=anio_actual, value=anio_actual, disabled=not es_historico)
            with c_hist3:
                fecha_inicio_tratamiento = st.date_input("Fecha de inicio de tratamiento", value=datetime.now().date())

            f4_c1, f4_c2 = st.columns(2)
            with f4_c1:
                areas_disponibles = sorted(list(dict_esp.keys()))
                index_psicologia = 0
                for i, area in enumerate(areas_disponibles):
                    if "PSICOLOG" in area.upper():
                        index_psicologia = i
                        break
                area_sel = st.selectbox("Especialidad requerida", areas_disponibles if areas_disponibles else ["Sin Especialidades"], index=index_psicologia)
                
            with f4_c2:
                nombres = dict_esp.get(area_sel, ["No Disponible"])
                esp_asig = st.selectbox("Especialista asignado", nombres)

            tipo_terapia = "N/A"
            modalidad = "N/A"
            
            if "PSICOLOG" in area_sel.upper():
                st.markdown("<hr style='margin: 12px 0; border: 0; border-top: 1px dashed #CBD5E1;'/>", unsafe_allow_html=True)
                st.caption("📌 Configuración del Servicio Psicológico")
                col_psi1, col_psi2 = st.columns(2)
                with col_psi1:
                    if not es_menor:
                        opciones_servicio = ["Individual", "De Pareja", "Familiar"]
                        index_servicio = 0
                    else:
                        opciones_servicio = ["Individual", "Infanto-Juvenil", "De Pareja", "Familiar"]
                        index_servicio = 1
                        
                    tipo_terapia = st.selectbox("Tipo de Servicio", opciones_servicio, index=index_servicio)
                with col_psi2:
                    modalidad = st.selectbox("Modalidad de atención", ["Presencial", "Híbrido", "Online"])

        # ==========================================
        # BLOQUES DINÁMICOS: PAREJA Y FAMILIA
        # ==========================================
        nombre_pareja_completo = ""
        nombres_familiares = []

        if tipo_terapia == "De Pareja":
            with st.container(border=True):
                cabecera_paso("05", "Datos del Segundo Integrante (Pareja)", "Información complementaria para el expediente mancomunado.", "#FCE7F3", "#DB2777")
                cp1, cp2 = st.columns(2)
                with cp1: n_pareja = st.text_input("Nombre(s) de la pareja").upper()
                with cp2: a_pareja = st.text_input("Apellido(s) de la pareja").upper()
                
                cp3, cp4 = st.columns(2)
                with cp3: f_nac_pareja = st.date_input("Nacimiento pareja", min_value=datetime(1920,1,1), max_value=datetime.now().date())
                with cp4: tel_pareja = st.text_input("Teléfono de la pareja", max_chars=10)
                
                cp5, cp6 = st.columns(2)
                with cp5: correo_pareja = st.text_input("Correo electrónico de la pareja").lower()
                with cp6: dir_pareja = st.text_input("Domicilio de la pareja (Si es diferente)").upper()
                
                st.markdown("<h5 style='color: #DB2777; font-size: 13.5px; margin-top: 12px;'>🚨 Contacto de Emergencia de la Pareja</h5>", unsafe_allow_html=True)
                ce_p1, ce_p2, ce_p3 = st.columns(3)
                with ce_p1: ce_nom_pareja = st.text_input("Llamar a (Emergencia Pareja)").upper()
                with ce_p2: ce_par_pareja = st.text_input("Parentesco (Emergencia Pareja)").upper()
                with ce_p3: ce_tel_pareja = st.text_input("Tel. Emergencia (Pareja)", max_chars=10)
                
                if n_pareja:
                    nombre_pareja_completo = f"{n_pareja} {a_pareja}".strip()

        elif tipo_terapia == "Familiar":
            with st.container(border=True):
                cabecera_paso("05", "Integrantes Adicionales de la Familia", "Ingrese a los demás participantes. El titular ya quedó registrado en el Paso 01.", "#F3E8FF", "#7C3AED")
                cf1, cf2 = st.columns(2)
                with cf1: fam1 = st.text_input("Nombre de Familiar 1").upper()
                with cf2: par1 = st.text_input("Parentesco 1").upper()
                
                cf3, cf4 = st.columns(2)
                with cf3: fam2 = st.text_input("Nombre de Familiar 2 (Opcional)").upper()
                with cf4: par2 = st.text_input("Parentesco 2").upper()

                if fam1: nombres_familiares.append(fam1)
                if fam2: nombres_familiares.append(fam2)

        st.write("")
        if st.button("🔍 REVISAR DATOS Y PREVISUALIZAR FOLIO →", type="primary", use_container_width=True):
            if nombre and tel and dir_com and len(tel) == 10 and (not es_menor or nombre_tutor):
                
                nombre_base = f"{nombre} {apellido}".strip()
                nombre_expediente = nombre_base
                
                if tipo_terapia == "De Pareja" and nombre_pareja_completo:
                    nombre_expediente = f"{nombre_base} Y {nombre_pareja_completo}"
                elif tipo_terapia == "Familiar" and nombres_familiares:
                    nombres_unidos = ", ".join(nombres_familiares)
                    nombre_expediente = f"FAMILIA: {nombre_base}, {nombres_unidos}"

                st.session_state.tmp_p = {
                    "id_p": generar_id_terintalia(db, area_sel, anio_registro),
                    "nombre": nombre_expediente, 
                    "nombre_titular": nombre_base, 
                    "fecha_registro": datetime.now().strftime("%d/%m/%Y"),
                    "fecha_inicio_tratamiento": str(fecha_inicio_tratamiento),
                    "f_nac": str(f_nac),
                    "fecha_nac": f_nac.strftime("%d/%m/%Y"), 
                    "edad": edad,
                    "sexo": sexo_manual if sexo_opc == "Otro" else sexo_opc,
                    "estado_civil": estado_civil,
                    "escolaridad": escolaridad,
                    "ocupacion": ocupacion,
                    "nombre_tutor": nombre_tutor,
                    "telefono": tel,
                    "tel_casa": tel_casa,
                    "correo": correo,
                    "direccion": dir_com,
                    "contacto_emergencia_nom": ce_nombre,
                    "contacto_emergencia_par": ce_parentesco,
                    "contacto_emergencia_tel": ce_tel,
                    "esp": area_sel,
                    "med": esp_asig,
                    "tipo_terapia": tipo_terapia,
                    "modalidad": modalidad,
                    "anio": anio_registro,
                    "status": "ACTIVO"
                }
                
                if tipo_terapia == "De Pareja":
                    st.session_state.tmp_p["pareja_nombre"] = nombre_pareja_completo
                    st.session_state.tmp_p["pareja_fecha_nac"] = str(f_nac_pareja)
                    st.session_state.tmp_p["pareja_telefono"] = tel_pareja
                    st.session_state.tmp_p["pareja_correo"] = correo_pareja
                    st.session_state.tmp_p["pareja_direccion"] = dir_pareja
                    st.session_state.tmp_p["pareja_emergencia_nom"] = ce_nom_pareja
                    st.session_state.tmp_p["pareja_emergencia_par"] = ce_par_pareja
                    st.session_state.tmp_p["pareja_emergencia_tel"] = ce_tel_pareja
                elif tipo_terapia == "Familiar":
                    st.session_state.tmp_p["familia_nombres"] = nombres_familiares
                
                st.session_state.confirmando_p = True
                st.rerun()
            else:
                st.error("⚠️ Rellena el Nombre, Domicilio, Tutor (si es menor) y verifica que el Teléfono celular tenga exactamente 10 dígitos.")

    # ==========================================
    # PANTALLA 2: CONFIRMACIÓN EJECUTIVA
    # ==========================================
    else:
        p = st.session_state.tmp_p
        
        st.markdown(f"""
            <div style="background: #EFF6FF; border: 1px solid #BFDBFE; border-radius: 16px; padding: 20px 24px; margin-bottom: 18px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
                <div>
                    <div style="font-size: 12px; font-weight: 700; color: #1D4ED8; text-transform: uppercase;">Verificación Previa al Guardado</div>
                    <div style="font-size: 20px; font-weight: 800; color: #0F172A; margin-top: 2px;">{p['nombre']}</div>
                </div>
                <div style="background: #FFFFFF; border: 1px solid #93C5FD; padding: 8px 16px; border-radius: 12px; text-align: right;">
                    <div style="font-size: 10.5px; color: #64748B; font-weight: 700; text-transform: uppercase;">Folio Consecutivo a Generar</div>
                    <div style="font-size: 18px; font-weight: 800; color: #EA580C;">📄 {p['id_p']}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Titular:** {p['nombre_titular']} ({p['edad']} años)")
                if p['nombre_tutor'] != "N/A":
                    st.markdown(f"**Tutor Legal:** <span style='color:#EA580C; font-weight:700;'>{p['nombre_tutor']}</span>", unsafe_allow_html=True)
                st.write(f"**Teléfono Celular:** {p['telefono']}")
                st.write(f"**Domicilio:** {p['direccion']}")
            with c2:
                st.write(f"**Especialidad:** {p['esp']}")
                st.write(f"**Especialista Asignado:** {p['med']}")
                if p['tipo_terapia'] != "N/A":
                    st.write(f"**Servicio:** {p['tipo_terapia']} ({p['modalidad']})")
                st.write(f"**Inicio de Tratamiento:** {p['fecha_inicio_tratamiento']}")

        st.write("")
        b1, b2 = st.columns(2)
        with b1:
            if st.button("✅ CONFIRMAR Y CREAR EXPEDIENTE", use_container_width=True, type="primary"):
                db.collection("pacientes").document(p['id_p']).set({
                    **p, "fecha_creacion": firestore.SERVER_TIMESTAMP
                })
                st.session_state.confirmando_p = False
                st.session_state.paciente_guardado = p 
                st.rerun()
        with b2:
            if st.button("⬅️ REGRESAR Y CORREGIR DATOS", use_container_width=True):
                st.session_state.confirmando_p = False
                st.rerun()
