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

# Evita que Google Chrome intente traducir la página y rompa los estilos
st.markdown('<html lang="es" class="notranslate" translate="no">', unsafe_allow_html=True)

# Importar fuentes de Google Fonts para mejorar la tipografía
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&display=swap" rel="stylesheet">', unsafe_allow_html=True)

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
# CSS GLOBAL (Estilos de Interfaz)
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <style>
        /* Fondo general crema */
        [data-testid="stAppViewContainer"] {{
            background-color: {CREAM} !important;
        }}
        [data-testid="stAppViewContainer"] > .main {{
            background-color: {CREAM};
        }}

        .block-container {{
            padding-top: 2.5rem;
            padding-bottom: 3rem;
            padding-left: 3rem;
            padding-right: 3rem;
            max-width: 1200px;
        }}

        /* Barra lateral (Granate) */
        [data-testid="stSidebar"] {{
            background-color: {MAROON} !important;
        }}
        [data-testid="stSidebar"] > div:first-child {{
            padding-top: 2rem;
        }}

        /* Título FloraVision en la barra lateral con nueva tipografía */
        .brand-title {{
            font-family: 'Montserrat', sans-serif;
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: -0.5px;
            margin-bottom: 0px;
            display: inline-block;
        }}
        .brand-title .color-flora {{
            color: {PINK};        
        }}
        .brand-title .color-vision {{
            color: {GOLD};        
        }}
        .brand-underline {{
            width: 180px;
            height: 3px;
            background: linear-gradient(90deg, {PINK} 0%, {GOLD} 100%);
            margin-top: 4px;
            margin-bottom: 2.5rem;
        }}

        /* Estilizar las opciones de st.radio para que parezcan botones redondeados de Canva */
        div[data-testid="stRadio"] label {{
            background-color: transparent !important;
            color: {CREAM} !important;
            border: 2px solid {GOLD} !important;
            border-radius: 25px !important;
            padding: 0.5rem 1.2rem !important;
            margin-bottom: 0.8rem !important;
            width: 100% !important;
            display: flex !important;
            font-family: 'Georgia', serif !important;
            font-weight: 600 !important;
            cursor: pointer !important;
            transition: all 0.15s ease-in-out !important;
        }}
        div[data-testid="stRadio"] label:hover {{
            background-color: {PINK} !important;
            border-color: {PINK} !important;
            color: {MAROON_DARK} !important;
        }}
        
        /* Oculta los círculos de opción nativos y contenedores vacíos */
        div[data-testid="stRadio"] label div[data-testid="stMarkdownContainer"]::before {{
            display: none !important;
        }}
        div[data-testid="stWidgetMarkdownExpanded"] {{
            display: none !important;
        }}
        div[data-testid="stRadio"] > label:first-child {{
            display: none !important;
        }}

        /* Título de las secciones */
        .section-title {{
            text-align: center;
            color: {TEXT_MAROON};
            font-family: Georgia, serif;
            font-weight: 700;
            font-size: 1.8rem;
            margin-bottom: 1.5rem;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# MENÚ EN LA BARRA LATERAL (SIDEBAR)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div class="brand-title"><span class="color-flora">Flora</span><span class="color-vision">Vision</span></div>'
        '<div class="brand-underline"></div>',
        unsafe_allow_html=True,
    )

    # Control estricto del st.radio para evitar elements huérfanos arriba
    opcion_seleccionada = st.sidebar.radio(
        label="MenuSeleccion",
        options=["Principal", "Detección", "Inventario", "Dashboard"],
        label_visibility="collapsed"
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

    html = '<div style="max-width: 400px; margin: 0 auto;">'
    for porcentaje, color in barras:
        html += f"""
        <div style="
            width:100%;
            height:18px;
            background:{TRACK_GREY};
            border-radius:20px;
            margin-bottom:16px;
            overflow:hidden;
        ">
            <div style="
                width:{porcentaje}%;
                height:100%;
                background:{color};
                border-radius:20px;
            ">
            </div>
        </div>
        """
    html += '</div>'
    return html

# ---------------------------------------------------------------------------
# FUNCIONES DE RENDERIZADO DE PÁGINAS
# ---------------------------------------------------------------------------
def render_principal():
    """Slide 1: Pantalla de Bienvenida Oficial + Dashboard Resumen Semanal"""
    
    # Emoji del calendario centrado o alineado sutilmente
    st.markdown(
        """<div style="text-align: center; font-size: 3rem; margin-top: 10px; margin-bottom: 5px; user-select: none;">🗓️</div>""", 
        unsafe_allow_html=True
    )
    st.markdown('<div class="section-title">Resumen Semanal</div>', unsafe_allow_html=True)

    # Añadimos columnas extras en los extremos para encoger y centrar el contenido visual
    _, col_izquierda, col_derecha, _ = st.columns([0.5, 1, 1, 0.5])
    
    with col_izquierda:
        labels = ["Sanas", "En riesgo", "Enfermas"]
        values = [35, 35, 30]
        colors = [PINK, GOLD, MAROON]

        # Reducido el tamaño del gráfico con figsize=(2.5, 2.5)
        fig, ax = plt.subplots(figsize=(2.5, 2.5), subplot_kw=dict(aspect="equal"))
        ax.pie(
            values, 
            colors=colors, 
            startangle=90, 
            counterclock=False,
            wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2)
        )
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')
        st.pyplot(fig, clear_figure=True, use_container_width=False)
        
    with col_derecha:
        # Espaciador vertical interno para alinear las barras con la dona pequeña
        st.markdown('<div style="height: 15px;"></div>', unsafe_allow_html=True)
        st.markdown(progress_bars(), unsafe_allow_html=True)


def render_deteccion():
    """Slide 2: Módulo de Detección Inteligente (Subida de fotos)"""
    st.markdown(
        '<div class="section-title">Detección Inteligente</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("""
        <div style="
            background:white;
            border:12px solid #B98DA0;
            border-radius:25px;
            padding:25px;
        ">
        """, unsafe_allow_html=True)

        archivo = st.file_uploader(
            "Sube tu foto para análisis de detección",
            type=["jpg", "jpeg", "png"]
        )

        if archivo:
            st.image(archivo, use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="
            background:white;
            border:12px solid #B98DA0;
            border-radius:25px;
            padding:25px;
        ">
        """, unsafe_allow_html=True)

        st.subheader("Resultado")
        st.progress(78)
        st.success("Planta identificada")
        st.write("Enfermedad detectada: Mancha Foliar")
        st.info("Confianza del modelo: 78 %")
        st.write("Recomendación:")
        st.write("Aplicar tratamiento preventivo y continuar el monitoreo.")
        st.markdown("</div>", unsafe_allow_html=True)


def render_dashboard():
    """Slide 4: El Dashboard Estadístico General (Espacio disponible para métricas futuras)"""
    st.markdown('<div class="section-title">Métricas Históricas Generales</div>', unsafe_allow_html=True)
    
    st.markdown(
        f"""
        <div style="
            background-color: white; 
            border: 15px solid {CARD_BORDER}; 
            border-radius: 30px; 
            padding: 50px; 
            text-align: center;
            margin-top: 20px;
        ">
            <p style="color: {MAROON}; font-family: Georgia, serif; font-size: 1.2rem;">
                Próximamente: Gráficas de rendimiento histórico por lotes y tendencias temporales.
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )


def render_inventario():
    """Slide 3: Tabla de Inventario de Plantas"""
    st.markdown(
        '<div class="section-title">Inventario</div>',
        unsafe_allow_html=True
    )

    datos = {
        "Planta": ["Tomate", "Lechuga", "Pimiento", "Pepino"],
        "Cantidad": [45, 18, 32, 14],
        "Estado": ["Saludable", "Riesgo", "Saludable", "Enferma"]
    }

    st.dataframe(
        datos,
        use_container_width=True
    )

# ---------------------------------------------------------------------------
# CONTROLADOR / ENRUTADOR PRINCIPAL (Asignación de Vistas Reales)
# ---------------------------------------------------------------------------
if opcion_seleccionada == "Principal":
    render_principal()

elif opcion_seleccionada == "Detección":
    render_deteccion()

elif opcion_seleccionada == "Inventario":
    render_inventario()

elif opcion_seleccionada == "Dashboard":
    render_dashboard()