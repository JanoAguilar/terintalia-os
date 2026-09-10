import streamlit as st
import pandas as pd
from datetime import datetime
import time

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
    admin_actual = st.session_state.get("nombre", "Administrador")

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
    # PESTAÑA 1: ESPECIALISTAS
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
            
            # Exportar Especialistas
            # Al exportar el DataFrame completo, las nuevas columnas (profesion_base, poblacion, etc.) se incluyen automáticamente
            csv_esp = df_esp.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Exportar Info. Completa de Especialistas (CSV)",
                data=csv_esp,
                file_name="especialistas_completo.csv",
                mime="text/csv",
            )

            st.markdown("---")
            st.markdown("<h4 style='color: #E67E22; font-size: 16px;'>🛠️ Gestión de Especialista</h4>", unsafe_allow_html=True)
            
            nombres_esp = {f"{e['nombre_completo']} ({e['especialista_id_interno']})": e for e in lista_esp}
            esp_seleccionado = st.selectbox("Seleccione el Especialista a gestionar:", list(nombres_esp.keys()))
            
            datos_esp = nombres_esp[esp_seleccionado]
            id_interno = datos_esp['especialista_id_interno']
            estatus_actual = datos_esp.get('estatus', 'ACTIVO')

            with st.container(border=True):
                col_i, col_e = st.columns([2, 1])
                col_i.write(f"**Especialista:** {esp_seleccionado}")
                col_e.write(f"**Estatus:** `{estatus_actual}`")

                # --- 1. EDICIÓN ESPECIALISTA (AHORA CON TODOS LOS CAMPOS) ---
                with st.expander("✏️ Editar Información Completa y Estatus", expanded=False):
                    with st.form(f"form_edit_esp_{id_interno}"):
                        st.markdown("<h5 style='color: #164032;'>👤 Datos Personales y Contacto</h5>", unsafe_allow_html=True)
                        c_n1, c_n2 = st.columns(2)
                        nuevo_nombre = c_n1.text_input("Nombre Completo", value=datos_esp.get("nombre_completo", "")).upper()
                        nuevo_correo = c_n2.text_input("Correo Institucional", value=datos_esp.get("correo_corporativo", "")).lower()

                        c_t1, c_t2 = st.columns(2)
                        nuevo_tel = c_t1.text_input("Teléfono celular", value=datos_esp.get("telefono", datos_esp.get("contacto", "")))
                        nuevo_estatus = c_t2.selectbox("Estatus en sistema", ["ACTIVO", "INACTIVO"], index=0 if estatus_actual == "ACTIVO" else 1)

                        st.markdown("<hr style='margin: 10px 0;'><h5 style='color: #2980B9;'>🎓 Formación Académica</h5>", unsafe_allow_html=True)
                        c_f1, c_f2 = st.columns(2)
                        nueva_profesion = c_f1.text_input("Profesión base", value=datos_esp.get("profesion_base", "")).upper()
                        nueva_cedula = c_f2.text_input("Cédula profesional base", value=datos_esp.get("cedula_base", datos_esp.get("cedula", ""))).upper()

                        c_f3, c_f4 = st.columns(2)
                        nuevo_posgrado = c_f3.text_input("Especialidad / posgrado (Opcional)", value=datos_esp.get("posgrado", "")).upper()
                        nueva_ced_posgrado = c_f4.text_input("Cédula de posgrado (Opcional)", value=datos_esp.get("cedula_posgrado", "")).upper()

                        st.markdown("<hr style='margin: 10px 0;'><h5 style='color: #E67E22;'>🏥 Perfil Clínico</h5>", unsafe_allow_html=True)
                        c_p1, c_p2 = st.columns(2)
                        
                        area_actual = datos_esp.get("area_atencion", datos_esp.get("especialidad", "")).capitalize()
                        nueva_area = c_p1.text_input("Área de atención", value=area_actual).upper()

                        poblacion_actual = datos_esp.get("poblacion_atiende", [])
                        if isinstance(poblacion_actual, str):
                            poblacion_actual = [poblacion_actual] if poblacion_actual else []
                        
                        opciones_poblacion = ["Niños", "Adolescentes", "Adultos", "Parejas", "Familias", "Adultos Mayores"]
                        for p in poblacion_actual:
                            if p not in opciones_poblacion:
                                opciones_poblacion.append(p)
                                
                        nueva_poblacion = c_p2.multiselect("Población que atiende", opciones_poblacion, default=poblacion_actual)
                        
                        st.write("")
                        if st.form_submit_button("💾 Guardar Cambios del Especialista", type="primary", use_container_width=True):
                            
                            nuevos_datos_esp = {
                                "nombre_completo": nuevo_nombre,
                                "correo_corporativo": nuevo_correo,
                                "telefono": nuevo_tel,
                                "contacto": nuevo_tel, # Retrocompatibilidad
                                "estatus": nuevo_estatus,
                                "profesion_base": nueva_profesion,
                                "cedula_base": nueva_cedula,
                                "cedula": nueva_cedula, # Retrocompatibilidad
                                "posgrado": nuevo_posgrado,
                                "cedula_posgrado": nueva_ced_posgrado,
                                "area_atencion": nueva_area,
                                "especialidad": nueva_area, # Retrocompatibilidad
                                "poblacion_atiende": nueva_poblacion
                            }

                            cambios = []
                            for clave, valor_nuevo in nuevos_datos_esp.items():
                                # Omitimos las llaves duplicadas por retrocompatibilidad para no ensuciar el historial
                                if clave in ["contacto", "cedula", "especialidad"]: 
                                    continue
                                
                                valor_viejo = datos_esp.get(clave, [] if isinstance(valor_nuevo, list) else "")
                                
                                if isinstance(valor_nuevo, list):
                                    viejo_list = valor_viejo if isinstance(valor_viejo, list) else []
                                    if sorted(valor_nuevo) != sorted(viejo_list):
                                        cambios.append(f"{clave.replace('_', ' ').capitalize()}: {viejo_list} ➡️ {valor_nuevo}")
                                else:
                                    if str(valor_nuevo) != str(valor_viejo):
                                        cambios.append(f"{clave.replace('_', ' ').capitalize()}: {valor_viejo} ➡️ {valor_nuevo}")

                            if cambios:
                                db.collection("especialistas").document(id_interno).update(nuevos_datos_esp)
                                registrar_cambio(db, "especialistas", id_interno, "ACTUALIZACIÓN", " | ".join(cambios), admin_actual)
                                st.success("Perfil del especialista actualizado exitosamente.")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.info("No se modificó ninguna información.")

                with st.expander("📜 Ver Historial de Cambios", expanded=False):
                    historial_esp = db.collection("especialistas").document(id_interno).collection("historial_cambios").order_by("fecha", direction="DESCENDING").get()
                    if not historial_esp:
                        st.caption("No hay registros de cambios.")
                    else:
                        for h in historial_esp:
                            dat = h.to_dict()
                            st.markdown(f"<small><b>{dat['fecha']}</b> | <b>{dat['accion']}</b> por {dat['autor']}</small><br><small style='color:#666;'>{dat['detalles']}</small><hr style='margin: 5px 0px;'>", unsafe_allow_html=True)

                # --- 2. ZONA DE PELIGRO (ELIMINAR ESPECIALISTA) ---
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("⚠️ ELIMINAR ESPECIALISTA (Zona de Peligro)", expanded=False):
                    docs_pacientes = db.collection("pacientes").where("med", "==", esp_seleccionado).get()
                    cantidad_pacientes = len(docs_pacientes)

                    if cantidad_pacientes > 0:
                        st.error(f"🚨 **ACCIÓN BLOQUEADA:** Este especialista tiene **{cantidad_pacientes} pacientes** asignados actualmente.")
                        st.warning("Para poder eliminar a este especialista, **primero debes reasignar a todos sus pacientes** a otro médico desde la pestaña 'Gestión de Pacientes'.")
                    else:
                        st.error(f"Estás a punto de eliminar definitivamente el perfil de **{esp_seleccionado}**.\n\nEsta acción es **irreversible**.")
                        
                        c_del_esp1, c_del_esp2 = st.columns([2, 1])
                        with c_del_esp1:
                            clave_borrado_esp = st.text_input("Ingresa la clave de autorización para eliminar:", type="password", key=f"clave_del_esp_{id_interno}")
                        
                        with c_del_esp2:
                            st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                            if st.button("🗑️ Proceder a Eliminar", type="primary", use_container_width=True, key=f"btn_del_esp_{id_interno}"):
                                if clave_borrado_esp == "5years":
                                    with st.spinner("Eliminando especialista..."):
                                        db.collection("especialistas").document(id_interno).delete()
                                    st.success("✅ Especialista eliminado exitosamente.")
                                    time.sleep(1.5)
                                    st.rerun()
                                elif clave_borrado_esp == "":
                                    st.warning("Ingresa la clave para habilitar el borrado.")
                                else:
                                    st.error("❌ Clave de autorización incorrecta.")

    # ==========================================
    # PESTAÑA 2: PACIENTES
    # ==========================================
    with tab2:
        st.markdown("<h4 style='color: #164032; font-size: 16px;'>Control General de Pacientes</h4>", unsafe_allow_html=True)
        
        docs_pac = db.collection("pacientes").get()
        lista_pac = [d.to_dict() for d in docs_pac]
        
        if not lista_pac:
            st.warning("No hay pacientes registrados.")
        else:
            # 1. Grid Visual Resumido
            df_pac_visual = pd.DataFrame(lista_pac)
            busqueda = st.text_input("🔍 Buscar Paciente por Nombre o Folio").upper()
            if busqueda:
                df_pac_visual = df_pac_visual[df_pac_visual['nombre'].str.contains(busqueda) | df_pac_visual['id_p'].str.contains(busqueda)]
            
            st.dataframe(df_pac_visual[["id_p", "nombre", "esp", "med", "status"]], use_container_width=True, hide_index=True)
            
            # --- LÓGICA DE EXPORTACIÓN CON ESTRUCTURA EXACTA ---
            datos_exportar = []
            for p in lista_pac:
                if busqueda and (busqueda not in p.get('nombre', '').upper() and busqueda not in p.get('id_p', '').upper()):
                    continue
                
                fila_export = {
                    "NUMERO DE EXPEDIENTE": p.get("id_p", ""),
                    "ESPECIALIDAD": p.get("esp", ""),
                    "ESPECIALISTA TRATANTE": p.get("med", ""),
                    "status": p.get("status", ""),
                    "modalidad": p.get("modalidad", ""),
                    "fecha_registro": p.get("fecha_registro", ""),
                    "NOMBRE DEL PACIENTE": p.get("nombre_titular", p.get("nombre", "")),
                    "edad": p.get("edad", ""),
                    "fecha_nac": p.get("fecha_nac", ""),
                    "telefono": p.get("telefono", ""),
                    "correo": p.get("correo", ""),
                    "ocupacion": p.get("ocupacion", ""),
                    "escolaridad": p.get("escolaridad", ""),
                    "tipo_terapia": p.get("tipo_terapia", ""),
                    "nombre_tutor": p.get("nombre_tutor", ""),
                    "estado_civil": p.get("estado_civil", ""),
                    "direccion": p.get("direccion", ""),
                    "NOMBRE DEL CONTACTO DE EMERGENCIA": p.get("contacto_emergencia_nom", ""),
                    "TELEFONO DE CONTACTO DE EMERGENCIA": p.get("contacto_emergencia_tel", ""),
                    "PARENTEZCO CONTACTO DE EMERGENCIA": p.get("contacto_emergencia_par", "")
                }
                datos_exportar.append(fila_export)

            df_export = pd.DataFrame(datos_exportar)
            csv_pac = df_export.to_csv(index=False).encode('utf-8-sig')
            
            st.download_button(
                label="📥 Exportar Base de Datos de Pacientes (Formato Especial)",
                data=csv_pac,
                file_name="base_pacientes.csv",
                mime="text/csv",
            )

            st.markdown("---")
            st.markdown("<h4 style='color: #E67E22; font-size: 16px;'>🛠️ Gestión de Expediente</h4>", unsafe_allow_html=True)
            
            if not df_pac_visual.empty:
                nombres_pac = {f"{p['nombre']} ({p['id_p']})": p for p in df_pac_visual.to_dict('records')}
                pac_sel = st.selectbox("Seleccione un paciente para gestionar:", list(nombres_pac.keys()))
                
                datos_p = nombres_pac[pac_sel]
                id_paciente = datos_p['id_p']
                esp_paciente = datos_p.get('esp', '').upper()
                
                # --- 1. EDICIÓN DE INFORMACIÓN ---
                with st.expander(f"✏️ Editar Información de {datos_p.get('nombre')}", expanded=False):
                    with st.form(f"form_edit_pac_{id_paciente}"):
                        st.markdown("<h5 style='color: #164032;'>👤 Datos Personales</h5>", unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        n_nombre = c1.text_input("Nombre Completo", value=datos_p.get("nombre", "")).upper()
                        n_edad = c2.text_input("Edad", value=datos_p.get("edad", ""))
                        
                        c3, c4, c5 = st.columns(3)
                        n_sexo = c3.selectbox("Sexo", ["Masculino", "Femenino", "Otro"], index=["Masculino", "Femenino", "Otro"].index(datos_p.get("sexo", "Masculino")) if datos_p.get("sexo", "Masculino") in ["Masculino", "Femenino", "Otro"] else 0)
                        n_civil = c4.selectbox("Estado civil", ["Soltero(a)", "Casado(a)", "Divorciado(a)", "Viudo(a)", "Unión Libre"], index=["Soltero(a)", "Casado(a)", "Divorciado(a)", "Viudo(a)", "Unión Libre"].index(datos_p.get("estado_civil", "Soltero(a)")) if datos_p.get("estado_civil", "Soltero(a)") in ["Soltero(a)", "Casado(a)", "Divorciado(a)", "Viudo(a)", "Unión Libre"] else 0)
                        n_escolaridad = c5.text_input("Escolaridad", value=datos_p.get("escolaridad", "")).upper()

                        st.markdown("<hr style='margin: 10px 0;'><h5 style='color: #164032;'>📞 Contacto y Dirección</h5>", unsafe_allow_html=True)
                        c6, c7 = st.columns(2)
                        n_tel = c6.text_input("Teléfono Celular", value=datos_p.get("telefono", ""))
                        n_tel_casa = c7.text_input("Teléfono Casa", value=datos_p.get("tel_casa", ""))
                        
                        c8, c9 = st.columns(2)
                        n_correo = c8.text_input("Correo Electrónico", value=datos_p.get("correo", "")).lower()
                        n_dir = c9.text_input("Domicilio Completo", value=datos_p.get("direccion", "")).upper()

                        st.markdown("<hr style='margin: 10px 0;'><h5 style='color: #164032;'>🚨 Emergencia</h5>", unsafe_allow_html=True)
                        c10, c11, c12 = st.columns(3)
                        n_em_nom = c10.text_input("Llamar a", value=datos_p.get("contacto_emergencia_nom", "")).upper()
                        n_em_par = c11.text_input("Parentesco", value=datos_p.get("contacto_emergencia_par", "")).upper()
                        n_em_tel = c12.text_input("Tel. Emergencia", value=datos_p.get("contacto_emergencia_tel", ""))

                        st.markdown("<hr style='margin: 10px 0;'><h5 style='color: #E67E22;'>🏥 Estatus y Reasignación</h5>", unsafe_allow_html=True)
                        c13, c14 = st.columns(2)
                        n_estatus = c13.selectbox("Estatus de Expediente", ["ACTIVO", "INACTIVO"], index=0 if datos_p.get('status') == "ACTIVO" else 1)
                        
                        medicos_compatibles = dict_esp_por_area.get(esp_paciente, [])
                        med_actual = datos_p.get("med", "")
                        
                        if med_actual and med_actual not in medicos_compatibles:
                            medicos_compatibles.insert(0, med_actual)
                            
                        index_med = medicos_compatibles.index(med_actual) if med_actual in medicos_compatibles else 0
                        
                        c14.caption(f"Especialidad del paciente: **{esp_paciente}**")
                        n_med = c14.selectbox("Reasignar Médico", medicos_compatibles, index=index_med)

                        st.write("")
                        if st.form_submit_button("💾 ACTUALIZAR EXPEDIENTE", type="primary", use_container_width=True):
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
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.info("No se modificó ninguna información.")

                # --- 2. HISTORIAL DE CAMBIOS ---
                with st.expander("📜 Ver Historial de Cambios del Paciente", expanded=False):
                    historial_pac = db.collection("pacientes").document(id_paciente).collection("historial_cambios").order_by("fecha", direction="DESCENDING").get()
                    if not historial_pac:
                        st.caption("No hay registros de cambios para este paciente.")
                    else:
                        for h in historial_pac:
                            dat = h.to_dict()
                            st.markdown(f"<small><b>{dat['fecha']}</b> | <b>{dat['accion']}</b> por {dat['autor']}</small><br><small style='color:#666;'>{dat['detalles']}</small><hr style='margin: 5px 0px;'>", unsafe_allow_html=True)

                # --- 3. ZONA DE PELIGRO (ELIMINAR PACIENTE) ---
                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("⚠️ ELIMINAR EXPEDIENTE (Zona de Peligro)", expanded=False):
                    st.error(f"""
                    **🚨 ADVERTENCIA LEGAL NORMATIVA (NOM-004)**
                    
                    Estás a punto de eliminar definitivamente a **{datos_p.get('nombre')} ({id_paciente})**.
                    Las normas de salud exigen conservar los expedientes clínicos por un **mínimo de 5 años** a partir de la fecha del último acto médico.
                    
                    Si procedes, se borrará su registro de la base de datos central. **Esta acción es irreversible.**
                    """)
                    
                    c_del1, c_del2 = st.columns([2, 1])
                    with c_del1:
                        clave_borrado = st.text_input("Ingresa la clave de autorización para eliminar:", type="password", key=f"clave_del_pac_{id_paciente}")
                    
                    with c_del2:
                        st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
                        if st.button("🗑️ Proceder a Eliminar", type="primary", use_container_width=True, key=f"btn_del_pac_{id_paciente}"):
                            if clave_borrado == "5years":
                                with st.spinner("Borrando expediente de la base de datos..."):
                                    db.collection("pacientes").document(id_paciente).delete()
                                st.success(f"✅ El expediente de {datos_p.get('nombre')} ha sido eliminado.")
                                time.sleep(1.5)
                                st.rerun()
                            elif clave_borrado == "":
                                st.warning("Ingresa la clave para habilitar el borrado.")
                            else:
                                st.error("❌ Clave de autorización incorrecta.")
