import streamlit as st
import os
from datetime import datetime, timedelta
import time
from firebase_admin import storage

# =========================================================
# MODAL SOLO PARA IMÁGENES (FIREBASE STORAGE)
# =========================================================
@st.dialog("Visor de Pruebas y Evidencias", width="large")
def modal_visualizador_url(url, tipo_archivo, descripcion):
    st.markdown(f"**Evaluación:** {descripcion}")
    st.markdown("---")
    st.image(url, use_container_width=True)
    if st.button("Cerrar Visor", use_container_width=True):
        st.rerun()

# =========================================================
# RENDERIZADO PRINCIPAL
# =========================================================
def render(db, id_pac):
    st.markdown("<h4 style='color: #1E3A8A; font-size: 16px;'>Registro de Pruebas y Evaluaciones (Clinimetría)</h4>", unsafe_allow_html=True)
    
    with st.form("form_eval", clear_on_submit=True):
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            tipo_prueba = st.selectbox("Instrumento Aplicado", [
                "Inventario de Evaluación de la Personalidad (PAI)",
                "Escala de Experiencias Disociativas (DES)",
                "Cociente de Espectro Autista (AQ)",
                "Escala de Conners Revisada (CRS)",
                "Test del Dibujo de la Figura Humana (DFH)",
                "Escala de Inteligencia (WAIS / WISC)",
                "Otra (Especificar)"
            ])
            if tipo_prueba == "Otra (Especificar)":
                tipo_prueba = st.text_input("Nombre de la prueba").upper()
        with col_t2:
            fecha_aplicacion = st.date_input("Fecha de Aplicación")
        
        puntuacion = st.text_input("Puntuación Obtenida (Opcional)")
        interpretacion = st.text_area("Interpretación Clínica / Resultados")
        
        # --- NUEVO ADJUNTO CON INSTRUCCIONES EXACTAS ---
        st.markdown("<h5 style='font-size: 14px; color: #334155; margin-top: 10px;'>📎 Evidencia Documental (Opcional)</h5>", unsafe_allow_html=True)
        
        # Mensaje flotante corregido y exacto
        st.info("💡 **¿Cómo adjuntar?** Selecciona tu archivo en el recuadro de abajo. El documento se subirá a la nube cuando presiones el botón de abajo que dice **'🔐 REGISTRAR EVALUACIÓN Y SUBIR EVIDENCIA'**.")
        
        archivo_eval = st.file_uploader("📂 Seleccionar PDF o Imagen (Max. 10 MB)", type=["pdf", "jpg", "png", "jpeg"])
        
        st.write("")
        if st.form_submit_button("🔐 REGISTRAR EVALUACIÓN Y SUBIR EVIDENCIA", type="primary", use_container_width=True):
            if tipo_prueba and interpretacion:
                
                nombre_archivo = ""
                storage_path = ""
                tipo_archivo = ""
                
                if archivo_eval:
                    if archivo_eval.size > 10 * 1024 * 1024:
                        st.error("🚨 ARCHIVO MUY PESADO: El límite actual es de 10 MB. No se guardó la evaluación.")
                        st.stop()
                    else:
                        with st.spinner("Subiendo evidencia al disco duro de Firebase Storage..."):
                            bucket = storage.bucket()
                            storage_path = f"evaluaciones/{id_pac}/{int(time.time())}_{archivo_eval.name}"
                            blob = bucket.blob(storage_path)
                            blob.upload_from_string(archivo_eval.getvalue(), content_type=archivo_eval.type)
                            nombre_archivo = archivo_eval.name
                            tipo_archivo = archivo_eval.type
                
                datos_evaluacion = {
                    "prueba": tipo_prueba,
                    "fecha_ap": str(fecha_aplicacion),
                    "puntuacion": puntuacion,
                    "interpretacion": interpretacion,
                    "archivo_nombre": nombre_archivo,
                    "registrado_por": st.session_state.get("nombre", "Especialista"),
                    "fecha_sello": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                
                if storage_path:
                    datos_evaluacion["storage_path"] = storage_path
                    datos_evaluacion["tipo"] = tipo_archivo
                
                db.collection("pacientes").document(id_pac).collection("evaluaciones").add(datos_evaluacion)
                
                st.toast("✅ ¡Evaluación y evidencia selladas exitosamente!", icon="🎉")
                time.sleep(1.5)
                st.rerun()
            else:
                st.error("El nombre de la prueba y la interpretación son obligatorios.")

    # --- HISTORIAL DE EVALUACIONES ---
    st.markdown("---")
    evals = db.collection("pacientes").document(id_pac).collection("evaluaciones").order_by("fecha_sello", direction="DESCENDING").get()
    
    if not evals:
        st.info("No hay evaluaciones registradas.")
    else:
        for e in evals:
            ev = e.to_dict()
            doc_id = e.id
            
            with st.container(border=True):
                tiene_archivo = "storage_path" in ev or "archivo_ruta" in ev
                
                if tiene_archivo:
                    c_info, c_vis, c_desc = st.columns([2.5, 1, 1])
                else:
                    c_info = st.columns([1])[0]
                
                with c_info:
                    st.markdown(f"<h5 style='color: #2563EB; margin-bottom: 0;'>📊 {ev.get('prueba', '')}</h5>", unsafe_allow_html=True)
                    st.caption(f"Aplicada el: {ev.get('fecha_ap', '')} | Sellada por {ev.get('registrado_por', '')} el {ev.get('fecha_sello', '')}")
                    st.write(f"**Puntuación:** {ev.get('puntuacion', 'N/A')}")
                    st.write(f"**Interpretación:** {ev.get('interpretacion', '')}")
                    if ev.get('archivo_nombre'):
                        st.caption(f"📎 Adjunto: `{ev.get('archivo_nombre')}`")
                
                if tiene_archivo:
                    if "storage_path" in ev:
                        ruta_blob = ev.get("storage_path")
                        tipo_archivo = ev.get("tipo", "application/pdf")
                        
                        try:
                            bucket = storage.bucket()
                            blob = bucket.blob(ruta_blob)
                            url_segura = blob.generate_signed_url(version="v4", expiration=timedelta(minutes=60), method="GET", response_disposition="inline")
                            
                            with c_vis:
                                if "pdf" in tipo_archivo:
                                    btn_pdf = f'''
                                    <a href="{url_segura}" target="_blank" style="
                                        display: block; text-align: center; background-color: #FFFFFF; 
                                        padding: 6px 0px; border: 1px solid #94A3B8; border-radius: 8px; 
                                        text-decoration: none; color: #334155; font-size: 14px; font-weight: 600; margin-top: 25px;">
                                        👁️ Abrir PDF
                                    </a>
                                    '''
                                    st.markdown(btn_pdf, unsafe_allow_html=True)
                                else:
                                    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
                                    if st.button("👁️ Visualizar", key=f"vis_ev_{doc_id}", use_container_width=True):
                                        modal_visualizador_url(url_segura, tipo_archivo, ev.get("prueba", ""))
                            
                            with c_desc:
                                btn_descarga = f'''
                                <a href="{url_segura}" target="_blank" download style="
                                    display: block; text-align: center; background-color: #FFFFFF; 
                                    padding: 6px 0px; border: 1px solid #94A3B8; border-radius: 8px; 
                                    text-decoration: none; color: #334155; font-size: 14px; font-weight: 600; margin-top: 25px;">
                                    ⬇️ Descargar
                                </a>
                                '''
                                st.markdown(btn_descarga, unsafe_allow_html=True)
                        
                        except Exception as ex:
                            with c_vis:
                                st.error("Error URL")
                            with c_desc:
                                st.error("No disponible")
                                
                    elif "archivo_ruta" in ev:
                        ruta = ev.get("archivo_ruta")
                        with c_vis:
                            st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
                            st.button("👁️ N/A", key=f"vis_ev_err_{doc_id}", disabled=True, use_container_width=True, help="Archivos locales no admiten previsualización")
                            
                        with c_desc:
                            st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
                            if ruta and os.path.exists(ruta):
                                with open(ruta, "rb") as f:
                                    st.download_button("📥 Descargar", f, file_name=ev.get('archivo_nombre', 'prueba.pdf'), key=f"dwn_ev_leg_{doc_id}", use_container_width=True)
                            else:
                                st.error("No encontrado")
