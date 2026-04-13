import streamlit as st
from datetime import datetime

def render(db, id_pac, paciente=None):
    # Variables de estado para los modales
    if 'conf_borrador_n' not in st.session_state: st.session_state.conf_borrador_n = False
    if 'conf_sello_n' not in st.session_state: st.session_state.conf_sello_n = False
    if 'tmp_nota' not in st.session_state: st.session_state.tmp_nota = {}

    if paciente is None:
        doc_p = db.collection("pacientes").document(id_pac).get()
        paciente = doc_p.to_dict() if doc_p.exists else {}

    esp_upper = paciente.get("esp", "").upper()
    terapia = paciente.get("tipo_terapia", "")

    # ==========================================
    # LÓGICA DE RUTEO DE NOTAS
    # ==========================================
    opciones_notas = []
    if "FISIO" in esp_upper:
        opciones_notas = ["NOTA FISIOTERAPIA"]
    elif "NUTRI" in esp_upper:
        opciones_notas = ["NOTA NUTRICIÓN"]
    elif terapia == "De Pareja":
        opciones_notas = ["NOTA TERAPIA DE PAREJA"]
    else:
        opciones_notas = ["NOTA S.O.A.P. (Psicología)", "NOTA E.M.D.R."]

    # ==========================================
    # LECTURA DE NOTAS PREVIAS Y BORRADORES
    # ==========================================
    todas_las_notas_ref = db.collection("pacientes").document(id_pac).collection("notas_evolucion").get()
    
    notas_selladas = []
    datos_borrador = {}

    for doc in todas_las_notas_ref:
        if doc.id == "borrador_actual":
            datos_borrador = doc.to_dict()
        else:
            n_data = doc.to_dict()
            if n_data.get("estado") == "SELLADA":
                notas_selladas.append(n_data)

    # ---------------------------------------------------------
    # EL CEREBRO MATEMÁTICO: CÁLCULO DE LA SIGUIENTE SESIÓN
    # ---------------------------------------------------------
    max_sesion = 0
    tiene_evaluacion = False

    for n in notas_selladas:
        val = n.get("sesion_num", "").strip()
        if val == "Evaluación Inicial":
            tiene_evaluacion = True
        elif val.startswith("Sesión "):
            try:
                num = int(val.replace("Sesión ", ""))
                if num > max_sesion:
                    max_sesion = num
            except:
                pass
    
    # Calculamos el número que sigue matemáticamente
    if max_sesion == 0:
        sig_sesion_num = "Sesión 1"
    else:
        sig_sesion_num = f"Sesión {max_sesion + 1}"

    # Decidimos cuál debe ser la opción seleccionada por DEFECTO
    if len(notas_selladas) == 0 and not tiene_evaluacion:
        sesion_sugerida = "Evaluación Inicial"
    else:
        sesion_sugerida = sig_sesion_num

    # Construimos la lista inteligente para el menú desplegable
    lista_sesiones = []
    lista_sesiones.append(sesion_sugerida)
    
    # Agregamos "Sesión 1" si sugirió Evaluación, para darles la opción de saltársela si quieren
    if sig_sesion_num not in lista_sesiones:
        lista_sesiones.append(sig_sesion_num)
    
    if "Evaluación Inicial" not in lista_sesiones:
        lista_sesiones.append("Evaluación Inicial")

    lista_sesiones.extend(["Sesión Extraordinaria", "Sesión de Cierre", "Otra"])

    # ==========================================
    # PANTALLA PRINCIPAL: FORMULARIO DE NOTA
    # ==========================================
    if not st.session_state.conf_borrador_n and not st.session_state.conf_sello_n:
        
        expandir_formulario = True if datos_borrador else False
        
        if datos_borrador:
            titulo_expander = f"📝 CONTINUAR BORRADOR ACTIVO - {datos_borrador.get('sesion_num', '')}"
        else:
            titulo_expander = "✍️ CREAR NUEVA NOTA DE EVOLUCIÓN"

        with st.expander(titulo_expander, expanded=expandir_formulario):
            
            if datos_borrador:
                st.error("🚨 **TIENES UN BORRADOR PENDIENTE DE FIRMA.** Por favor, termina de redactarlo y séllalo legalmente para que forme parte del expediente.")

            default_tipo = datos_borrador.get("tipo_nota", opciones_notas[0])
            if default_tipo not in opciones_notas: 
                default_tipo = opciones_notas[0]

            if len(opciones_notas) > 1:
                tipo_nota = st.selectbox("Seleccione el formato de sesión a registrar:", opciones_notas, index=opciones_notas.index(default_tipo))
            else:
                tipo_nota = opciones_notas[0]
                st.info(f"Formato clínico asignado automáticamente: **{tipo_nota}**")

            st.markdown("---")

            with st.form("form_nota"):
                payload = {}
                st.caption("Complete todos los campos. Si un rubro no aplica, escriba 'N/A' o 'Sin alteraciones'. Puede expandir cualquier caja arrastrando su esquina inferior derecha.")
                
                c_ses, c_fec = st.columns(2)
                
                # Respetar la sesión guardada en el borrador, si no, usar la inteligente
                valor_guardado = datos_borrador.get("sesion_num", sesion_sugerida)
                if valor_guardado not in lista_sesiones:
                    lista_sesiones.insert(0, valor_guardado)
                
                payload["sesion_num"] = c_ses.selectbox("Tipo de Sesión (Secuencia Automática):", lista_sesiones, index=lista_sesiones.index(valor_guardado))
                
                if len(notas_selladas) == 0:
                    c_ses.caption("*(Aún no hay sesiones registradas, se sugiere Evaluación Inicial)*")
                elif max_sesion == 0:
                    c_ses.caption("*(Iniciando esquema de sesiones numeradas)*")
                else:
                    c_ses.caption(f"*(La última sesión registrada fue la Sesión {max_sesion})*")
                
                fecha_str = datos_borrador.get("fecha_sesion_str", "")
                try: 
                    default_date = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                except: 
                    default_date = datetime.today().date()
                
                fecha_obj = c_fec.date_input("Fecha de la sesión:", value=default_date)
                payload["fecha_sesion_str"] = str(fecha_obj)

                # ---------------------------------------------------------
                # 1. NOTA S.O.A.P. (Psicología)
                # ---------------------------------------------------------
                if tipo_nota == "NOTA S.O.A.P. (Psicología)":
                    st.markdown("<h5 style='color: #164032;'>S — Subjetivo (Lo que refiere el paciente)</h5>", unsafe_allow_html=True)
                    payload["s_motivo"] = st.text_area("Motivo de hoy:", value=datos_borrador.get("s_motivo", ""))
                    payload["s_cambios"] = st.text_area("Cambios desde última sesión:", value=datos_borrador.get("s_cambios", ""))
                    payload["s_sintomas"] = st.text_area("Síntomas reportados y Estado emocional:", value=datos_borrador.get("s_sintomas", ""))
                    payload["s_eventos"] = st.text_area("Eventos relevantes:", value=datos_borrador.get("s_eventos", ""))

                    st.markdown("<h5 style='color: #164032;'>O — Objetivo (Lo que observa el clínico)</h5>", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    payload["o_afecto"] = c1.text_area("Afecto y Conducta:", value=datos_borrador.get("o_afecto", ""))
                    payload["o_lenguaje"] = c2.text_area("Lenguaje y Pensamiento:", value=datos_borrador.get("o_lenguaje", ""))
                    c3, c4 = st.columns(2)
                    payload["o_regulacion"] = c3.text_area("Regulación emocional y Activación:", value=datos_borrador.get("o_regulacion", ""))
                    payload["o_riesgos"] = c4.text_area("Seguridad / Riesgos:", value=datos_borrador.get("o_riesgos", ""))

                    st.markdown("<h5 style='color: #164032;'>A — Análisis (Impresión y Avances)</h5>", unsafe_allow_html=True)
                    payload["a_hipotesis"] = st.text_area("Hipótesis clínica y Relación con formulación:", value=datos_borrador.get("a_hipotesis", ""))
                    payload["a_avances"] = st.text_area("Avances, Dificultades y Respuesta terapéutica:", value=datos_borrador.get("a_avances", ""))

                    st.markdown("<h5 style='color: #164032;'>P — Plan (Estrategia)</h5>", unsafe_allow_html=True)
                    payload["p_tecnicas"] = st.text_area("Técnicas utilizadas hoy e Intervenciones:", value=datos_borrador.get("p_tecnicas", ""))
                    payload["p_tareas"] = st.text_area("Tareas asignadas e Indicaciones:", value=datos_borrador.get("p_tareas", ""))
                    payload["p_proxima"] = st.text_area("Objetivo para la próxima sesión:", value=datos_borrador.get("p_proxima", ""))

                # ---------------------------------------------------------
                # 2. NOTA E.M.D.R.
                # ---------------------------------------------------------
                elif tipo_nota == "NOTA E.M.D.R.":
                    st.markdown("<h5 style='color: #8E44AD;'>1. Problema y 2. Blanco Trabajado</h5>", unsafe_allow_html=True)
                    payload["emdr_problema"] = st.text_area("Problema o tema abordado:", value=datos_borrador.get("emdr_problema", ""))
                    payload["emdr_blanco"] = st.text_area("Descripción del recuerdo y la Imagen más perturbadora:", value=datos_borrador.get("emdr_blanco", ""))

                    st.markdown("<h5 style='color: #8E44AD;'>3. Cogniciones y 4. Emociones</h5>", unsafe_allow_html=True)
                    c1, c2 = st.columns(2)
                    payload["emdr_cn"] = c1.text_area("Cognición Negativa (CN):", value=datos_borrador.get("emdr_cn", ""))
                    payload["emdr_cp"] = c2.text_area("Cognición Positiva (CP):", value=datos_borrador.get("emdr_cp", ""))
                    c3, c4 = st.columns(2)
                    payload["emdr_voc_ini"] = c3.text_input("VOC Inicial (0-7):", value=datos_borrador.get("emdr_voc_ini", ""))
                    payload["emdr_voc_fin"] = c4.text_input("VOC Final (0-7):", value=datos_borrador.get("emdr_voc_fin", ""))
                    payload["emdr_emociones"] = st.text_area("Emociones asociadas y Sensaciones corporales:", value=datos_borrador.get("emdr_emociones", ""))

                    st.markdown("<h5 style='color: #8E44AD;'>5. Perturbación, 6. Procesamiento y 7. Instalación</h5>", unsafe_allow_html=True)
                    c5, c6 = st.columns(2)
                    payload["emdr_sud_ini"] = c5.text_input("SUD Inicial (0-10):", value=datos_borrador.get("emdr_sud_ini", ""))
                    payload["emdr_sud_fin"] = c6.text_input("SUD Final (0-10):", value=datos_borrador.get("emdr_sud_fin", ""))
                    payload["emdr_procesamiento"] = st.text_area("Material que emergió (imágenes, recuerdos, emociones):", value=datos_borrador.get("emdr_procesamiento", ""))
                    c7, c8 = st.columns(2)
                    op_inst = ["", "Completada", "Parcial"]
                    payload["emdr_instalacion"] = c7.selectbox("Instalación de CP:", op_inst, index=op_inst.index(datos_borrador.get("emdr_instalacion", "")) if datos_borrador.get("emdr_instalacion", "") in op_inst else 0)
                    payload["emdr_escaneo"] = c8.text_input("Escaneo corporal (Sensaciones restantes):", value=datos_borrador.get("emdr_escaneo", ""))

                    st.markdown("<h5 style='color: #8E44AD;'>8. Estatus y 9. Estabilización</h5>", unsafe_allow_html=True)
                    c9, c10 = st.columns(2)
                    op_est = ["", "Completado", "Parcialmente procesado", "Pendiente"]
                    op_fin = ["", "Inestable", "Regular", "Estable", "Muy estable"]
                    payload["emdr_estatus"] = c9.selectbox("Estatus del blanco:", op_est, index=op_est.index(datos_borrador.get("emdr_estatus", "")) if datos_borrador.get("emdr_estatus", "") in op_est else 0)
                    payload["emdr_estado_fin"] = c10.selectbox("Estado final del paciente:", op_fin, index=op_fin.index(datos_borrador.get("emdr_estado_fin", "")) if datos_borrador.get("emdr_estado_fin", "") in op_fin else 0)
                    payload["emdr_ejercicio"] = st.text_area("Ejercicio de estabilización utilizado y Observaciones:", value=datos_borrador.get("emdr_ejercicio", ""))

                    st.markdown("<h5 style='color: #8E44AD;'>10. Indicaciones y 11. Reevaluación</h5>", unsafe_allow_html=True)
                    payload["emdr_indicaciones"] = st.text_area("Tareas, indicaciones y activaciones explicadas:", value=datos_borrador.get("emdr_indicaciones", ""))
                    payload["emdr_reevaluacion"] = st.text_area("Aspectos para explorar en la próxima sesión:", value=datos_borrador.get("emdr_reevaluacion", ""))

                # ---------------------------------------------------------
                # 3. NOTA TERAPIA DE PAREJA
                # ---------------------------------------------------------
                elif tipo_nota == "NOTA TERAPIA DE PAREJA":
                    st.markdown("<h5 style='color: #D35400;'>1. Tema y 2. Dinámica Observada</h5>", unsafe_allow_html=True)
                    payload["par_tema"] = st.text_area("Tema principal de la sesión:", value=datos_borrador.get("par_tema", ""))
                    c1, c2 = st.columns(2)
                    payload["par_din_a"] = c1.text_area("Conductas Integrante A:", value=datos_borrador.get("par_din_a", ""))
                    payload["par_din_b"] = c2.text_area("Conductas Integrante B:", value=datos_borrador.get("par_din_b", ""))

                    st.markdown("<h5 style='color: #D35400;'>3. Emociones Predominantes</h5>", unsafe_allow_html=True)
                    c3, c4 = st.columns(2)
                    payload["par_emo_a"] = c3.text_area("Emociones Integrante A:", value=datos_borrador.get("par_emo_a", ""))
                    payload["par_emo_b"] = c4.text_area("Emociones Integrante B:", value=datos_borrador.get("par_emo_b", ""))

                    st.markdown("<h5 style='color: #D35400;'>4. Intervenciones, 5. Cambios y 6. Tareas</h5>", unsafe_allow_html=True)
                    payload["par_intervenciones"] = st.text_area("Intervenciones del terapeuta:", value=datos_borrador.get("par_intervenciones", ""))
                    payload["par_cambios"] = st.text_area("Cambios observados durante la sesión:", value=datos_borrador.get("par_cambios", ""))
                    payload["par_tareas"] = st.text_area("Tareas terapéuticas asignadas:", value=datos_borrador.get("par_tareas", ""))

                    st.markdown("<h5 style='color: #D35400;'>7. Riesgos y 8. Plan</h5>", unsafe_allow_html=True)
                    payload["par_riesgos"] = st.text_area("Riesgos detectados (Escalada, violencia, etc.):", value=datos_borrador.get("par_riesgos", ""))
                    payload["par_plan"] = st.text_area("Plan para próxima sesión:", value=datos_borrador.get("par_plan", ""))

                # ---------------------------------------------------------
                # 4. NOTA NUTRICIÓN
                # ---------------------------------------------------------
                elif tipo_nota == "NOTA NUTRICIÓN":
                    st.markdown("<h5 style='color: #2980B9;'>S — Subjetivo y Psiconutrición</h5>", unsafe_allow_html=True)
                    payload["nut_s_cambios"] = st.text_area("Cambios, dificultades y síntomas GI reportados:", value=datos_borrador.get("nut_s_cambios", ""))
                    c1, c2 = st.columns(2)
                    op_adh = ["", "Adecuada", "Parcial", "Baja"]
                    op_res = ["", "No", "Ocasionales", "Frecuentes"]
                    payload["nut_s_adherencia"] = c1.selectbox("Adherencia al plan:", op_adh, index=op_adh.index(datos_borrador.get("nut_s_adherencia", "")) if datos_borrador.get("nut_s_adherencia", "") in op_adh else 0)
                    payload["nut_s_restriccion"] = c2.selectbox("Episodios de restricción:", op_res, index=op_res.index(datos_borrador.get("nut_s_restriccion", "")) if datos_borrador.get("nut_s_restriccion", "") in op_res else 0)
                    c3, c4 = st.columns(2)
                    op_emo = ["", "No", "Leve", "Moderada", "Alta"]
                    payload["nut_s_atracon"] = c3.selectbox("Episodios de sobreingesta/atracón:", op_res, index=op_res.index(datos_borrador.get("nut_s_atracon", "")) if datos_borrador.get("nut_s_atracon", "") in op_res else 0)
                    payload["nut_s_emocional"] = c4.selectbox("Alimentación emocional:", op_emo, index=op_emo.index(datos_borrador.get("nut_s_emocional", "")) if datos_borrador.get("nut_s_emocional", "") in op_emo else 0)
                    payload["nut_s_activadores"] = st.text_area("Situaciones que activan la conducta alimentaria:", value=datos_borrador.get("nut_s_activadores", ""))

                    st.markdown("<h5 style='color: #2980B9;'>O — Objetivo y A — Análisis</h5>", unsafe_allow_html=True)
                    c5, c6 = st.columns(2)
                    payload["nut_o_peso_imc"] = c5.text_input("Peso y IMC actual:", value=datos_borrador.get("nut_o_peso_imc", ""))
                    payload["nut_o_medidas"] = c6.text_input("Medidas antropométricas relevantes:", value=datos_borrador.get("nut_o_medidas", ""))
                    payload["nut_o_obs"] = st.text_area("Observaciones clínicas y Cambios vs consulta previa:", value=datos_borrador.get("nut_o_obs", ""))
                    payload["nut_a_analisis"] = st.text_area("Interpretación del progreso y factores emocionales asociados:", value=datos_borrador.get("nut_a_analisis", ""))

                    st.markdown("<h5 style='color: #2980B9;'>P — Plan</h5>", unsafe_allow_html=True)
                    payload["nut_p_ajustes"] = st.text_area("Ajustes al plan y Educación nutricional:", value=datos_borrador.get("nut_p_ajustes", ""))
                    payload["nut_p_estrategias"] = st.text_area("Estrategias conductuales y Objetivos para el siguiente periodo:", value=datos_borrador.get("nut_p_estrategias", ""))
                    op_psi = ["", "No", "Sugerida", "Ya se encuentra en terapia"]
                    payload["nut_p_psicologia"] = st.selectbox("Necesidad de intervención psicológica:", op_psi, index=op_psi.index(datos_borrador.get("nut_p_psicologia", "")) if datos_borrador.get("nut_p_psicologia", "") in op_psi else 0)

                # ---------------------------------------------------------
                # 5. NOTA FISIOTERAPIA
                # ---------------------------------------------------------
                elif tipo_nota == "NOTA FISIOTERAPIA":
                    st.markdown("<h5 style='color: #E67E22;'>S — Subjetivo</h5>", unsafe_allow_html=True)
                    payload["fis_s_cambios"] = st.text_area("Cambios referidos por el paciente:", value=datos_borrador.get("fis_s_cambios", ""))
                    payload["fis_s_dolor"] = st.text_input("Dolor actual (EVA 0-10):", value=datos_borrador.get("fis_s_dolor", ""))

                    st.markdown("<h5 style='color: #E67E22;'>O — Objetivo y A — Análisis</h5>", unsafe_allow_html=True)
                    payload["fis_o_hallazgos"] = st.text_area("Hallazgos (Rango mov., fuerza, inflamación, tolerancia):", value=datos_borrador.get("fis_o_hallazgos", ""))
                    payload["fis_a_analisis"] = st.text_area("Interpretación clínica del progreso:", value=datos_borrador.get("fis_a_analisis", ""))

                    st.markdown("<h5 style='color: #E67E22;'>P — Plan</h5>", unsafe_allow_html=True)
                    payload["fis_p_intervencion"] = st.text_area("Intervención realizada (Manual, ejercicios, electro, etc.):", value=datos_borrador.get("fis_p_intervencion", ""))
                    payload["fis_p_indicaciones"] = st.text_area("Indicaciones para casa y Plan próxima sesión:", value=datos_borrador.get("fis_p_indicaciones", ""))

                # --- BOTONES DE ACCIÓN ---
                st.write("")
                st.markdown("<hr style='margin: 5px 0px;'>", unsafe_allow_html=True)
                cb1, cb2 = st.columns(2)
                with cb1:
                    btn_borrador = st.form_submit_button("💾 GUARDAR COMO BORRADOR", use_container_width=True)
                with cb2:
                    btn_firmar = st.form_submit_button("🔐 FIRMAR Y SELLAR NOTA", type="primary", use_container_width=True)

            # --- PROCESAMIENTO DE BOTONES ---
            if btn_borrador:
                st.session_state.tmp_nota = payload
                st.session_state.tmp_nota["tipo_nota"] = tipo_nota
                st.session_state.conf_borrador_n = True
                st.rerun()

            if btn_firmar:
                num_sesion = payload["sesion_num"].strip()
                # Candado Anti-Duplicados
                duplicado = False
                for n_data in notas_selladas:
                    if n_data.get("sesion_num", "").strip() == num_sesion:
                        # Ignoramos si es una sesión comodín, bloqueamos si es "Sesión X"
                        if num_sesion.startswith("Sesión"):
                            duplicado = True
                            break
                
                if duplicado:
                    st.error(f"🚨 **Sesión Duplicada:** Ya existe una nota sellada con el identificador '{num_sesion}'.")
                else:
                    campos_faltantes = [k.replace("_", " ").title() for k, v in payload.items() if str(v).strip() == ""]
                    if campos_faltantes:
                        st.error(f"🚨 **No se puede sellar la nota.** Faltan {len(campos_faltantes)} campos por llenar. Escriba 'N/A' en los que no apliquen.")
                    else:
                        st.session_state.tmp_nota = payload
                        st.session_state.tmp_nota["tipo_nota"] = tipo_nota
                        st.session_state.conf_sello_n = True
                        st.rerun()

    # ==========================================
    # PANTALLAS DE CONFIRMACIÓN
    # ==========================================
    elif st.session_state.conf_borrador_n:
        st.warning("⚠️ **ATENCIÓN:** Estás a punto de guardar esta nota como **Borrador**. La nota aún no tendrá validez legal y podrás seguir editándola después. ¿Deseas continuar?")
        c1, c2 = st.columns(2)
        if c1.button("✅ SÍ, GUARDAR BORRADOR", use_container_width=True):
            payload_final = st.session_state.tmp_nota
            payload_final["estado"] = "BORRADOR"
            
            db.collection("pacientes").document(id_pac).collection("notas_evolucion").document("borrador_actual").set(payload_final)
            st.session_state.conf_borrador_n = False
            st.success("Borrador guardado exitosamente.")
            st.rerun()
        if c2.button("❌ CANCELAR Y REGRESAR", use_container_width=True):
            st.session_state.conf_borrador_n = False
            st.rerun()

    elif st.session_state.conf_sello_n:
        st.error("🚨 **ADVERTENCIA LEGAL:** Estás a punto de **SELLAR DEFINITIVAMENTE** esta Nota Clínica. \n\nEsta acción es **IRREVERSIBLE** y el documento quedará anexado al historial del paciente sin posibilidad de modificación futura. ¿Confirmas que los datos son correctos?")
        c1, c2 = st.columns(2)
        if c1.button("🔐 SÍ, ESTOY SEGURO, FIRMAR Y SELLAR", type="primary", use_container_width=True):
            payload_final = st.session_state.tmp_nota
            payload_final["estado"] = "SELLADA"
            payload_final["fecha_sistema"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            payload_final["autor"] = st.session_state.get("nombre", "Especialista")
            
            db.collection("pacientes").document(id_pac).collection("notas_evolucion").add(payload_final)
            db.collection("pacientes").document(id_pac).collection("notas_evolucion").document("borrador_actual").delete()
            
            st.session_state.conf_sello_n = False
            st.success("Nota sellada y encriptada legalmente.")
            st.rerun()
        if c2.button("❌ CANCELAR Y REVISAR DATOS", use_container_width=True):
            st.session_state.conf_sello_n = False
            st.rerun()

    # ==========================================
    # SECCIÓN: HISTORIAL DE NOTAS (Solo Selladas)
    # ==========================================
    st.markdown("<h4 style='color: #E67E22; font-size: 16px; margin-top: 15px;'>📜 Historial de Notas de Evolución</h4>", unsafe_allow_html=True)
    
    notas_selladas.sort(key=lambda x: x.get("fecha_sistema", ""), reverse=True)
    
    if not notas_selladas:
        st.info("No hay notas previas registradas en este expediente.")
    else:
        for n in notas_selladas:
            tipo = n.get("tipo_nota", "Nota Clínica")
            sesion = n.get("sesion_num", "S/N")
            fecha = n.get("fecha_sesion_str", n.get("fecha_sistema", "")[:10])
            autor = n.get("autor", "Especialista")

            with st.expander(f"📅 {fecha} | {sesion} | {tipo} | 👨‍⚕️ {autor}"):
                st.caption(f"Sellada en sistema el: {n.get('fecha_sistema', '')}")
                
                if tipo == "NOTA S.O.A.P. (Psicología)":
                    st.markdown(f"**S:** Motivo: {n.get('s_motivo','')} | Síntomas: {n.get('s_sintomas','')} | Eventos: {n.get('s_eventos','')}")
                    st.markdown(f"**O:** Afecto: {n.get('o_afecto','')} | Lenguaje: {n.get('o_lenguaje','')} | Regulación: {n.get('o_regulacion','')} | Riesgos: {n.get('o_riesgos','')}")
                    st.markdown(f"**A:** Hipótesis: {n.get('a_hipotesis','')} | Avances: {n.get('a_avances','')}")
                    st.markdown(f"**P:** Técnicas: {n.get('p_tecnicas','')} | Tareas: {n.get('p_tareas','')} | Próxima: {n.get('p_proxima','')}")
                
                elif tipo == "NOTA E.M.D.R.":
                    st.markdown(f"**Blanco:** {n.get('emdr_problema','')} - {n.get('emdr_blanco','')}")
                    st.markdown(f"**Cogniciones:** CN: {n.get('emdr_cn','')} | CP: {n.get('emdr_cp','')} (VOC {n.get('emdr_voc_ini','')} ➔ {n.get('emdr_voc_fin','')})")
                    st.markdown(f"**SUD:** {n.get('emdr_sud_ini','')} ➔ {n.get('emdr_sud_fin','')} | **Emociones:** {n.get('emdr_emociones','')}")
                    st.markdown(f"**Procesamiento:** {n.get('emdr_procesamiento','')}")
                    st.markdown(f"**Cierre:** Estatus: {n.get('emdr_estatus','')} | Estado: {n.get('emdr_estado_fin','')} | Estabilización: {n.get('emdr_ejercicio','')}")
                
                elif tipo == "NOTA TERAPIA DE PAREJA":
                    st.markdown(f"**Tema:** {n.get('par_tema','')}")
                    st.markdown(f"**Dinámica/Emociones:** Int A: {n.get('par_din_a','')} ({n.get('par_emo_a','')}) | Int B: {n.get('par_din_b','')} ({n.get('par_emo_b','')})")
                    st.markdown(f"**Intervenciones/Cambios:** {n.get('par_intervenciones','')} | {n.get('par_cambios','')}")
                    st.markdown(f"**Plan/Riesgos:** Tareas: {n.get('par_tareas','')} | Próxima: {n.get('par_plan','')} | Riesgos: {n.get('par_riesgos','')}")
                
                elif tipo == "NOTA NUTRICIÓN":
                    st.markdown(f"**S:** Cambios: {n.get('nut_s_cambios','')} | Adherencia: {n.get('nut_s_adherencia','')} | Restricción/Atracón: {n.get('nut_s_restriccion','')} / {n.get('nut_s_atracon','')}")
                    st.markdown(f"**O:** Peso/IMC: {n.get('nut_o_peso_imc','')} | Medidas: {n.get('nut_o_medidas','')} | Obs: {n.get('nut_o_obs','')}")
                    st.markdown(f"**A:** Interpretación: {n.get('nut_a_analisis','')}")
                    st.markdown(f"**P:** Ajustes: {n.get('nut_p_ajustes','')} | Objetivos: {n.get('nut_p_estrategias','')} | Apoyo Psi: {n.get('nut_p_psicologia','')}")

                elif tipo == "NOTA FISIOTERAPIA":
                    st.markdown(f"**S:** Cambios: {n.get('fis_s_cambios','')} | EVA: {n.get('fis_s_dolor','')}")
                    st.markdown(f"**O:** Hallazgos: {n.get('fis_o_hallazgos','')}")
                    st.markdown(f"**A:** Análisis: {n.get('fis_a_analisis','')}")
                    st.markdown(f"**P:** Intervención: {n.get('fis_p_intervencion','')} | Indicaciones: {n.get('fis_p_indicaciones','')}")