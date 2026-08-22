import streamlit as st
import matplotlib.pyplot as plt
import datetime

# ---------------------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA (¡Debe ser la primerísima línea!)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="FloraVision",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializar de manera estricta el estado de la página si no existe En "Inicio"
if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = "Inicio"

# Evita traducciones molestas en Google Chrome que rompan la maquetación
st.markdown('<html lang="es" class="notranslate" translate="no">', unsafe_allow_html=True)
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@800&display=swap" rel="stylesheet">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# PALETA DE COLORES OFICIAL Y BASE DE DATOS LOCAL
# ---------------------------------------------------------------------------
MAROON = "#5C0030"
MAROON_DARK = "#4A0027"
GOLD = "#C9A227"
PINK = "#F6A8C9"
CREAM = "#FDF3F1"
CARD_BORDER = "#B98DA0"
TRACK_GREY = "#E2DFDF"
TEXT_MAROON = "#5C0030"

# Datos compartidos del Inventario (Gráficos Dinámicos y Funcionales)
DATOS_INVENTARIO = {
    "Planta": ["Rosa", "Orquídea", "Girasol", "Tulipán"],
    "Cantidad": [45, 18, 32, 14],
    "Estado": ["Saludable", "Riesgo", "Saludable", "Enferma"]
}

