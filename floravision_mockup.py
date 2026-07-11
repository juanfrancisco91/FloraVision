import streamlit as st
import matplotlib.pyplot as plt

# ---------------------------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA (¡Debe ser la primerísima línea!)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="FloraVision",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Inicializar de manera estricta el estado de la página si no existe
if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = "Inicio"

# Evita traducciones molestas en Google Chrome que rompan la maquetación
st.markdown('<html lang="es" class="notranslate" translate="no">', unsafe_allow_html=True)
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@800&display=swap" rel="stylesheet">', unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# PALETA DE COLORES OFICIAL
# ---------------------------------------------------------------------------
MAROON = "#5C0030"
MAROON_DARK = "#4A0027"
GOLD = "#C9A227"
PINK = "#F6A8C9"
CREAM = "#FDF3F1"
CARD_BORDER = "#B98DA0"
TRACK_GREY = "#E2DFDF"
TEXT_MAROON = "#5C0030"

# ---------------------------------------------------------------------------
# CSS GLOBAL (Maquetación y Tarjetas del Dashboard)
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
        [data-testid="stAppViewContainer"] {{
            background-color: {CREAM} !important;
        }}
        [data-testid="stAppViewContainer"] > .main {{
            background-color: {CREAM};
        }}
        .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }}
        [data-testid="stSidebar"] {{
            background-color: {MAROON} !important;
        }}

        /* TÍTULO ESTÁTICO DE CANVA (Solución limpia y segura temporal) */
        .brand-logo-text {{
            font-family: 'Montserrat', sans-serif;
            font-size: 2.4rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-bottom: 0px;
            line-height: 1.2;
            user-select: none;
        }}
        .brand-logo-text .color-flora {{ color: {PINK}; }}
        .brand-logo-text .color-vision {{ color: {GOLD}; }}
        
        .brand-underline {{
            width: 180px;
            height: 3px;
            background: linear-gradient(90deg, {PINK} 0%, {GOLD} 100%);
            margin-top: 6px;
            margin-bottom: 2rem;
        }}

        /* Estilizar st.radio como los botones del menú original */
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
            box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
            transition: all 0.15s ease-in-out !important;
        }}
        
        div[data-testid="stRadio"] label p {{
            color: {TEXT_MAROON} !important;
            font-family: 'Georgia', serif !important;
            font-weight: 600 !important;
            font-size: 1.05rem !important;
            margin: 0 !important;
        }}
        
        div[data-testid="stRadio"] label:hover {{
            background-color: {PINK} !important;
            border-color: {PINK} !important;
        }}
        
        /* Ocultar círculos nativos de st.radio */
        div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"]::before {{
            display: none !important;
        }}
        div[data-testid="stWidgetMarkdownExpanded"] {{
            display: none !important;
        }}
        div[data-testid="stRadio"] > label:first-child {{
            display: none !important;
        }}

        .section-title {{
            text-align: center;
            color: {TEXT_MAROON};
            font-family: Georgia, serif;
            font-weight: 700;
            font-size: 1.8rem;
            margin-bottom: 2rem;
        }}

        /* ESTILOS EXCLUSIVOS PARA LAS TARJETAS KPI DEL DASHBOARD */
        .kpi-card {{
            background-color: white;
            border: 4px solid {CARD_BORDER};
            border-radius: 20px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0px 4px 10px rgba(0,0,0,0.02);
        }}
        .kpi-title {{
            font-family: 'Georgia', serif;
            font-weight: bold;
            font-size: 1.1rem;
            color: {TEXT_MAROON};
            margin-bottom: 0.5rem;
        }}
        .kpi-value {{
            font-family: 'Montserrat', sans-serif;
            font-weight: 800;
            font-size: 2.2rem;
        }}
        
        /* CONTENEDOR INFERIOR DEL DASHBOARD */
        .dashboard-box {{
            background-color: white;
            border: 8px solid {CARD_BORDER};
            border-radius: 25px;
            padding: 2rem;
            height: 100%;
        }}
        .dashboard-subtitle {{
            font-family: 'Georgia', serif;
            font-weight: bold;
            font-size: 1.3rem;
            color: {TEXT_MAROON};
            margin-bottom: 1rem;
            text-align: center;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# FUNCIONES DE CONTROL DE NAVEGACIÓN (Callbacks)
# ---------------------------------------------------------------------------
def cambiar_modulo():
    if "sidebar_radio" in st.session_state:
        st.session_state.pagina_actual = st.session_state.sidebar_radio

# ---------------------------------------------------------------------------
# MENÚ EN LA BARRA LATERAL (SIDEBAR)
# ---------------------------------------------------------------------------
with st.sidebar:
    # Logotipo nítido e impecable
    st.markdown(
        '<div class="brand-logo-text"><span class="color-flora">Flora</span><span class="color-vision">Vision</span></div>'
        '<div class="brand-underline"></div>',
        unsafe_allow_html=True,
    )

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
# COMPONENTES AUXILIARES
# ---------------------------------------------------------------------------
def progress_bars():
    barras = [
        (55, MAROON),
        (35, PINK),
        (65, GOLD),
        (75, MAROON),
        (45, "#CC8FB2"),
    ]
    html = '<div style="width: 100%; display: flex; flex-direction: column; justify-content: center; height: 100%; gap: 16px;">'
    for porcentaje, color in barras:
        html += f'<div style="width:100%; height:18px; background:{TRACK_GREY}; border-radius:20px; overflow:hidden;"><div style="width:{porcentaje}%; height:100%; background:{color}; border-radius:20px;"></div></div>'
    html += '</div>'
    return html

# ---------------------------------------------------------------------------
# RENDERIZADO DE LAS VISTAS
# ---------------------------------------------------------------------------
def render_inicio():
    st.markdown("""<div style="text-align: center; font-size: 2.5rem; margin-top: 10px; margin-bottom: 5px;">📅</div>""", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Resumen Semanal</div>', unsafe_allow_html=True)

    _, col_izq, col_espacio, col_der, _ = st.columns([0.2, 1.1, 0.2, 1.3, 0.2])
    with col_izq:
        values = [35, 35, 30]
        colors = [PINK, GOLD, MAROON]
        fig, ax = plt.subplots(figsize=(3.2, 3.2), subplot_kw=dict(aspect="equal"))
        ax.pie(values, colors=colors, startangle=90, counterclock=False, wedgeprops=dict(width=0.42, edgecolor='white', linewidth=3))
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')
        st.pyplot(fig, clear_figure=True, use_container_width=True)
    with col_der:
        st.markdown(progress_bars(), unsafe_allow_html=True)


def render_deteccion():
    st.markdown('<div class="section-title">Detección Inteligente</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown(f'<div style="background:white; border:12px solid {CARD_BORDER}; border-radius:25px; padding:25px;">', unsafe_allow_html=True)
        archivo = st.file_uploader("Sube tu foto para análisis de detección", type=["jpg", "jpeg", "png"])
        if archivo:
            st.image(archivo, use_container_width=True)
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
    datos = {
        "Planta": ["Rosa", "Orquídea", "Girasol", "Tulipán"],
        "Cantidad": [45, 18, 32, 14],
        "Estado": ["Saludable", "Riesgo", "Saludable", "Enferma"]
    }
    st.dataframe(datos, use_container_width=True)


def render_dashboard():
    """Slide 4: Dashboard Completo basado en tu Mockup Dibujado"""
    st.markdown("""<div style="text-align: center; font-size: 2.5rem; margin-top: 10px; margin-bottom: 5px;">📊</div>""", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Estadísticas Generales</div>', unsafe_allow_html=True)

    # 1. FILA DE TARJETAS DE MÉTRICAS (KPIs superiores del dibujo)
    card_col1, card_col2, card_col3 = st.columns(3)
    
    with card_col1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Plantas Enfermas</div>
                <div class="kpi-value" style="color: {MAROON};">14</div>
            </div>
        """, unsafe_allow_html=True)
        
    with card_col2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Tratamientos Activos</div>
                <div class="kpi-value" style="color: {GOLD};">5</div>
            </div>
        """, unsafe_allow_html=True)
        
    with card_col3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">Plantas Saludables</div>
                <div class="kpi-value" style="color: {PINK};">95</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)

    # 2. BLOQUE INFERIOR (Gráfico de barras + Progreso de efectividad)
    col_grafica, col_efectividad = st.columns([1.3, 1])
    
    with col_grafica:
        st.markdown(f'<div class="dashboard-box">', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-subtitle">Distribución por Especies</div>', unsafe_allow_html=True)
        
        # Crear gráfico de barras verticales (Estilo limpio)
        especies = ["Rosa", "Orquídea", "Girasol", "Tulipán"]
        cantidades = [45, 18, 32, 14]
        colores_barras = [MAROON, PINK, GOLD, "#CC8FB2"]
        
        fig, ax = plt.subplots(figsize=(5, 3.2))
        barras = ax.bar(especies, cantidades, color=colores_barras, width=0.5, edgecolor="none")
        
        # Estilización del gráfico
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(CARD_BORDER)
        ax.spines['bottom'].set_color(CARD_BORDER)
        ax.tick_params(colors=TEXT_MAROON, labelsize=9)
        ax.grid(axis='y', linestyle='--', alpha=0.3, color=CARD_BORDER)
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')
        
        st.pyplot(fig, clear_figure=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_efectividad:
        st.markdown(f'<div class="dashboard-box" style="display: flex; flex-direction: column; justify-content: center;">', unsafe_allow_html=True)
        st.markdown('<div class="dashboard-subtitle">Efectividad del Tratamiento</div>', unsafe_allow_html=True)
        
        # Muestra la métrica del 80% solicitada en tu boceto
        st.markdown(f"""
            <div style="text-align: center; margin-bottom: 1.5rem;">
                <span style="font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 3.5rem; color: {GOLD};">80%</span>
                <p style="font-family: 'Georgia', serif; color: {TEXT_MAROON}; font-size: 0.95rem; margin-top: 0px;">Recuperación exitosa en lotes tratados</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Barra de progreso estilizada acorde a la paleta
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