import streamlit as st
import base64
from datetime import datetime
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
    except:
        return None

def mostrar_logo(ancho="200px"):
    bin_str = get_base64("logo.png")
    if bin_str:
        st.markdown(f'''
            <div style="display: flex; justify-content: center; padding: 12px 0;">
                <img src="data:image/png;base64,{bin_str}" draggable="false" 
                     style="max-width: {ancho}; height: auto; object-fit: contain; filter: drop-shadow(0 4px 6px rgba(0,0,0,0.05));">
            </div>''', unsafe_allow_html=True)
    else:
        st.markdown("<h3 style='text-align:center; color:#1E3A8A; font-weight:800; letter-spacing:-0.5px;'>🏥 TERINTALIA OS</h3>", unsafe_allow_html=True)

# =========================================================
# MOTOR GRÁFICO CSS: DISEÑO ULTRA-PREMIUM SAAS MÉDICO
# =========================================================
st.markdown("""
    <style>
    /* 1. TIPOGRAFÍA MODERNA DUAL */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');
    
    html, body, p, span, label, div {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    h1, h2, h3, h4, h5 {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        letter-spacing: -0.02em;
    }
    .stIconMaterial, .material-symbols-rounded, [data-testid="stIconMaterial"] {
        font-family: 'Material Symbols Rounded' !important;
    }

    /* SCROLLBARS ESTILIZADAS TIPO MACOS/SAAS */
    ::-webkit-scrollbar {
        width: 7px;
        height: 7px;
    }
    ::-webkit-scrollbar-track {
        background: #F1F5F9;
    }
    ::-webkit-scrollbar-thumb {
        background: #CBD5E1;
        border-radius: 999px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #94A3B8;
    }

    /* OCULTAR ELEMENTOS NATIVOS DE STREAMLIT PARA ASPECTO DE WEB APP */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background: transparent !important;}

    /* 2. FONDO PRINCIPAL CON LUZ AMBIENTAL SUTIL */
    .stApp {
        background-color: #F4F7FB;
        background-image: 
            radial-gradient(at 0% 0%, rgba(37, 99, 235, 0.05) 0px, transparent 45%),
            radial-gradient(at 100% 0%, rgba(16, 185, 129, 0.05) 0px, transparent 45%);
    }

    /* ANIMACIÓN SUAVE AL CARGAR CONTENIDO */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        animation: fadeInPage 0.35s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes fadeInPage {
        from { opacity: 0; transform: translateY(6px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* 3. SIDEBAR (MENÚ LATERAL) - ESTILO NAVEGACIÓN APP MODERNA */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B1120 0%, #0F172A 60%, #131F38 100%) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.07) !important;
        box-shadow: 4px 0 24px rgba(0, 0, 0, 0.12) !important;
    }
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #94A3B8 !important;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] b {
        color: #F8FAFC !important;
    }

    /* Transformar Radio Buttons del Sidebar en Botones de Menú Interactivos */
    [data-testid="stSidebar"] [role="radiogroup"] {
        gap: 6px !important;
        padding-top: 4px;
    }
    [data-testid="stSidebar"] [data-baseweb="radio"] {
        background-color: rgba(255, 255, 255, 0.02) !important;
        border: 1px solid rgba(255, 255, 255, 0.04) !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
        margin: 0 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        width: 100% !important;
    }
    [data-testid="stSidebar"] [data-baseweb="radio"] > div:first-child {
        display: none !important;
    }
    [data-testid="stSidebar"] [data-baseweb="radio"]:hover {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(255, 255, 255, 0.12) !important;
        transform: translateX(4px);
    }
    [data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) {
        background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
        border-color: #3B82F6 !important;
        box-shadow: 0 6px 16px -3px rgba(37, 99, 235, 0.45) !important;
    }
    [data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) p,
    [data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) span,
    [data-testid="stSidebar"] [data-baseweb="radio"]:has(input:checked) div {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }

    /* 4. TARJETAS / CONTENEDORES CON ELEVACIÓN DINÁMICA */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #FFFFFF !important;
        border-radius: 16px !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 12px -2px rgba(15, 23, 42, 0.04), 0 2px 6px -1px rgba(15, 23, 42, 0.02) !important;
        padding: 18px !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #CBD5E1 !important;
        box-shadow: 0 12px 24px -6px rgba(15, 23, 42, 0.08), 0 4px 10px -2px rgba(15, 23, 42, 0.03) !important;
    }

    /* 5. PESTAÑAS (TABS) ESTILO PÍLDORA FLOTANTE (SEGMENTED CONTROL) */
    [data-baseweb="tab-list"] {
        background-color: #E2E8F0 !important;
        padding: 6px !important;
        border-radius: 14px !important;
        gap: 6px !important;
        border-bottom: none !important;
        margin-bottom: 18px !important;
    }
    [data-baseweb="tab"] {
        border-radius: 10px !important;
        padding: 10px 18px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        color: #475569 !important;
        border: none !important;
        background-color: transparent !important;
        transition: all 0.2s ease !important;
    }
    [data-baseweb="tab"]:hover {
        color: #0F172A !important;
        background-color: rgba(255, 255, 255, 0.5) !important;
    }
    [data-baseweb="tab"][aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #1E3A8A !important;
        box-shadow: 0 4px 10px rgba(15, 23, 42, 0.08) !important;
    }
    [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* 6. ACORDEONES (EXPANDERS) MODERNOS */
    [data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 14px !important;
        box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03) !important;
        overflow: hidden !important;
        margin-bottom: 10px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stExpander"]:hover {
        border-color: #CBD5E1 !important;
        box-shadow: 0 6px 12px rgba(15, 23, 42, 0.05) !important;
    }
    [data-testid="stExpander"] details summary {
        padding: 14px 18px !important;
        background-color: #F8FAFC !important;
        font-weight: 600 !important;
        color: #1E293B !important;
        border-bottom: 1px solid transparent;
    }
    [data-testid="stExpander"] details[open] summary {
        background-color: #F1F5F9 !important;
        border-bottom: 1px solid #E2E8F0 !important;
        color: #1E3A8A !important;
    }

    /* 7. BOTONES PRIMARIOS Y SECUNDARIOS CON DEGRADADO Y MICRO-INTERACCIÓN */
    button[kind="primary"] {
        background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px;
        color: white !important;
        padding: 0.55rem 1.2rem !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.22) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #3B82F6 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(37, 99, 235, 0.32) !important;
    }
    button[kind="primary"]:active {
        transform: translateY(0px);
    }

    .stButton > button:not([kind="primary"]), .stFormSubmitButton > button:not([kind="primary"]) {
        background-color: #FFFFFF !important;
        border: 1px solid #CBD5E1 !important; 
        color: #334155 !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        padding: 0.55rem 1.2rem !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:not([kind="primary"]):hover, .stFormSubmitButton > button:not([kind="primary"]):hover {
        border-color: #3B82F6 !important; 
        color: #1E3A8A !important;
        background-color: #F8FAFC !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.1) !important;
    }

    /* BOTÓN DE CERRAR SESIÓN EN EL SIDEBAR */
    [data-testid="stSidebar"] .stButton > button {
        background: rgba(239, 68, 68, 0.12) !important;
        color: #FCA5A5 !important;
        border: 1px solid rgba(239, 68, 68, 0.25) !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: #EF4444 !important;
        border-color: #EF4444 !important;
        color: #FFFFFF !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 14px rgba(239, 68, 68, 0.35) !important;
    }

    /* 8. ENTRADAS DE TEXTO, SELECTORES Y ÁREAS DE TEXTO */
    input, div[data-baseweb="select"] > div, textarea {
        background-color: #F8FAFC !important; 
        border: 1px solid #CBD5E1 !important; 
        border-radius: 10px !important;
        color: #0F172A !important; 
        transition: all 0.2s ease !important;
        box-shadow: inset 0 1px 2px rgba(15, 23, 42, 0.03) !important; 
    }
    input:hover, textarea:hover, div[data-baseweb="select"] > div:hover {
        border-color: #94A3B8 !important;
        background-color: #FFFFFF !important;
    }
    input:focus, textarea:focus, div[data-baseweb="select"] > div:focus-within {
        background-color: #FFFFFF !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.18) !important;
        border-color: #2563EB !important;
    }
    
    /* 9. TÍTULOS DE LOS CAMPOS (Labels) */
    [data-testid="stTextInput"] label, [data-testid="stTextArea"] label, [data-testid="stSelectbox"] label, [data-testid="stDateInput"] label, [data-testid="stNumberInput"] label {
        display: block !important;
        font-weight: 600 !important;
        color: #334155 !important;
        font-size: 13.5px !important;
        margin-bottom: 5px !important;
    }

    /* 10. ALERTAS Y NOTIFICACIONES REFINADAS */
    [data-testid="stAlert"] {
        border-radius: 12px !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03) !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA DE LOGIN (PANTALLA DE ACCESO PREMIUM) ---
def login():
    st.markdown("""
        <style>
        .stApp {
            background: radial-gradient(circle at 20% 20%, #EFF6FF 0%, #F8FAFC 45%, #E2E8F0 100%);
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 22px !important;
            border: 1px solid rgba(255, 255, 255, 0.9) !important;
            box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.12), 0 0 0 1px rgba(15, 23, 42, 0.03) !important;
            background: rgba(255, 255, 255, 0.96) !important;
            backdrop-filter: blur(12px) !important;
            padding: 28px !important;
        }
        [data-testid="stTextInput"] input {
            background-color: #F8FAFC !important; 
            border: 1px solid #CBD5E1 !important;
            border-radius: 12px !important;
            padding: 14px 16px !important; 
            font-size: 15px !important;
            color: #0F172A !important;
            font-weight: 500 !important;
        }
        .stFormSubmitButton button {
            border-radius: 12px !important;
            padding: 10px 0px !important;
            font-size: 15px !important;
            letter-spacing: 0.8px;
            background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%) !important;
            box-shadow: 0 8px 20px -4px rgba(37, 99, 235, 0.4) !important;
            border: none !important;
            color: white !important;
            margin-top: 12px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.write("")
    st.write("")
    mostrar_logo(ancho="210px")
    
    col1, col2, col3 = st.columns([1.3, 1.1, 1.3])
    
    with col2:
        with st.container(border=True):
            st.markdown("""
                <div style="text-align: center; margin-bottom: 22px;">
                    <span style="background: #EFF6FF; color: #1D4ED8; font-size: 11px; font-weight: 700; padding: 4px 12px; border-radius: 999px; letter-spacing: 0.8px; text-transform: uppercase;">Portal Clínico Encriptado</span>
                    <h3 style="color: #0F172A; margin-top: 10px; margin-bottom: 4px; font-size: 22px;">Bienvenido de nuevo</h3>
                    <p style="color: #64748B; font-size: 13.5px; margin: 0;">Ingrese sus credenciales corporativas de Terintalia</p>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("form_login", clear_on_submit=False):
                usuario = st.text_input("CORREO CORPORATIVO", placeholder="nombre@terintalia.com").lower().strip()
                password = st.text_input("CONTRASEÑA", type="password", placeholder="••••••••")
                
                submit = st.form_submit_button("INGRESAR AL PORTAL →", type="primary", use_container_width=True)
                
                if submit:
                    if usuario == "admin@terintalia.com" and password == "Master2026":
                        st.session_state.autenticado = True
                        st.session_state.rol = "DIRECTOR"
                        st.session_state.nombre = "DIRECTOR GENERAL"
                        st.session_state.user_id = "ADMIN"
                        st.rerun()
                    elif usuario in ["asistente.clinico@terintalia.com", "recepcion@terintalia.com"] and password == "Recep2026":
                        st.session_state.autenticado = True
                        st.session_state.rol = "RECEPCIONISTA"
                        st.session_state.nombre = "ASISTENTE CLÍNICO"
                        st.session_state.user_id = "ASISTENTE"
                        st.rerun()
                    else:
                        query = db.collection("especialistas").where("correo_corporativo", "==", usuario).get()
                        if query:
                            user_doc = query[0].to_dict()
                            if user_doc.get("estatus", "ACTIVO").upper() == "INACTIVO":
                                st.error("🚫 Acceso denegado: Usuario revocado o inactivo. Contacte al administrador.")
                            elif user_doc.get("password") == password:
                                st.session_state.autenticado = True
                                st.session_state.rol = user_doc.get("rol", "ESPECIALISTA").upper()
                                st.session_state.user_id = user_doc.get("especialista_id_interno")
                                st.session_state.nombre = user_doc.get("nombre_completo")
                                st.rerun()
                            else: 
                                st.error("Clave incorrecta.")
                        else: 
                            st.error("Usuario no registrado.")
                            
        st.markdown("<p style='text-align:center; color:#94A3B8; font-size:12px; margin-top:18px;'>🔒 Terintalia OS • Cumplimiento Normativo de Expediente Clínico</p>", unsafe_allow_html=True)

# --- INICIO DEL SISTEMA ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    login()
else:
    rol = st.session_state.rol
    rol_visual = "ASISTENTE CLÍNICO" if rol in ["RECEPCIONISTA", "ASISTENTE CLÍNICO"] else rol
    
    partes_nombre = st.session_state.nombre.split()
    iniciales_user = "".join([p[0] for p in partes_nombre[:2]]).upper() if partes_nombre else "TR"
    
    with st.sidebar:
        mostrar_logo(ancho="150px")
        
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 14px; padding: 14px; margin: 8px 0 20px 0; display: flex; align-items: center; gap: 12px;">
                <div style="width: 42px; height: 42px; border-radius: 10px; background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: 700; font-size: 15px; flex-shrink: 0; box-shadow: 0 4px 10px rgba(37,99,235,0.3);">
                    {iniciales_user}
                </div>
                <div style="overflow: hidden;">
                    <div style="color: #F8FAFC; font-weight: 600; font-size: 13.5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{st.session_state.nombre}</div>
                    <div style="display: inline-block; background: rgba(59, 130, 246, 0.2); color: #60A5FA; font-size: 10.5px; font-weight: 700; padding: 2px 8px; border-radius: 999px; margin-top: 4px; letter-spacing: 0.4px;">● {rol_visual}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<p style='font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 1.2px; color: #64748B !important; margin-bottom: 6px; padding-left: 4px;'>Navegación Clínica</p>", unsafe_allow_html=True)
        
        opciones_principales = ["📊 Dashboard (Inicio)"]
        
        if rol in ["DIRECTOR", "RECEPCIONISTA", "ASISTENTE CLÍNICO"]:
            opciones_principales += ["📝 Alta de Pacientes", "👩‍⚕️ Alta de Especialistas"]
        
        opciones_principales.append("📂 Expediente Clínico")
        opciones_principales.append("📁 Repositorio")
        
        if rol == "DIRECTOR":
            opciones_principales.append("⚙️ Gestión de Clínica")
        
        opcion = st.radio("Módulos", opciones_principales, key="menu_principal", label_visibility="collapsed")
        
        st.markdown("<div style='margin-top: 28px; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 16px;'></div>", unsafe_allow_html=True)
        if st.button("🚪 Cerrar Sesión Segura", key="btn_cerrar", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    # =========================================================
    # RUTEO DE PANTALLAS: DASHBOARD ANALÍTICO EJECUTIVO
    # =========================================================
    if opcion == "📊 Dashboard (Inicio)":
        hoy_str = datetime.now().strftime("%d / %m / %Y")
        
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%); border-radius: 20px; padding: 28px 32px; color: white; margin-bottom: 24px; box-shadow: 0 12px 28px -6px rgba(30, 58, 138, 0.25); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                <div>
                    <span style="background: rgba(255,255,255,0.12); color: #93C5FD; font-size: 11.5px; font-weight: 600; padding: 5px 12px; border-radius: 999px; letter-spacing: 0.6px;">📅 FECHA DEL SISTEMA: {hoy_str}</span>
                    <h2 style="color: #FFFFFF !important; margin: 12px 0 4px 0; font-size: 28px; font-weight: 800;">Panel de Control Clínico</h2>
                    <p style="color: #CBD5E1 !important; margin: 0; font-size: 14.5px;">Bienvenido, <b>{st.session_state.nombre}</b>. Monitoreo en tiempo real del padrón y áreas de especialidad.</p>
                </div>
                <div style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.14); border-radius: 14px; padding: 12px 20px; text-align: right;">
                    <div style="font-size: 11px; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.8px;">Nivel de Acceso</div>
                    <div style="font-size: 16px; font-weight: 700; color: #38BDF8; margin-top: 2px;">{rol_visual}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        todos_docs = db.collection("pacientes").get()
        
        if rol in ["DIRECTOR", "RECEPCIONISTA", "ASISTENTE CLÍNICO"]:
            pacientes_docs = todos_docs
        else:
            pacientes_docs = []
            for doc in todos_docs:
                if st.session_state.user_id in doc.to_dict().get("med", ""):
                    pacientes_docs.append(doc)

        lista_pac_data = [p.to_dict() for p in pacientes_docs]
        total_pac = len(lista_pac_data)
        pac_activos = sum(1 for p in lista_pac_data if p.get("status") == "ACTIVO")
        pac_inactivos = total_pac - pac_activos
        porcentaje_activo = int((pac_activos / total_pac) * 100) if total_pac > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
                <div style="background: white; border-radius: 16px; padding: 22px 24px; border: 1px solid #E2E8F0; border-left: 5px solid #2563EB; box-shadow: 0 4px 12px rgba(15,23,42,0.04);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #64748B; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Total Expedientes</span>
                        <span style="background: #EFF6FF; color: #2563EB; padding: 8px 10px; border-radius: 10px; font-size: 18px;">👥</span>
                    </div>
                    <div style="font-size: 36px; font-weight: 800; color: #0F172A; margin: 10px 0 4px 0; font-family: 'Plus Jakarta Sans', sans-serif;">{total_pac}</div>
                    <div style="color: #64748B; font-size: 12.5px;">Padrón registrado bajo tu alcance</div>
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div style="background: white; border-radius: 16px; padding: 22px 24px; border: 1px solid #E2E8F0; border-left: 5px solid #10B981; box-shadow: 0 4px 12px rgba(15,23,42,0.04);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #64748B; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Pacientes Activos</span>
                        <span style="background: #ECFDF5; color: #10B981; padding: 8px 10px; border-radius: 10px; font-size: 18px;">🟢</span>
                    </div>
                    <div style="font-size: 36px; font-weight: 800; color: #0F172A; margin: 10px 0 4px 0; font-family: 'Plus Jakarta Sans', sans-serif;">{pac_activos}</div>
                    <div style="color: #059669; font-size: 12.5px; font-weight: 600;">{porcentaje_activo}% de tasa de actividad clínica</div>
                </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
                <div style="background: white; border-radius: 16px; padding: 22px 24px; border: 1px solid #E2E8F0; border-left: 5px solid #94A3B8; box-shadow: 0 4px 12px rgba(15,23,42,0.04);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #64748B; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">Archivo / Inactivos</span>
                        <span style="background: #F1F5F9; color: #64748B; padding: 8px 10px; border-radius: 10px; font-size: 18px;">📁</span>
                    </div>
                    <div style="font-size: 36px; font-weight: 800; color: #0F172A; margin: 10px 0 4px 0; font-family: 'Plus Jakarta Sans', sans-serif;">{pac_inactivos}</div>
                    <div style="color: #64748B; font-size: 12.5px;">Expedientes en resguardo histórico</div>
                </div>
            """, unsafe_allow_html=True)
                
        st.write("")

        col_ana1, col_ana2 = st.columns([1.15, 1])

        with col_ana1:
            with st.container(border=True):
                st.markdown("""
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                        <div>
                            <div style="font-size:16px; font-weight:800; color:#0F172A; font-family:'Plus Jakarta Sans',sans-serif;">📊 Distribución por Especialidad y Modalidad</div>
                            <div style="font-size:12.5px; color:#64748B;">Carga clínica activa segmentada por área de atención</div>
                        </div>
                        <span style="background:#EFF6FF; color:#1D4ED8; font-size:11px; font-weight:700; padding:4px 10px; border-radius:999px;">Tiempo Real</span>
                    </div>
                """, unsafe_allow_html=True)

                if total_pac == 0:
                    st.info("Aún no hay pacientes registrados para generar métricas por especialidad.")
                else:
                    conteo_esp = {}
                    conteo_mod = {"Presencial": 0, "Online": 0, "Híbrido": 0}
                    for p in lista_pac_data:
                        esp_nom = p.get("esp", "OTRA").upper()
                        conteo_esp[esp_nom] = conteo_esp.get(esp_nom, 0) + 1
                        mod_nom = p.get("modalidad", "N/A")
                        if mod_nom in conteo_mod:
                            conteo_mod[mod_nom] += 1

                    colores_barras = ["#2563EB", "#10B981", "#8B5CF6", "#F59E0B", "#EC4899"]
                    html_barras = ""
                    for idx, (esp_k, cant) in enumerate(sorted(conteo_esp.items(), key=lambda x: x[1], reverse=True)):
                        pct = int((cant / total_pac) * 100)
                        color_b = colores_barras[idx % len(colores_barras)]
                        html_barras += f"""
                        <div style="margin-bottom: 14px;">
                            <div style="display:flex; justify-content:space-between; font-size:13px; font-weight:600; color:#1E293B; margin-bottom:5px;">
                                <span>{esp_k}</span>
                                <span style="color:#64748B;"><b>{cant}</b> pac. ({pct}%)</span>
                            </div>
                            <div style="width:100%; background:#F1F5F9; height:9px; border-radius:999px; overflow:hidden;">
                                <div style="width:{max(pct, 4)}%; background:{color_b}; height:100%; border-radius:999px;"></div>
                            </div>
                        </div>
                        """
                    st.markdown(html_barras, unsafe_allow_html=True)

                    st.markdown(f"""
                        <div style="margin-top: 18px; padding-top: 14px; border-top: 1px solid #F1F5F9; display: flex; gap: 10px; flex-wrap: wrap;">
                            <div style="flex:1; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:8px 12px; text-align:center;">
                                <div style="font-size:11px; color:#64748B; font-weight:600;">🏢 PRESENCIAL</div>
                                <div style="font-size:16px; font-weight:800; color:#0F172A; margin-top:2px;">{conteo_mod['Presencial']}</div>
                            </div>
                            <div style="flex:1; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:8px 12px; text-align:center;">
                                <div style="font-size:11px; color:#64748B; font-weight:600;">💻 ONLINE</div>
                                <div style="font-size:16px; font-weight:800; color:#0F172A; margin-top:2px;">{conteo_mod['Online']}</div>
                            </div>
                            <div style="flex:1; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:10px; padding:8px 12px; text-align:center;">
                                <div style="font-size:11px; color:#64748B; font-weight:600;">🔄 HÍBRIDO</div>
                                <div style="font-size:16px; font-weight:800; color:#0F172A; margin-top:2px;">{conteo_mod['Híbrido']}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

        with col_ana2:
            with st.container(border=True):
                st.markdown("""
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
                        <div>
                            <div style="font-size:16px; font-weight:800; color:#0F172A; font-family:'Plus Jakarta Sans',sans-serif;">🆕 Últimos Expedientes Aperturados</div>
                            <div style="font-size:12.5px; color:#64748B;">Registros más recientes ingresados a la plataforma</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                if total_pac == 0:
                    st.info("No hay expedientes recientes para mostrar.")
                else:
                    pac_recientes = lista_pac_data[-4:][::-1]
                    html_feed = ""
                    for pr in pac_recientes:
                        nom_pr = pr.get("nombre", "Paciente")
                        id_pr = pr.get("id_p", "S/F")
                        esp_pr = pr.get("esp", "Clínica")
                        ini_pr = pr.get("fecha_inicio_tratamiento", pr.get("fecha_registro", "Reciente"))
                        html_feed += f"""
                        <div style="display:flex; justify-content:space-between; align-items:center; padding:10px 12px; border-radius:12px; background:#F8FAFC; border:1px solid #E2E8F0; margin-bottom:8px;">
                            <div style="overflow:hidden; padding-right:8px;">
                                <div style="font-size:13.5px; font-weight:700; color:#0F172A; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">{nom_pr}</div>
                                <div style="font-size:11.5px; color:#64748B;">{esp_pr} • Inicio: {ini_pr}</div>
                            </div>
                            <span style="background:#FFF7ED; color:#EA580C; border:1px solid #FED7AA; font-size:11px; font-weight:700; padding:3px 9px; border-radius:999px; flex-shrink:0;">{id_pr}</span>
                        </div>
                        """
                    st.markdown(html_feed, unsafe_allow_html=True)

        st.markdown("""
            <div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 18px 24px; margin-top: 8px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 12px;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <div style="background: #FEF3C7; color: #D97706; width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 18px;">💡</div>
                    <div>
                        <div style="font-weight: 700; color: #0F172A; font-size: 14px;">Navegación Rápida de Expedientes</div>
                        <div style="color: #64748B; font-size: 12.5px;">Dirígete a <b>Expediente Clínico</b> en el menú lateral para visualizar el nuevo Semáforo de Cumplimiento Legal de cada paciente.</div>
                    </div>
                </div>
                <span style="background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; font-size: 11.5px; font-weight: 700; padding: 5px 12px; border-radius: 999px;">✓ NOM-004-SSA3-2012 Activo</span>
            </div>
        """, unsafe_allow_html=True)

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
