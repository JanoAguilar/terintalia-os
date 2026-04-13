import streamlit as st
import os
from datetime import datetime

def render(db, id_pac):
    # Asegurarnos de que exista la carpeta para guardar los archivos físicos
    CARPETA_PACIENTES = "archivos_pacientes"
    if not os.path.exists(CARPETA_PACIENTES):
        os.makedirs(CARPETA_PACIENTES)

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
        
        # --- NUEVO BOTÓN DE ADJUNTO PARA LA PRUEBA ---
        st.markdown("<h5 style='font-size: 14px; color: #334155; margin-top: 10px;'>📎 Evidencia Documental (Opcional)</h5>", unsafe_allow_html=True)
        st.caption("Si cuenta con el protocolo calificado, el dibujo del paciente o el reporte en PDF, puede anexarlo aquí.")
        archivo_eval = st.file_uploader("Sube el PDF o Imagen de la prueba", type=["pdf", "jpg", "png", "jpeg"], label_visibility="collapsed")
        
        st.write("")
        if st.form_submit_button("🔐 REGISTRAR Y SELLAR EVALUACIÓN", type="primary", use_container_width=True):
            if tipo_prueba and interpretacion:
                
                ruta_archivo = ""
                nombre_archivo = ""
                
                # Si el terapeuta subió un archivo, lo guardamos en la carpeta local
                if archivo_eval:
                    nombre_archivo = archivo_eval.name
                    # Le ponemos la hora al nombre para que no se sobreescriban archivos con el mismo nombre
                    ruta_archivo = os.path.join(CARPETA_PACIENTES, f"{id_pac}_eval_{datetime.now().strftime('%H%M%S')}_{nombre_archivo}")
                    with open(ruta_archivo, "wb") as f:
                        f.write(archivo_eval.getbuffer())
                
                db.collection("pacientes").document(id_pac).collection("evaluaciones").add({
                    "prueba": tipo_prueba,
                    "fecha_ap": str(fecha_aplicacion),
                    "puntuacion": puntuacion,
                    "interpretacion": interpretacion,
                    "archivo_nombre": nombre_archivo,
                    "archivo_ruta": ruta_archivo,
                    "registrado_por": st.session_state.get("nombre", "Especialista"),
                    "fecha_sello": datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                st.success("Evaluación registrada permanentemente.")
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
            with st.container(border=True):
                # Dividimos en 2 columnas: 80% para texto, 20% para el botón de descarga
                c_info, c_desc = st.columns([4, 1])
                with c_info:
                    st.markdown(f"<h5 style='color: #2563EB; margin-bottom: 0;'>📊 {ev.get('prueba', '')}</h5>", unsafe_allow_html=True)
                    st.caption(f"Aplicada el: {ev.get('fecha_ap', '')} | Sellada por {ev.get('registrado_por', '')} el {ev.get('fecha_sello', '')}")
                    st.write(f"**Puntuación:** {ev.get('puntuacion', 'N/A')}")
                    st.write(f"**Interpretación:** {ev.get('interpretacion', '')}")
                
                with c_desc:
                    ruta = ev.get('archivo_ruta', '')
                    if ruta and os.path.exists(ruta):
                        with open(ruta, "rb") as f:
                            st.download_button("📥 Descargar Prueba", f, file_name=ev.get('archivo_nombre', 'prueba.pdf'), key=f"dwn_ev_{e.id}", use_container_width=True)
                    elif ruta:
                        st.error("Archivo físico no encontrado.")