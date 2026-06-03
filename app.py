import streamlit as st
import base64
from conexion import conectar_db
import mod_especialistas, mod_pacientes, mod_expedientes

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Terintalia OS", page_icon="🏥", layout="wide")
db = conectar_db()

# --- FUNCIÓN PARA LOGO ---
def get_base64(file_path):
    try:
        with open(file_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    except: return None

def mostrar_logo(ancho="200px"):
    bin_str = get_base64("logo.png")
    if bin_str:
        st.markdown(f'''
            <div style="display: flex; justify-content: center; padding: 10px 0;">
                <img src="data:image/png;base64,{bin_str}" draggable="false" 
                     style="max-width: {ancho}; height: auto; object-fit: contain;">
            </div>''', unsafe_allow_html=True)
    else: st.markdown("<h3 style='text-align:center; color:#1E3A8A;'>🏥 TERINTALIA</h3>", unsafe_allow_html=True)

# --- CSS: REDISEÑO PREMIUM (AZUL CORPORATIVO Y CONTRASTES) ---
st.markdown("""
    <style>
    /* 1. FUENTE MODERNA */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, p, span, h1, h2, h3, label, div {
        font-family: 'Inter', sans-serif;
    }
    
    .stIconMaterial, .material-symbols-rounded, [data-testid="stIconMaterial"] {
        font-family: 'Material Symbols Rounded' !important;
    }

    /* 2. FONDO PRINCIPAL (Gris ultra claro) */
    .stApp {
        background-color: #F8FAFC; 
    }

    /* 3. SIDEBAR (Menú Lateral) - AZUL MEDIANOCHE ELEGANTE */
    [data-testid="stSidebar"] {
        background-color: #0F172A !important;
        border-right: 1px solid #1E293B !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #CBD5E1 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] b {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] [data-baseweb="radio"] div {
        color: #FFFFFF !important;
    }

    /* 4. TARJETAS / CONTENEDORES CON EFECTO CRISTAL */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #ffffff;
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
        transition: all 0.3s ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -2px rgba(0, 0, 0, 0.04) !important;
        transform: translateY(-2px);
    }

    /* 5. BOTONES PRIMARIOS (Acciones Principales) - AZUL SÓLIDO */
    button[kind="primary"] {
        background-color: #1E3A8A !important; /* Azul Marino Sólido */
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px;
        color: white !important;
        transition: all 0.3s ease !important;
    }
    button[kind="primary"]:hover {
        background-color: #1E40AF !important; /* Azul ligeramente más claro al pasar el mouse */
        transform: scale(1.02);
        box-shadow: 0 4px 10px rgba(30, 58, 138, 0.3) !important;
    }

    /* 6. BOTONES SECUNDARIOS (Borradores, etc.) - BLANCOS CON BORDE */
    .stButton > button:not([kind="primary"]), .stFormSubmitButton > button:not([kind="primary"]) {
        background-color: #FFFFFF !important;
        border: 1px solid #94A3B8 !important; 
        color: #334155 !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:not([kind="primary"]):hover, .stFormSubmitButton > button:not([kind="primary"]):hover {
        border-color: #3B82F6 !important; 
        color: #1E3A8A !important;
        background-color: #F8FAFC !important;
    }

    /* 7. BOTÓN DE CERRAR SESIÓN EN EL SIDEBAR - AZUL BRILLANTE SÓLIDO */
    [data-testid="stSidebar"] .stButton > button {
        background-color: #2563EB !important; /* Azul Brillante Sólido */
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background-color: #1D4ED8 !important; /* Azul más oscuro al hover */
        transform: translateY(-1px);
        color: white !important;
    }

    /* 8. ENTRADAS DE TEXTO Y ÁREAS DE TEXTO */
    input, div[data-baseweb="select"] > div, textarea {
        background-color: #FFFFFF !important; 
        border: 1px solid #94A3B8 !important; 
        border-radius: 8px !important;
        color: #1E293B !important; 
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.06) !important; 
    }
    input:focus, textarea:focus, div[data-baseweb="select"] > div:focus-within {
        box-shadow: 0 0 0 2px #3B82F6 !important;
        border-color: #3B82F6 !important;
    }
    
    /* 9. TÍTULOS DE LOS CAMPOS (Labels) */
    [data-testid="stTextInput"] label, [data-testid="stTextArea"] label, [data-testid="stSelectbox"] label {
        display: block !important;
        font-weight: 600 !important;
        color: #334155 !important;
        font-size: 14px !important;
        margin-bottom: 4px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE LOGIN (PANTALLA DE ACCESO PREMIUM) ---
def login():
    # CSS EXCLUSIVO PARA EL LOGIN 
    st.markdown("""
        <style>
        /* Fondo ligeramente gris/azulado para resaltar la tarjeta */
        .stApp {
            background: radial-gradient(circle at center, #F8FAFC 0%, #E2E8F0 100%);
        }
        
        /* Sombra de la tarjeta (Efecto 3D flotante) */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 16px !important;
            border: 1px solid #FFFFFF !important;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04) !important;
            background: #FFFFFF !important;
            padding: 10px !important;
        }

        /* Cajas de texto del login */
        [data-testid="stTextInput"] input {
            background-color: #F1F5F9 !important; 
            border: 1px solid #CBD5E1 !important;
            border-radius: 10px !important;
            padding: 14px 16px !important; 
            font-size: 15px !important;
            color: #0F172A !important;
            font-weight: 500 !important;
        }
        
        /* Efecto al dar clic en la caja de texto */
        [data-testid="stTextInput"] input:focus {
            background-color: #FFFFFF !important;
            border-color: #2563EB !important;
            box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.15) !important; 
        }

        /* Botón de Ingresar sólido e imponente */
        .stFormSubmitButton button {
            border-radius: 10px !important;
            padding: 6px 0px !important;
            font-size: 16px !important;
            letter-spacing: 1px;
            background-color: #1E3A8A !important; /* Azul sólido oscuro, sin degradado */
            box-shadow: 0 4px 6px -1px rgba(30, 58, 138, 0.2) !important;
            border: none !important;
            color: white !important;
            margin-top: 15px !important;
            transition: all 0.3s ease !important;
        }
        .stFormSubmitButton button:hover {
            background-color: #1E40AF !important; /* Brillo sólido al hover */
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(30, 58, 138, 0.3) !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.write("")
    st.write("")
    st.write("")
    
    mostrar_logo(ancho="220px")
    
    col1, col2, col3 = st.columns([1.5, 1, 1.5])
    
    with col2:
        with st.container(border=True):
            with st.form("form_login", clear_on_submit=False):
                st.markdown("<p style='text-align: center; color: #64748B; margin-bottom: 25px; font-weight: 500;'>Acceso Seguro al Sistema Clínico</p>", unsafe_allow_html=True)
                
                usuario = st.text_input("CORREO CORPORATIVO").lower()
                password = st.text_input("CONTRASEÑA", type="password")
                
                st.write("") 
                
                submit = st.form_submit_button("INICIAR SESIÓN", type="primary", use_container_width=True)
                
                if submit:
                    if usuario == "admin@terintalia.com" and password == "Master2026":
                        st.session_state.autenticado = True
                        st.session_state.rol = "DIRECTOR"
                        st.session_state.nombre = "DIRECTOR GENERAL"
                        st.session_state.user_id = "ADMIN"
                        st.rerun()
                    elif usuario == "recepcion@terintalia.com" and password == "Recep2026":
                        st.session_state.autenticado = True
                        st.session_state.rol = "RECEPCIONISTA"
                        st.session_state.nombre = "PERSONAL DE RECEPCIÓN"
                        st.session_state.user_id = "RECEP"
                        st.rerun()
                    else:
                        query = db.collection("especialistas").where("correo_corporativo", "==", usuario).get()
                        if query:
                            user_doc = query[0].to_dict()
                            if user_doc.get("password") == password:
                                st.session_state.autenticado = True
                                st.session_state.rol = user_doc.get("rol", "ESPECIALISTA").upper()
                                st.session_state.user_id = user_doc.get("especialista_id_interno")
                                st.session_state.nombre = user_doc.get("nombre_completo")
                                st.rerun()
                            else: 
                                st.error("Clave incorrecta.")
                        else: 
                            st.error("Usuario no registrado.")

# --- INICIO DEL SISTEMA ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    login()
else:
   # --- MENÚ LATERAL ESTRUCTURADO ---
    rol = st.session_state.rol
    
    with st.sidebar:
        mostrar_logo(ancho="160px")
        st.markdown(f"<div style='text-align:center; padding-bottom: 10px;'><b>{st.session_state.nombre}</b><br><small style='color:#3B82F6;'>{rol}</small></div>", unsafe_allow_html=True)
        
        st.markdown("### 📌 MENÚ PRINCIPAL")
        
        opciones_principales = ["📊 Dashboard (Inicio)"]
        
        if rol in ["DIRECTOR", "RECEPCIONISTA"]:
            opciones_principales += ["📝 Alta de Pacientes", "👩‍⚕️ Alta de Especialistas"]
        
        opciones_principales.append("📂 Expediente Clínico")
        opciones_principales.append("📁 Repositorio")
        
        if rol == "DIRECTOR":
            opciones_principales.append("⚙️ Gestión de Clínica")
        
        opcion = st.radio("Módulos", opciones_principales, key="menu_principal", label_visibility="collapsed")
        
        st.markdown("---")
        if st.button("🚪 CERRAR SESIÓN", key="btn_cerrar", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # --- RUTEO DE PANTALLAS ---
    if opcion == "📊 Dashboard (Inicio)":
        st.title("📊 Resumen de la Clínica")
        st.write("Visión general del estado actual de Terintalia. *(Solo lectura)*")
        
        # --- INICIO DE LA MODIFICACIÓN ---
        if rol in ["DIRECTOR", "RECEPCIONISTA"]:
            pacientes_docs = db.collection("pacientes").get()
        else:
            # Filtro para que el Especialista solo vea los suyos
            # IMPORTANTE: Cambia "medico_asignado" por el nombre exacto de tu campo en Firebase
            pacientes_docs = db.collection("pacientes").where("medico_asignado", "==", st.session_state.nombre).get()
        # --- FIN DE LA MODIFICACIÓN ---
        total_pac = len(pacientes_docs)
        pac_activos = sum(1 for p in pacientes_docs if p.to_dict().get("status") == "ACTIVO")
        pac_inactivos = total_pac - pac_activos
        
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container(border=True):
                st.metric(label="👥 Total Pacientes Registrados", value=total_pac)
        with col2:
            with st.container(border=True):
                st.metric(label="🟢 Pacientes Activos", value=pac_activos)
        with col3:
            with st.container(border=True):
                st.metric(label="⚪ Pacientes Inactivos", value=pac_inactivos)
                
        st.markdown("---")
        st.info("💡 Utiliza el menú lateral para acceder a los expedientes y gestionar la información.")

    elif opcion == "📝 Alta de Pacientes":
        mod_pacientes.render_alta_pacientes(db)

    elif opcion == "👩‍⚕️ Alta de Especialistas":
        mod_especialistas.render_alta_especialistas(db)

    elif opcion == "📂 Expediente Clínico":
        mod_expedientes.render_expedientes(db, rol, st.session_state.user_id)
        
    elif opcion == "📁 Repositorio":
        import mod_repositorio
        mod_repositorio.render_repositorio(rol)

    elif opcion == "⚙️ Gestión de Clínica":
        import mod_administracion
        mod_administracion.render_administracion(db)