# ---------------------------------------------------------------------------
# CSS GLOBAL (Réplica exacta de tu Mockup)
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
        [data-testid="stAppViewContainer"] {{
            background-color: {CREAM} !important;
            transition: background-color 0.3s ease;
        }}
        [data-testid="stAppViewContainer"] > .main {{
            background-color: {CREAM};
        }}
        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1150px;
        }}
        [data-testid="stSidebar"] {{
            background-color: {MAROON} !important;
        }}

        /* LOGO INTERACTIVO EN EL SIDEBAR */
        .logo-btn-container div.stButton > button {{
            background-color: white !important;
            border: 2px solid {CARD_BORDER} !important;
            border-radius: 25px !important;
            padding: 0.5rem 1.2rem !important;
            width: 100% !important;
            text-align: center !important;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.04) !important;
            cursor: pointer !important;
            transition: all 0.15s ease-in-out !important;
            margin-bottom: 0.5rem !important;
        }}
        .logo-btn-container div.stButton > button:hover {{
            background-color: {CREAM} !important;
            border-color: {MAROON} !important;
            transform: translateY(-1px);
        }}
        .logo-btn-container div.stButton > button p,
        .logo-btn-container p,
        .floravision-logo p {{
            color: {TEXT_MAROON} !important;
            -webkit-text-fill-color: {TEXT_MAROON} !important;
            font-family: 'Montserrat', sans-serif !important;
            font-size: 1.8rem !important;
            font-weight: 800 !important;
            letter-spacing: -0.5px !important;
            line-height: 1.2 !important;
            margin: 0 !important;
        }}
        
        .brand-underline {{
            width: 180px;
            height: 3px;
            background: linear-gradient(90deg, {PINK} 0%, {GOLD} 100%);
            margin-top: 6px;
            margin-bottom: 2.5rem;
        }}

        /* BOTONES DEL MENÚ LATERAL (ST.RADIO) */
        div[data-testid="stRadio"] label {{
            background-color: white !important;
            border: 2px solid {CARD_BORDER} !important;
            border-radius: 25px !important;
            padding: 0.5rem 1.2rem !important;
            margin-bottom: 0.8rem !important;
            width: 100% !important;
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            cursor: pointer !important;
            box-shadow: 0px 2px 5px rgba(0,0,0,0.04);
            transition: all 0.15s ease-in-out !important;
        }}
        div[data-testid="stRadio"] label p {{
            color: {TEXT_MAROON} !important;
            font-family: 'Georgia', serif !important;
            font-weight: 600 !important;
            font-size: 1.05rem !important;
            margin: 0 !important;
        }}
        
        div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"]::before {{ display: none !important; }}
        div[data-testid="stWidgetMarkdownExpanded"] {{ display: none !important; }}
        
        /* Ocultar la primera opción fantasma (Inicio) */
        div[data-testid="stRadio"] > label:first-child {{ display: none !important; }}
        div[data-testid="stRadio"] div[role="radiogroup"] > label:first-child {{ display: none !important; }}

        /* ESTILIZACIÓN DEL CALENDARIO FUNCIONAL */
        div[data-testid="stDateInput"] div[data-baseweb="input"] {{
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
        }}
        div[data-testid="stDateInput"] input {{
            font-size: 1.1rem !important;
            font-family: 'Georgia', serif !important;
            color: {TEXT_MAROON} !important;
            font-weight: bold !important;
            width: 130px !important;
            text-align: right !important;
            cursor: pointer !important;
        }}

        /* CUADRO MAESTRO DE INICIO: Estilizamos el st.container(border=True) nativo */
        .main div[data-testid="stVerticalBlockBorderWrapper"] {{
            background-color: white !important;
            border: 12px solid {CARD_BORDER} !important;
            border-radius: 24px !important;
            padding: 30px 40px !important;
            box-shadow: 0px 10px 30px rgba(0,0,0,0.04) !important;
        }}
        
        /* Evita duplicaciones del borde lila en sub-bloques internos */
        .main div[data-testid="stVerticalBlockBorderWrapper"] div[data-testid="stVerticalBlockBorderWrapper"] {{
            border: none !important;
            padding: 0 !important;
            box-shadow: none !important;
            background-color: transparent !important;
        }}

        .main-section-title {{
            text-align: center;
            color: {TEXT_MAROON};
            font-family: 'Georgia', serif;
            font-weight: 700;
            font-size: 1.8rem;
            margin-bottom: 2rem;
        }}

        /* TARJETAS KPI GENERALES */
        .kpi-card {{ background-color: white; border: 4px solid {CARD_BORDER}; border-radius: 20px; padding: 1.5rem; text-align: center; }}
        .kpi-title {{ font-family: 'Georgia', serif; font-weight: bold; font-size: 1.1rem; color: {TEXT_MAROON}; margin-bottom: 0.5rem; }}
        .kpi-value {{ font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 2.2rem; }}
        
        /* ESTILO PARA CONTENEDOR DE FILA INFERIOR DEL DASHBOARD */
        .dashboard-box-dark {{ 
            background-color: transparent; 
            border: 4px solid rgba(255,255,255,0.2); 
            border-radius: 25px; 
            padding: 2rem; 
            height: 100%; 
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# INYECCIÓN DINÁMICA DE FONDO OSCURO SÓLO PARA EL DASHBOARD (Efecto Canva)
# ---------------------------------------------------------------------------
if st.session_state.pagina_actual == "Dashboard":
    st.markdown(
        f"""
        <style>
            [data-testid="stAppViewContainer"] {{
                background-color: {MAROON} !important;
            }}
            [data-testid="stAppViewContainer"] > .main {{
                background-color: {MAROON} !important;
            }}
            .section-title {{
                color: white !important;
            }}
            /* Tarjetas KPI mutan a fondo transparente con bordes claros en Dashboard */
            .kpi-card {{
                background-color: transparent !important;
                border: 4px solid rgba(255,255,255,0.3) !important;
            }}
            .kpi-title {{ color: rgba(255,255,255,0.8) !important; }}
        </style>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------------------------------
# CONTROLES DE NAVEGACIÓN (Callbacks unificados)
# ---------------------------------------------------------------------------
def ir_a_inicio():
    st.session_state.pagina_actual = "Inicio"
    if "sidebar_radio" in st.session_state:
        st.session_state.sidebar_radio = "Inicio"

def cambiar_modulo():
    if "sidebar_radio" in st.session_state:
        st.session_state.pagina_actual = st.session_state.sidebar_radio

# ---------------------------------------------------------------------------
# MENÚ EN LA BARRA LATERAL (SIDEBAR)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown('<div class="logo-btn-container">', unsafe_allow_html=True)
    st.button("FloraVision", key="btn_logo_home", on_click=ir_a_inicio)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="brand-underline"></div>', unsafe_allow_html=True)

    opciones_menu = ["Inicio", "Detección", "Inventario", "Dashboard"]
    idx_defecto = opciones_menu.index(st.session_state.pagina_actual) if st.session_state.pagina_actual in opciones_menu else 0

    st.radio(
        label="MenuSeleccion",
        options=opciones_menu,
        index=idx_defecto,
        label_visibility="collapsed",
        key="sidebar_radio",
        on_change=cambiar_modulo
    )

# ---------------------------------------------------------------------------
# COMPONENTES AUXILIARES DINÁMICOS
# ---------------------------------------------------------------------------
def progress_bars():
    cantidades = DATOS_INVENTARIO["Cantidad"]
    html = '<div style="width: 100%; display: flex; flex-direction: column; justify-content: center; height: 100%; gap: 20px; padding-top: 15px; padding-bottom: 15px;">'
    colores = [MAROON, PINK, GOLD, "#CC8FB2"]
    
    for i, cant in enumerate(cantidades):
        porcentaje = min(int((cant / 60) * 100), 100)
        html += f'<div style="width:100%; height:18px; background:{TRACK_GREY}; border-radius:20px; overflow:hidden;"><div style="width:{porcentaje}%; height:100%; background:{colores[i]}; border-radius:20px;"></div></div>'
    html += '</div>'
    return html

# ---------------------------------------------------------------------------
# RENDERIZADO DE LAS VISTAS
# ---------------------------------------------------------------------------
def render_inicio():
    """Slide 1: Estructura Canva Crema Nativa"""
    col_vacia, col_calendario = st.columns([3.5, 1])
    with col_calendario:
        st.date_input(
            label="Fecha",
            value=datetime.date.today(),
            label_visibility="collapsed",
            key="calendar_widget"
        )

    with st.container(border=True):
        st.markdown('<div class="main-section-title">Resumen Semanal</div>', unsafe_allow_html=True)
        col_dona, col_barras = st.columns([1, 1.2])
        
        with col_dona:
            estados = DATOS_INVENTARIO["Estado"]
            sanas = estados.count("Saludable")
            riesgo = estados.count("Riesgo")
            enfermas = estados.count("Enferma")
            
            values = [sanas, riesgo, enfermas]
            colors = [PINK, GOLD, MAROON]
            
            fig, ax = plt.subplots(figsize=(3.1, 3.1), subplot_kw=dict(aspect="equal"))
            ax.pie(values, colors=colors, startangle=90, counterclock=False, wedgeprops=dict(width=0.42, edgecolor='white', linewidth=3))
            fig.patch.set_facecolor('none')
            ax.set_facecolor('none')
            st.pyplot(fig, clear_figure=True, use_container_width=True)
            
        with col_barras:
            st.markdown(progress_bars(), unsafe_allow_html=True)


def render_deteccion():
    st.markdown('<div class="section-title">Detección Inteligente</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f'<div style="background:white; border:12px solid {CARD_BORDER}; border-radius:25px; padding:25px;">', unsafe_allow_html=True)
        archivo = st.file_uploader("Sube tu foto para análisis de detección", type=["jpg", "jpeg", "png"])
        if archivo: st.image(archivo, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div style="background:white; border:12px solid {CARD_BORDER}; border-radius:25px; padding:25px;">', unsafe_allow_html=True)
        st.subheader("Resultado")
        st.progress(78)
        st.success("Planta identificada")
        st.write("Enfermedad detectada: Mancha Foliar")
        st.info("Confianza del modelo: 78 %")
        st.write("Recomendación: Aplicar tratamiento preventivo.")
        st.markdown("</div>", unsafe_allow_html=True)


def render_inventario():
    st.markdown('<div class="section-title">Inventario</div>', unsafe_allow_html=True)
    st.dataframe(DATOS_INVENTARIO, use_container_width=True)


def render_dashboard():
    """Slide 4: El Dashboard Invertido con Fondo Oscuro Oficial de Canva (Error de Matplotlib solucionado)"""
    st.markdown('<div class="section-title" style="font-family: Georgia, serif; font-size: 2rem; font-weight:700;">Dashboard FloraVision</div>', unsafe_allow_html=True)
    
    # Botón de Filtro Temporal Estilo Canva (Amarillo)
    st.markdown(f'<div style="display:inline-block; background-color:{GOLD}; color:{MAROON}; font-family:Georgia, serif; font-weight:bold; padding: 6px 16px; border-radius:8px; margin-bottom:20px; font-size:0.9rem;">Última Semana</div>', unsafe_allow_html=True)

    # 1. FILA DE METRICAS KPI SUPERIORES (Estilo Tarjetas del Boceto)
    card_col1, card_col2, card_col3 = st.columns(3)
    cantidades = DATOS_INVENTARIO["Cantidad"]
    estados = DATOS_INVENTARIO["Estado"]
    
    with card_col1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Plantas Enfermas</div><div class="kpi-value" style="color: {PINK};">{estados.count("Enferma")}</div></div>', unsafe_allow_html=True)
    with card_col2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Tratamientos Activos</div><div class="kpi-value" style="color: {GOLD};">5</div></div>', unsafe_allow_html=True)
    with card_col3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Unidades Stock</div><div class="kpi-value" style="color: white;">{sum(cantidades)}</div></div>', unsafe_allow_html=True)

    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
    
    # 2. SECCIÓN DE GRÁFICAS (Distribución de barras blancas + Efectividad de recuperación)
    col_grafica, col_efectividad = st.columns([1.4, 1])
    
    with col_grafica:
        st.markdown(f'<div class="dashboard-box-dark">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'Georgia\', serif; font-size:1.2rem; color:white; text-align:center; margin-bottom:15px;">Promedio de Especies en Monitoreo</div>', unsafe_allow_html=True)
        
        especies = DATOS_INVENTARIO["Planta"]
        fig, ax = plt.subplots(figsize=(5, 3.2))
        
        # Las barras pasan a ser Blancas completas para contrastar con el fondo Maroon
        ax.bar(especies, cantidades, color="white", width=0.5, edgecolor="none")
        
        # SOLUCIÓN DE RAÍZ: Pasamos tuplas RGBA válidas para Matplotlib en lugar de Strings HTML
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color((1, 1, 1, 0.4))
        ax.spines['bottom'].set_color((1, 1, 1, 0.4))
        ax.tick_params(colors="white", labelsize=9)
        ax.grid(axis='y', linestyle='--', alpha=0.15, color="white")
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')
        
        st.pyplot(fig, clear_figure=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_efectividad:
        st.markdown(f'<div class="dashboard-box-dark" style="display: flex; flex-direction: column; justify-content: center; text-align:center;">', unsafe_allow_html=True)
        st.markdown('<div style="font-family:\'Georgia\', serif; font-size:1.2rem; color:white; margin-bottom:20px;">Efectividad del Tratamiento</div>', unsafe_allow_html=True)
        
        # Métrica de Porcentaje en Dorado Intenso
        st.markdown(f"""
            <div style="margin-bottom: 1.5rem;">
                <span style="font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 3.8rem; color: {GOLD};">80%</span>
                <p style="font-family: 'Georgia', serif; color: rgba(255,255,255,0.8); font-size: 0.95rem; margin-top: 5px;">Recuperación exitosa en lotes tratados</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.progress(80)
        st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# ENRUTADOR PRINCIPAL
# ---------------------------------------------------------------------------
if st.session_state.pagina_actual == "Inicio":
    render_inicio()
elif st.session_state.pagina_actual == "Detección":
    render_deteccion()
elif st.session_state.pagina_actual == "Inventario":
    render_inventario()
elif st.session_state.pagina_actual == "Dashboard":
    render_dashboard()