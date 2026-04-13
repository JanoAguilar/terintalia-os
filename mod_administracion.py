import streamlit as st
import pandas as pd
from datetime import datetime

# --- FUNCIÓN AUXILIAR PARA GUARDAR EL HISTORIAL ---
def registrar_cambio(db, coleccion, doc_id, accion, detalles, autor):
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db.collection(coleccion).document(doc_id).collection("historial_cambios").add({
        "fecha": fecha_actual,
        "accion": accion,
        "detalles": detalles,
        "autor": autor
    })

def render_administracion(db):
    st.markdown("<h2 style='color: #164032; font-weight: 600; font-size: 26px; margin-bottom: 0px;'>Panel de Administración</h2>", unsafe_allow_html=True)
    st.caption("Gestión central, edición de perfiles, reasignaciones y rastro de auditoría.")
    st.write("")

    tab1, tab2 = st.tabs(["👩‍⚕️ Gestión de Especialistas", "👤 Gestión de Pacientes"])
    admin_actual = st.session_state.nombre

    # ==========================================
    # OBTENER DICCIONARIO DE ESPECIALISTAS ACTIVOS
    # ==========================================
    docs_esp_activos = db.collection("especialistas").where("estatus", "==", "ACTIVO").get()
    dict_esp_por_area = {}
    
    for doc in docs_esp_activos:
        d = doc.to_dict()
        area = d.get('especialidad', '').upper()
        if area == "DIRECTOR": continue
        
        nombre_id = f"{d['nombre_completo']} ({d['especialista_id_interno']})"
        if area not in dict_esp_por_area:
            dict_esp_por_area[area] = []
        dict_esp_por_area[area].append(nombre_id)

    # ==========================================
    # PESTAÑA 1: ESPECIALISTAS (Diseño Actualizado)
    # ==========================================
    with tab1:
        st.markdown("<h4 style='color: #164032; font-size: 16px;'>Directorio de Especialistas</h4>", unsafe_allow_html=True)
        
        docs_esp = db.collection("especialistas").get()
        lista_esp = [d.to_dict() for d in docs_esp if d.to_dict().get('especialidad') != "DIRECTOR"]
        
        if not lista_esp:
            st.warning("No hay especialistas registrados.")
        else:
            df_esp = pd.DataFrame(lista_esp)
            st.dataframe(df_esp[["especialista_id_interno", "nombre_completo", "especialidad", "estatus"]], use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("<h4 style='color: #E67E22; font-size: 16px;'>🛠️ Modificar Especialista</h4>", unsafe_allow_html=True)
            
            nombres_esp = {f"{e['nombre_completo']} ({e['especialista_id_interno']})": e for e in lista_esp}
            esp_seleccionado = st.selectbox("Seleccione el Especialista a editar:", list(nombres_esp.keys()))
            
            datos_esp = nombres_esp[esp_seleccionado]
            id_interno = datos_esp['especialista_id_interno']
            estatus_actual = datos_esp.get('estatus', 'ACTIVO')

            with st.container(border=True):
                col_i, col_e = st.columns([2, 1])
                col_i.write(f"**Especialista:** {esp_seleccionado}")
                col_e.write(f"**Estatus:** `{estatus_actual}`")

                with st.expander("✏️ Editar Información y Estatus", expanded=False):
                    with st.form(f"form_edit_esp_{id_interno}"):
                        c1, c2 = st.columns(2)
                        nuevo_tel = c1.text_input("Teléfono", value=datos_esp.get("telefono", ""))
                        nuevo_estatus = c2.selectbox("Estatus en sistema", ["ACTIVO", "INACTIVO"], index=0 if estatus_actual == "ACTIVO" else 1)
                        
                        if st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
                            cambios = []
                            if nuevo_tel != datos_esp.get("telefono", ""): cambios.append(f"Teléfono: {nuevo_tel}")
                            if nuevo_estatus != estatus_actual: cambios.append(f"Estatus: {nuevo_estatus}")
                            
                            if cambios:
                                db.collection("especialistas").document(id_interno).update({
                                    "telefono": nuevo_tel,
                                    "estatus": nuevo_estatus
                                })
                                registrar_cambio(db, "especialistas", id_interno, "ACTUALIZACIÓN", " | ".join(cambios), admin_actual)
                                st.success("Datos actualizados.")
                                st.rerun()
                            else:
                                st.info("No se detectaron cambios.")

                with st.expander("📜 Ver Historial de Cambios", expanded=False):
                    historial_esp = db.collection("especialistas").document(id_interno).collection("historial_cambios").order_by("fecha", direction="DESCENDING").get()
                    if not historial_esp:
                        st.caption("No hay registros de cambios.")
                    else:
                        for h in historial_esp:
                            dat = h.to_dict()
                            st.markdown(f"<small><b>{dat['fecha']}</b> | <b>{dat['accion']}</b> por {dat['autor']}</small><br><small style='color:#666;'>{dat['detalles']}</small><hr style='margin: 5px 0px;'>", unsafe_allow_html=True)

    # ==========================================
    # PESTAÑA 2: PACIENTES (Diseño Minimalista y Full Edición)
    # ==========================================
    with tab2:
        st.markdown("<h4 style='color: #164032; font-size: 16px;'>Control General de Pacientes</h4>", unsafe_allow_html=True)
        
        docs_pac = db.collection("pacientes").get()
        lista_pac = [d.to_dict() for d in docs_pac]
        
        if not lista_pac:
            st.warning("No hay pacientes registrados.")
        else:
            df_pac = pd.DataFrame(lista_pac)
            busqueda = st.text_input("🔍 Buscar Paciente por Nombre o Folio").upper()
            if busqueda:
                df_pac = df_pac[df_pac['nombre'].str.contains(busqueda) | df_pac['id_p'].str.contains(busqueda)]
            
            st.dataframe(df_pac[["id_p", "nombre", "esp", "med", "status"]], use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown("<h4 style='color: #E67E22; font-size: 16px;'>🛠️ Edición Completa de Expediente</h4>", unsafe_allow_html=True)
            
            if not df_pac.empty:
                nombres_pac = {f"{p['nombre']} ({p['id_p']})": p for p in df_pac.to_dict('records')}
                pac_sel = st.selectbox("Seleccione un paciente para editar:", list(nombres_pac.keys()))
                
                datos_p = nombres_pac[pac_sel]
                id_paciente = datos_p['id_p']
                esp_paciente = datos_p.get('esp', '').upper()
                
                with st.expander(f"✏️ Editar Información de {datos_p.get('nombre')}", expanded=False):
                    with st.form(f"form_edit_pac_{id_paciente}"):
                        
                        # BLOQUE 1: DATOS PERSONALES
                        st.markdown("<h5 style='color: #164032;'>👤 Datos Personales</h5>", unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        n_nombre = c1.text_input("Nombre Completo", value=datos_p.get("nombre", "")).upper()
                        n_edad = c2.text_input("Edad", value=datos_p.get("edad", ""))
                        
                        c3, c4, c5 = st.columns(3)
                        n_sexo = c3.selectbox("Sexo", ["Masculino", "Femenino", "Otro"], index=["Masculino", "Femenino", "Otro"].index(datos_p.get("sexo", "Masculino")) if datos_p.get("sexo", "Masculino") in ["Masculino", "Femenino", "Otro"] else 0)
                        n_civil = c4.selectbox("Estado civil", ["Soltero(a)", "Casado(a)", "Divorciado(a)", "Viudo(a)", "Unión Libre"], index=["Soltero(a)", "Casado(a)", "Divorciado(a)", "Viudo(a)", "Unión Libre"].index(datos_p.get("estado_civil", "Soltero(a)")) if datos_p.get("estado_civil", "Soltero(a)") in ["Soltero(a)", "Casado(a)", "Divorciado(a)", "Viudo(a)", "Unión Libre"] else 0)
                        n_escolaridad = c5.text_input("Escolaridad", value=datos_p.get("escolaridad", "")).upper()

                        # BLOQUE 2: CONTACTO
                        st.markdown("<hr style='margin: 10px 0;'><h5 style='color: #164032;'>📞 Contacto y Dirección</h5>", unsafe_allow_html=True)
                        c6, c7 = st.columns(2)
                        n_tel = c6.text_input("Teléfono Celular", value=datos_p.get("telefono", ""))
                        n_tel_casa = c7.text_input("Teléfono Casa", value=datos_p.get("tel_casa", ""))
                        
                        c8, c9 = st.columns(2)
                        n_correo = c8.text_input("Correo Electrónico", value=datos_p.get("correo", "")).lower()
                        n_dir = c9.text_input("Domicilio Completo", value=datos_p.get("direccion", "")).upper()

                        # BLOQUE 3: EMERGENCIA
                        st.markdown("<hr style='margin: 10px 0;'><h5 style='color: #164032;'>🚨 Emergencia</h5>", unsafe_allow_html=True)
                        c10, c11, c12 = st.columns(3)
                        n_em_nom = c10.text_input("Llamar a", value=datos_p.get("contacto_emergencia_nom", "")).upper()
                        n_em_par = c11.text_input("Parentesco", value=datos_p.get("contacto_emergencia_par", "")).upper()
                        n_em_tel = c12.text_input("Tel. Emergencia", value=datos_p.get("contacto_emergencia_tel", ""))

                        # BLOQUE 4: ASIGNACIÓN Y ESTATUS
                        st.markdown("<hr style='margin: 10px 0;'><h5 style='color: #E67E22;'>🏥 Estatus y Reasignación</h5>", unsafe_allow_html=True)
                        c13, c14 = st.columns(2)
                        n_estatus = c13.selectbox("Estatus de Expediente", ["ACTIVO", "INACTIVO"], index=0 if datos_p.get('status') == "ACTIVO" else 1)
                        
                        # --- LÓGICA DE REASIGNACIÓN INTELIGENTE (Misma Especialidad) ---
                        medicos_compatibles = dict_esp_por_area.get(esp_paciente, [])
                        med_actual = datos_p.get("med", "")
                        
                        # Si el médico actual ya no está activo, lo agregamos a la lista visualmente para no perder la referencia
                        if med_actual and med_actual not in medicos_compatibles:
                            medicos_compatibles.insert(0, med_actual)
                            
                        index_med = medicos_compatibles.index(med_actual) if med_actual in medicos_compatibles else 0
                        
                        c14.caption(f"Especialidad del paciente: **{esp_paciente}**")
                        n_med = c14.selectbox("Reasignar Médico", medicos_compatibles, index=index_med)

                        st.write("")
                        if st.form_submit_button("💾 ACTUALIZAR EXPEDIENTE", type="primary", use_container_width=True):
                            
                            # Diccionario con lo nuevo vs lo viejo para rastrear cambios
                            nuevos_datos = {
                                "nombre": n_nombre, "edad": n_edad, "sexo": n_sexo, "estado_civil": n_civil, "escolaridad": n_escolaridad,
                                "telefono": n_tel, "tel_casa": n_tel_casa, "correo": n_correo, "direccion": n_dir,
                                "contacto_emergencia_nom": n_em_nom, "contacto_emergencia_par": n_em_par, "contacto_emergencia_tel": n_em_tel,
                                "status": n_estatus, "med": n_med
                            }
                            
                            cambios_p = []
                            for clave, valor_nuevo in nuevos_datos.items():
                                valor_viejo = datos_p.get(clave, "")
                                if str(valor_nuevo) != str(valor_viejo):
                                    cambios_p.append(f"{clave.capitalize()}: {valor_viejo} ➡️ {valor_nuevo}")

                            if cambios_p:
                                db.collection("pacientes").document(id_paciente).update(nuevos_datos)
                                detalle_cambio_p = " | ".join(cambios_p)
                                registrar_cambio(db, "pacientes", id_paciente, "ACTUALIZACIÓN DE EXPEDIENTE", detalle_cambio_p, admin_actual)
                                st.success("Expediente actualizado exitosamente.")
                                st.rerun()
                            else:
                                st.info("No se modificó ninguna información.")

                with st.expander("📜 Ver Historial de Cambios del Paciente", expanded=False):
                    historial_pac = db.collection("pacientes").document(id_paciente).collection("historial_cambios").order_by("fecha", direction="DESCENDING").get()
                    if not historial_pac:
                        st.caption("No hay registros de cambios para este paciente.")
                    else:
                        for h in historial_pac:
                            dat = h.to_dict()
                            st.markdown(f"<small><b>{dat['fecha']}</b> | <b>{dat['accion']}</b> por {dat['autor']}</small><br><small style='color:#666;'>{dat['detalles']}</small><hr style='margin: 5px 0px;'>", unsafe_allow_html=True)