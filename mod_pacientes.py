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

# --- LÓGICA DE NOMENCLATURA INTELIGENTE ---
def obtener_codigo_especialidad(esp):
    esp = esp.upper()
    if "PSICOLOG" in esp: return "PSIC"
    if "PSIQUIAT" in esp: return "PSIQ"
    return esp[:3]

def generar_id_terintalia(db, especialidad, anio_elegido):
    codigo_esp = obtener_codigo_especialidad(especialidad)
    docs = db.collection("pacientes").get()
    consecutivo = len(docs) + 1
    return f"TER{anio_elegido}{codigo_esp}{consecutivo}"

def render_alta_pacientes(db):
    st.markdown("<h2 style='color: #164032; font-weight: 600; font-size: 26px; margin-bottom: 0px;'>Registro de Nuevo Paciente</h2>", unsafe_allow_html=True)
    st.caption("Complete la información por bloques para aperturar el expediente clínico.")
    st.write("")

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

        st.success("✨ ¡Expediente creado exitosamente!")
        
        with st.container(border=True):
            st.markdown(f"<h4 style='color: #E67E22; font-size: 16px;'>📄 Folio: {p_guardado['id_p']}</h4>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Paciente / Titular:** {p_guardado['nombre']}")
                st.write(f"**Edad Titular:** {edad_paciente} años")
                if p_guardado.get("nombre_tutor") != "N/A":
                    st.markdown(f"**Tutor Legal:** <span style='color:#E67E22;'>{p_guardado['nombre_tutor']}</span>", unsafe_allow_html=True)
            with c2:
                # SE MOSTRARÁ EL ESPECIALISTA ASIGNADO CLARAMENTE
                st.write(f"**Especialista asignado:** {p_guardado['med']} ({p_guardado['esp']})")
                if tipo_servicio != "N/A":
                    st.write(f"**Servicio:** {tipo_servicio} ({p_guardado['modalidad']})")

        # --- BOTONES DE DESCARGA DE FORMATOS EN BLANCO ---
        st.markdown(f"<h4 style='color: #164032; font-size: 16px; margin-top: 15px;'>🖨️ Formatos en Blanco a Imprimir: {etiqueta_legal}</h4>", unsafe_allow_html=True)
        
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

        st.markdown("---")
        if st.button("🔄 Limpiar y registrar otro paciente", use_container_width=True):
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
    # PANTALLA 1: CAPTURA DE DATOS
    # ==========================================
    if not st.session_state.confirmando_p:
        
        with st.container(border=True):
            st.markdown("<h4 style='color: #164032; font-size: 15px; margin-bottom: 5px;'>👤 Datos Personales (Titular)</h4>", unsafe_allow_html=True)
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
                st.markdown("<hr style='margin: 10px 0; border: 0; border-top: 1px dashed #ccc;'/>", unsafe_allow_html=True)
                st.markdown("<span style='color: #E67E22; font-weight: bold;'>📌 Requisito Legal: Paciente Menor de Edad</span>", unsafe_allow_html=True)
                nombre_tutor = st.text_input("Nombre Completo del Padre o Tutor Legal").upper()

        with st.container(border=True):
            st.markdown("<h4 style='color: #164032; font-size: 15px; margin-bottom: 5px;'>📞 Información de Contacto</h4>", unsafe_allow_html=True)
            f3_c1, f3_c2 = st.columns(2)
            with f3_c1: tel = st.text_input("Teléfono celular (10 dígitos)", max_chars=10)
            with f3_c2: tel_casa = st.text_input("Teléfono de casa", max_chars=10)
            
            f3_c3, f3_c4 = st.columns(2)
            with f3_c3: correo = st.text_input("Correo electrónico").lower()
            with f3_c4: dir_com = st.text_input("Domicilio completo").upper()

        with st.container(border=True):
            st.markdown("<h4 style='color: #164032; font-size: 15px; margin-bottom: 5px;'>🚨 En caso de emergencia</h4>", unsafe_allow_html=True)
            ce_c1, ce_c2, ce_c3 = st.columns(3)
            with ce_c1: ce_nombre = st.text_input("Llamar a (Nombre)").upper()
            with ce_c2: ce_parentesco = st.text_input("Parentesco").upper()
            with ce_c3: ce_tel = st.text_input("Tel. de emergencia", max_chars=10)

        with st.container(border=True):
            st.markdown("<h4 style='color: #E67E22; font-size: 15px; margin-bottom: 5px;'>🏥 Asignación Clínica</h4>", unsafe_allow_html=True)
            
            c_hist1, c_hist2 = st.columns(2)
            with c_hist1: es_historico = st.toggle("¿Es un registro histórico?")
            with c_hist2:
                anio_registro = st.number_input("Año de registro", min_value=2000, max_value=int(datetime.now().year), value=2024) if es_historico else datetime.now().year

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
                st.markdown("<hr style='margin: 10px 0; border: 0; border-top: 1px dashed #ccc;'/>", unsafe_allow_html=True)
                st.caption("📌 Detalles del Servicio Psicológico")
                col_psi1, col_psi2 = st.columns(2)
                with col_psi1:
                    # --- CANDADO DE EDAD: Quitar Infanto-Juvenil si es adulto ---
                    if not es_menor:
                        opciones_servicio = ["Individual", "De Pareja", "Familiar"]
                        index_servicio = 0 # Individual por defecto
                    else:
                        opciones_servicio = ["Individual", "Infanto-Juvenil", "De Pareja", "Familiar"]
                        index_servicio = 1 # Infanto-Juvenil por defecto
                        
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
                st.markdown("<h4 style='color: #D35400; font-size: 15px; margin-bottom: 5px;'>❤️ Datos de la Pareja</h4>", unsafe_allow_html=True)
                cp1, cp2 = st.columns(2)
                with cp1: n_pareja = st.text_input("Nombre(s) de la pareja").upper()
                with cp2: a_pareja = st.text_input("Apellido(s) de la pareja").upper()
                
                cp3, cp4 = st.columns(2)
                with cp3: f_nac_pareja = st.date_input("Nacimiento pareja", min_value=datetime(1920,1,1), max_value=datetime.now().date())
                with cp4: tel_pareja = st.text_input("Teléfono de la pareja", max_chars=10)
                
                cp5, cp6 = st.columns(2)
                with cp5: correo_pareja = st.text_input("Correo electrónico de la pareja").lower()
                with cp6: dir_pareja = st.text_input("Domicilio de la pareja (Si es diferente)").upper()
                
                # --- NUEVA SECCIÓN: EMERGENCIA PAREJA ---
                st.markdown("<h5 style='color: #D35400; font-size: 14px; margin-top: 10px;'>🚨 Contacto de Emergencia de la Pareja</h5>", unsafe_allow_html=True)
                ce_p1, ce_p2, ce_p3 = st.columns(3)
                with ce_p1: ce_nom_pareja = st.text_input("Llamar a (Emergencia Pareja)").upper()
                with ce_p2: ce_par_pareja = st.text_input("Parentesco (Emergencia Pareja)").upper()
                with ce_p3: ce_tel_pareja = st.text_input("Tel. Emergencia (Pareja)", max_chars=10)
                
                if n_pareja:
                    nombre_pareja_completo = f"{n_pareja} {a_pareja}".strip()

        elif tipo_terapia == "Familiar":
            with st.container(border=True):
                st.markdown("<h4 style='color: #2980B9; font-size: 15px; margin-bottom: 5px;'>👨‍👩‍👧 Integrantes de la Familia</h4>", unsafe_allow_html=True)
                st.caption("Ingrese a los demás participantes. El paciente principal ya está registrado arriba.")
                
                cf1, cf2 = st.columns(2)
                with cf1: fam1 = st.text_input("Nombre de Familiar 1").upper()
                with cf2: par1 = st.text_input("Parentesco 1").upper()
                
                cf3, cf4 = st.columns(2)
                with cf3: fam2 = st.text_input("Nombre de Familiar 2 (Opcional)").upper()
                with cf4: par2 = st.text_input("Parentesco 2").upper()

                if fam1: nombres_familiares.append(fam1)
                if fam2: nombres_familiares.append(fam2)

        st.write("")
        if st.button("🔍 REVISAR Y CONTINUAR", use_container_width=True):
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
                
                # --- GUARDADO EXHAUSTIVO DE LA PAREJA EN FIREBASE ---
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
                st.error("⚠️ Rellena el Nombre, Domicilio, Tutor (si es menor) y verifica que el Tel. tenga 10 dígitos.")

    # ==========================================
    # PANTALLA 2: CONFIRMACIÓN
    # ==========================================
    else:
        p = st.session_state.tmp_p
        st.info(f"✨ **Folio a generar: {p['id_p']}**")
        
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                st.write(f"**Expediente a nombre de:** {p['nombre']}")
                if p['nombre_tutor'] != "N/A":
                    st.markdown(f"**Tutor Legal:** <span style='color:#E67E22;'>{p['nombre_tutor']}</span>", unsafe_allow_html=True)
                st.write(f"**Contacto Titular:** {p['telefono']}")
            with c2:
                # Mostrar explícitamente el especialista
                st.write(f"**Especialista asignado:** {p['med']} ({p['esp']})")
                if p['tipo_terapia'] != "N/A":
                    st.write(f"**Servicio:** {p['tipo_terapia']} ({p['modalidad']})")

        st.markdown("<h4 style='color: #164032; font-size: 15px;'>¿Confirmar y Guardar en Base de Datos?</h4>", unsafe_allow_html=True)
        b1, b2 = st.columns(2)
        with b1:
            if st.button("✅ SÍ, GUARDAR PACIENTE", use_container_width=True, type="primary"):
                db.collection("pacientes").document(p['id_p']).set({
                    **p, "fecha_creacion": firestore.SERVER_TIMESTAMP
                })
                st.session_state.confirmando_p = False
                st.session_state.paciente_guardado = p 
                st.rerun()
        with b2:
            if st.button("❌ REGRESAR Y CORREGIR", use_container_width=True):
                st.session_state.confirmando_p = False
                st.rerun()