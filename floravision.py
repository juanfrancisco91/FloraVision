import streamlit as st
import matplotlib.pyplot as plt
import datetime
import sys
import os
import numpy as np
import textwrap

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
# IMPORTACIONES DEL BACKEND
# ---------------------------------------------------------------------------
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_CAPTURE_DIR = os.path.join(_BASE_DIR, "feature-capture")
if _CAPTURE_DIR not in sys.path:
    sys.path.insert(0, _CAPTURE_DIR)

try:
    from analisis_imagen import (
        analizar_marchitamiento,
        convertir_a_probabilidades,
        clasificar_flor_ia,
        hex_a_rangos_hsv,
        aprender_por_refuerzo,
    )
    VISION_DISPONIBLE = True
except ImportError:
    VISION_DISPONIBLE = False

    def hex_a_rangos_hsv(hex_str: str) -> dict:
        return {"h_min": 20, "h_max": 85, "s_min": 50, "s_max": 255, "v_min": 50, "v_max": 255}

import base64

def matriz_a_base64(imagen_np: np.ndarray, max_dim: int = 350) -> str:
    """Convierte un ndarray BGR/RGB de OpenCV a string Data URL Base64 para HTML/Card."""
    if imagen_np is None or imagen_np.size == 0:
        return ""
    try:
        if len(imagen_np.shape) == 3 and imagen_np.shape[2] == 4:
            img_bgr = cv2.cvtColor(imagen_np, cv2.COLOR_RGBA2BGR)
        elif len(imagen_np.shape) == 3 and imagen_np.shape[2] == 3:
            img_bgr = cv2.cvtColor(imagen_np, cv2.COLOR_RGB2BGR) if imagen_np.dtype == np.uint8 else imagen_np
        else:
            img_bgr = imagen_np

        h, w = img_bgr.shape[:2]
        if max(h, w) > max_dim:
            scale = max_dim / float(max(h, w))
            img_bgr = cv2.resize(img_bgr, (int(w * scale), int(h * scale)))

        _, buffer = cv2.imencode('.jpg', img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        b64_str = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{b64_str}"
    except Exception as e:
        print(f"⚠️ Error convirtiendo matriz a base64: {e}")
        return ""

IMAGENES_DEMO_FLORES = {
    "Rosa": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=400&q=80",
    "Orquídea": "https://images.unsplash.com/photo-1525310072745-f49212b5ac6d?auto=format&fit=crop&w=400&q=80",
    "Girasol": "https://images.unsplash.com/photo-1597848212624-a19eb35e2651?auto=format&fit=crop&w=400&q=80",
    "Tulipán": "https://images.unsplash.com/photo-1520763185298-1b434c919102?auto=format&fit=crop&w=400&q=80",
    "Margarita": "https://images.unsplash.com/photo-1606041008023-472dfb5e530f?auto=format&fit=crop&w=400&q=80",
    "Clavel": "https://images.unsplash.com/photo-1582794543139-8ac9cb0f7b11?auto=format&fit=crop&w=400&q=80",
    "Lirio": "https://images.unsplash.com/photo-1508610048659-a06b669e3321?auto=format&fit=crop&w=400&q=80",
}

from agentefloravision import AgenteFloraVision, PRECIOS_BASE

# Inicializar el agente como singleton de sesión
if "agente" not in st.session_state:
    st.session_state.agente = AgenteFloraVision()

if "ultimo_resultado" not in st.session_state:
    st.session_state.ultimo_resultado = None

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
BLANCO_TABLA = "#FFFFFF"

# Datos de inventario de demostración (se usan cuando el agente aún no tiene historial)
DATOS_INVENTARIO_DEMO = {
    "Planta": ["Rosa", "Orquídea", "Girasol", "Tulipán"],
    "Cantidad": [45, 18, 32, 14],
    "Estado": ["Saludable", "Riesgo", "Saludable", "Enferma"]
}

def _get_inventario():
    """Retorna datos del agente si tiene historial, o estructura vacía si inicia desde 0."""
    agente = st.session_state.agente
    if agente.historial:
        return agente.inventario_agrupado()
    return {
        "Planta": [],
        "Cantidad": [],
        "Estado": [],
        "Precio": [],
        "Descuento": [],
        "PorcentajeMarchito": [],
        "Imagen": [],
        "Timestamp": [],
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

        /* CUADRO MAESTRO DE INICIO Y CONTENEDORES: Estilizamos el st.container(border=True) nativo */
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

        /* ===================================================================
           SISTEMA INTEGRAL DE CONTRASTE Y TIPOGRAFÍA HIGH-CONTRAST
           =================================================================== */

        /* 1. TEXTO EN CONTENEDORES OSCUROS (Barra lateral, Banners IA, Cabeceras de tabla) */
        [data-testid="stSidebar"],
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] div,
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
        .dark-container, .dark-container *,
        .dark-card, .dark-card *,
        .ai-banner, .ai-banner * {{
            color: #FFFFFF !important;
        }}

        /* Excepción en barra lateral: Logo FloraVision y pastillas del menú con texto oscuro */
        div[data-testid="stRadio"] label p,
        div[data-testid="stRadio"] label span,
        div[data-testid="stRadio"] label div,
        .logo-btn-container p,
        .logo-btn-container div.stButton > button p,
        .logo-btn-container div.stButton > button span,
        .floravision-logo,
        .floravision-logo p {{
            color: {TEXT_MAROON} !important;
            -webkit-text-fill-color: {TEXT_MAROON} !important;
            font-weight: bold !important;
        }}

        /* Texto Dorado Acentuado en contenedores oscuros */
        .gold-accent, .dark-container .gold-accent, .ai-banner .gold-accent {{
            color: #FFE87C !important;
            font-weight: 800 !important;
        }}

        /* 2. TEXTO EN CONTENEDORES CLAROS (Cuerpo principal, Tarjetas blancas, Formularios) */
        .main, .main p, .main span, .main label, .main div,
        .block-container, .block-container p, .block-container span, .block-container label {{
            color: #5C0030;
        }}

        /* Tarjetas KPI y cuadros blancos */
        .kpi-card, .kpi-card * {{
            background-color: white !important;
            color: {TEXT_MAROON} !important;
        }}
        .kpi-title {{
            color: {TEXT_MAROON} !important;
            font-weight: bold !important;
        }}
        .kpi-value {{
            color: {TEXT_MAROON} !important;
            font-weight: 800 !important;
        }}
        .kpi-value-gold {{
            color: {GOLD} !important;
        }}

        /* Cabecera vs Filas de Tabla de Inventario */
        .custom-table th, .custom-table th * {{
            background-color: {MAROON} !important;
            color: #FFFFFF !important;
            font-weight: bold !important;
        }}
        .custom-table td, .custom-table td * {{
            background-color: #FFFFFF !important;
            color: #222222 !important;
        }}

        /* Badges de Inventario sobre blanco */
        .badge-saludable {{
            background-color: #E6F4EA !important;
            color: #137333 !important;
            font-weight: bold !important;
        }}
        .badge-riesgo {{
            background-color: #FEF7E0 !important;
            color: #B06000 !important;
            font-weight: bold !important;
        }}
        .badge-enferma {{
            background-color: #FCE8E6 !important;
            color: #C5221F !important;
            font-weight: bold !important;
        }}

        /* Selectbox y Dropdowns */
        [data-testid="stSelectbox"] label,
        [data-testid="stSelectbox"] div[data-baseweb="select"] span,
        [data-testid="stSelectbox"] div[data-baseweb="select"] div {{
            color: {TEXT_MAROON} !important;
            font-weight: 600 !important;
        }}
        [role="listbox"] li, [role="option"] {{
            color: {TEXT_MAROON} !important;
            background-color: #FFFFFF !important;
        }}

        /* Botones generales */
        div.stButton > button {{
            background-color: #FFFFFF !important;
            color: {TEXT_MAROON} !important;
            border: 2px solid {CARD_BORDER} !important;
            font-weight: bold !important;
        }}
        div.stButton > button:hover {{
            background-color: {CREAM} !important;
            color: {TEXT_MAROON} !important;
            border-color: {MAROON} !important;
        }}

        /* 5. Forzar fondo blanco y borde en File Uploader */
        [data-testid="stFileUploaderDropzone"] {{
            background-color: white !important;
            border: 2px dashed {CARD_BORDER} !important;
        }}

        .main-section-title {{
            text-align: center;
            color: {TEXT_MAROON};
            font-family: 'Georgia', serif;
            font-weight: 700;
            font-size: 1.8rem;
            margin-bottom: 2rem;
        }}

        .section-title {{
            color: {TEXT_MAROON};
            font-family: 'Georgia', serif;
            font-weight: 700;
            font-size: 2rem;
            margin-bottom: 2rem;
        }}

        /* ESTILO PARA CONTENEDOR DE FILA INFERIOR DEL DASHBOARD */
        .dashboard-box-light {{ 
            background-color: white !important; 
            border: 4px solid {CARD_BORDER} !important; 
            border-radius: 25px !important; 
            padding: 2rem !important; 
            height: 100% !important; 
            box-shadow: 0px 10px 30px rgba(0,0,0,0.02) !important;
        }}
        .dashboard-box-light * {{
            color: {TEXT_MAROON} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
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

    opciones_menu = ["Inicio", "Detección", "Entrenamiento IA", "Inventario", "Dashboard"]
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
    cantidades = _get_inventario()["Cantidad"]
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
        st.markdown('<div class="main-section-title">Resumen Semanal de FloraVision</div>', unsafe_allow_html=True)
        
        # Calcular los datos dinámicos del Inventario
        _inv = _get_inventario()
        cantidades = _inv["Cantidad"]
        estados    = _inv["Estado"]
        
        total_unidades = sum(cantidades)
        sanas = sum(cant for cant, est in zip(cantidades, estados) if est == "Saludable")
        riesgo = sum(cant for cant, est in zip(cantidades, estados) if est == "Riesgo")
        enfermas = sum(cant for cant, est in zip(cantidades, estados) if est == "Enferma")
        
        # 1. KPIs de Resumen Semanal en HTML (Alineado a la izquierda para evitar problemas con Markdown)
        kpis_html = f"""<div style="display: flex; gap: 20px; margin-bottom: 30px; justify-content: space-between; flex-wrap: wrap;">
    <div style="flex: 1; min-width: 150px; background-color: white; border: 4px solid {CARD_BORDER}; border-radius: 15px; padding: 15px; text-align: center; box-shadow: 0px 4px 10px rgba(0,0,0,0.02);">
        <div style="font-family: 'Georgia', serif; font-weight: bold; font-size: 0.95rem; color: {TEXT_MAROON}; margin-bottom: 5px;">Registradas</div>
        <div style="font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 1.8rem; color: {TEXT_MAROON};">{total_unidades} <span style="font-size: 0.9rem; font-weight: normal;">uds</span></div>
    </div>
    <div style="flex: 1; min-width: 150px; background-color: white; border: 4px solid {CARD_BORDER}; border-radius: 15px; padding: 15px; text-align: center; box-shadow: 0px 4px 10px rgba(0,0,0,0.02);">
        <div style="font-family: 'Georgia', serif; font-weight: bold; font-size: 0.95rem; color: {TEXT_MAROON}; margin-bottom: 5px;">Sanas</div>
        <div style="font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 1.8rem; color: #137333;">{sanas} <span style="font-size: 0.9rem; font-weight: normal;">uds</span></div>
    </div>
    <div style="flex: 1; min-width: 150px; background-color: white; border: 4px solid {CARD_BORDER}; border-radius: 15px; padding: 15px; text-align: center; box-shadow: 0px 4px 10px rgba(0,0,0,0.02);">
        <div style="font-family: 'Georgia', serif; font-weight: bold; font-size: 0.95rem; color: {TEXT_MAROON}; margin-bottom: 5px;">Enfermas / Marchitas</div>
        <div style="font-family: 'Montserrat', sans-serif; font-weight: 800; font-size: 1.8rem; color: #C5221F;">{enfermas} <span style="font-size: 0.9rem; font-weight: normal;">uds</span></div>
    </div>
</div>"""
        st.markdown(kpis_html, unsafe_allow_html=True)
        
        # 2. Barra de distribución y progreso en HTML
        pct_sanas = int((sanas / total_unidades) * 100) if total_unidades > 0 else 0
        pct_riesgo = int((riesgo / total_unidades) * 100) if total_unidades > 0 else 0
        pct_enfermas = 100 - pct_sanas - pct_riesgo if total_unidades > 0 else 0
        
        st.write("**Distribución del Estado de las Plantas:**")
        distribucion_html = f"""<div style="width:100%; height:24px; background:{TRACK_GREY}; border-radius:12px; display:flex; overflow:hidden; margin-bottom: 10px; box-shadow: inset 0px 1px 3px rgba(0,0,0,0.1);">
    <div style="width:{pct_sanas}%; height:100%; background:#F6A8C9;" title="Saludable ({pct_sanas}%)"></div>
    <div style="width:{pct_riesgo}%; height:100%; background:#C9A227;" title="Riesgo ({pct_riesgo}%)"></div>
    <div style="width:{pct_enfermas}%; height:100%; background:#5C0030;" title="Enferma ({pct_enfermas}%)"></div>
</div>
<div style="display: flex; gap: 20px; font-family: 'Georgia', serif; font-size: 0.9rem; color: {TEXT_MAROON}; margin-bottom: 30px; flex-wrap: wrap;">
    <div style="display: flex; align-items: center; gap: 6px;">
        <div style="width: 12px; height: 12px; background-color: #F6A8C9; border-radius: 50%;"></div>
        <span>Sana ({sanas} uds - {pct_sanas}%)</span>
    </div>
    <div style="display: flex; align-items: center; gap: 6px;">
        <div style="width: 12px; height: 12px; background-color: #C9A227; border-radius: 50%;"></div>
        <span>En Riesgo ({riesgo} uds - {pct_riesgo}%)</span>
    </div>
    <div style="display: flex; align-items: center; gap: 6px;">
        <div style="width: 12px; height: 12px; background-color: #5C0030; border-radius: 50%;"></div>
        <span>Enferma/Marchita ({enfermas} uds - {pct_enfermas}%)</span>
    </div>
</div>"""
        st.markdown(distribucion_html, unsafe_allow_html=True)


def render_deteccion():
    import cv2
    st.markdown('<div class="section-title">Deteccion Inteligente</div>', unsafe_allow_html=True)

    agente = st.session_state.agente
    flores_disponibles = [f.capitalize() for f in list(PRECIOS_BASE.keys())]

    # ------------------------------------------------------------------
    # COLUMNA IZQUIERDA: Controles (replica los trackbars de cv_taskbar.py)
    # ------------------------------------------------------------------
    col_ctrl, col_vista = st.columns([1, 1.4])

    with col_ctrl:
        with st.container(border=True):
            st.markdown(f'<div style="font-family:Georgia,serif;font-weight:bold;font-size:1rem;color:{TEXT_MAROON};margin-bottom:4px;">Tipo de Flor</div>', unsafe_allow_html=True)
            st.caption("&#129302; La IA identificará la flor automáticamente al cargar la foto. También puedes seleccionarla manualmente.")
            tipo_flor = st.selectbox(
                "Tipo de Flor",
                flores_disponibles,
                index=0,
                key="selectbox_flor",
                label_visibility="collapsed",
            )

            st.divider()

            # Rueda de colores automática en vez de 6 sliders HSV
            st.markdown(f'<div style="font-family:Georgia,serif;font-weight:bold;font-size:1rem;color:{TEXT_MAROON};margin-bottom:4px;">Color de la Flor (Pétalos Sanos)</div>', unsafe_allow_html=True)
            st.caption("Toca el círculo para elegir el color exacto. El sistema calibrará los parámetros de detección automáticamente.")

            if "color_seleccionado" not in st.session_state:
                st.session_state.color_seleccionado = "#E60000"
            if "cp_flor" not in st.session_state:
                st.session_state["cp_flor"] = st.session_state.color_seleccionado

            col_picker, col_info = st.columns([1, 2.2])
            with col_picker:
                color_elegido = st.color_picker(
                    "Seleccionar color",
                    value=st.session_state.color_seleccionado,
                    key="cp_flor",
                    label_visibility="collapsed",
                )
                st.session_state.color_seleccionado = color_elegido

            with col_info:
                st.markdown(f"""<div style="display:flex; align-items:center; gap:8px; margin-top:10px;">
                    <div style="width:22px; height:22px; border-radius:50%; background-color:{color_elegido}; border:2px solid {CARD_BORDER}; box-shadow: 0 2px 4px rgba(0,0,0,0.15);"></div>
                    <span style="font-family:Georgia,serif; font-weight:bold; font-size:0.95rem; color:{TEXT_MAROON};">{color_elegido.upper()}</span>
                </div>""", unsafe_allow_html=True)

            # Presets visuales rápidos de colores comunes de flores
            st.markdown(f'<div style="font-size:0.8rem; font-weight:bold; color:{TEXT_MAROON}; margin-top:12px; margin-bottom:6px;">Presets Rápidos de Flor:</div>', unsafe_allow_html=True)
            preset_cols = st.columns(5)
            presets = [
                ("🌹 Rojo", "#E60000", "p_rojo"),
                ("🌻 Amarillo", "#FBC02D", "p_amarillo"),
                ("🌸 Rosa", "#EC407A", "p_rosa"),
                ("💜 Violeta", "#8E24AA", "p_violeta"),
                ("🧡 Naranja", "#FB8C00", "p_naranja"),
            ]

            def _cb_aplicar_preset(hex_val):
                st.session_state.color_seleccionado = hex_val
                st.session_state["cp_flor"] = hex_val

            for col_p, (label, hex_val, key_p) in zip(preset_cols, presets):
                with col_p:
                    st.button(
                        label.split()[0],
                        key=key_p,
                        help=label,
                        on_click=_cb_aplicar_preset,
                        args=(hex_val,),
                    )

            # Ajuste automático por detrás (rango HSV calculado en backend)
            rangos = hex_a_rangos_hsv(st.session_state.color_seleccionado)
            h_min = rangos["h_min"]
            h_max = rangos["h_max"]
            s_min = rangos["s_min"]
            s_max = rangos["s_max"]
            v_min = rangos["v_min"]
            v_max = rangos["v_max"]

            # Variables locales de rangos HSV accesibles en todo render_deteccion
            h_min_v = h_min
            h_max_v = h_max
            s_min_v = s_min
            s_max_v = s_max
            v_min_v = v_min
            v_max_v = v_max
            pct_preview = 0.0

            st.session_state.hsv_vals = rangos

            st.divider()

            metodo_entrada = st.radio(
                "Metodo de entrada:",
                ["Subir archivo", "Usar camara"],
                horizontal=True,
            )

            if "imagen_actual" not in st.session_state:
                st.session_state.imagen_actual = None
            if "ultimo_metodo" not in st.session_state:
                st.session_state.ultimo_metodo = metodo_entrada

            if st.session_state.ultimo_metodo != metodo_entrada:
                st.session_state.imagen_actual = None
                st.session_state.ultimo_metodo = metodo_entrada

            if metodo_entrada == "Subir archivo":
                archivo = st.file_uploader(
                    "Sube una foto para analisis",
                    type=["jpg", "jpeg", "png"],
                    key="uploader_foto",
                )
                if archivo is not None:
                    try:
                        bytes_data = archivo.getvalue()
                        if len(bytes_data) > 0:
                            img_decoded = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                            if img_decoded is not None:
                                st.session_state.imagen_actual = img_decoded
                    except Exception:
                        pass
            else:
                imagen_camara = st.camera_input("Captura con la camara", key="camara_foto")
                if imagen_camara is not None:
                    try:
                        bytes_data = imagen_camara.getvalue()
                        if len(bytes_data) > 0:
                            img_decoded = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)
                            if img_decoded is not None:
                                st.session_state.imagen_actual = img_decoded
                    except Exception:
                        pass

            if st.session_state.imagen_actual is not None:
                if st.button("🗑️ Quitar / Cambiar Imagen", key="btn_quitar_foto"):
                    st.session_state.imagen_actual = None
                    st.rerun()

            imagen_np = st.session_state.imagen_actual

            analizar_btn = st.button(
                "Analizar Marchitamiento",
                disabled=(imagen_np is None),
                use_container_width=True,
                key="btn_analizar",
            )

    # ------------------------------------------------------------------
    # COLUMNA DERECHA: Vista previa de mascaras e Identificación IA
    # ------------------------------------------------------------------
    with col_vista:
        with st.container(border=True):
            if imagen_np is None:
                st.info("Carga una imagen para ver las mascaras y la clasificacion por IA en tiempo real.")
            else:
                # Inferencia IA en tiempo real al subir imagen
                res_ia_preview = clasificar_flor_ia(imagen_np) if VISION_DISPONIBLE else {"modelo_activo": False}
                if res_ia_preview.get("modelo_activo"):
                    especie_ia = res_ia_preview.get("especie", "Desconocida")
                    confianza_ia = res_ia_preview.get("confianza", 0.0)
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, {MAROON} 0%, {MAROON_DARK} 100%); color: white; padding: 14px 20px; border-radius: 12px; margin-bottom: 14px; box-shadow: 0 4px 12px rgba(92,0,48,0.25);">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span style="font-size:0.78rem; letter-spacing:1px; opacity:0.9; text-transform:uppercase; color:#E2DFDF;">&#129302; Identificación por Modelo IA (MobileNetV2)</span>
                                <div style="font-family:'Montserrat',sans-serif; font-size:1.35rem; font-weight:800; color:#FFFFFF; text-shadow:0px 2px 4px rgba(0,0,0,0.3); margin-top:3px;">
                                    Flor Detectada: <span style="color:#FFE87C;">{especie_ia}</span>
                                </div>
                            </div>
                            <div style="text-align:right;">
                                <span style="font-size:0.78rem; opacity:0.9; color:#E2DFDF;">Confianza IA</span>
                                <div style="font-family:'Montserrat',sans-serif; font-size:1.35rem; font-weight:800; color:#FFE87C; text-shadow:0px 2px 4px rgba(0,0,0,0.3); margin-top:3px;">{confianza_ia}%</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # ----- Replicar exactamente la logica de cv_taskbar.py -----
                h_min_v = h_min
                h_max_v = h_max
                s_min_v = s_min
                s_max_v = s_max
                v_min_v = v_min
                v_max_v = v_max

                hsv = cv2.cvtColor(imagen_np, cv2.COLOR_BGR2HSV)
                _, S, _ = cv2.split(hsv)

                # 1. Máscara de pétalos sanos (color seleccionado)
                if h_min_v <= h_max_v:
                    bajo  = np.array([h_min_v, s_min_v, v_min_v])
                    alto  = np.array([h_max_v, s_max_v, v_max_v])
                    mascara_petalos = cv2.inRange(hsv, bajo, alto)
                else:
                    # Modo dual rojo
                    m1 = cv2.inRange(hsv, np.array([0,       s_min_v, v_min_v]), np.array([h_max_v, s_max_v, v_max_v]))
                    m2 = cv2.inRange(hsv, np.array([h_min_v, s_min_v, v_min_v]), np.array([179,     s_max_v, v_max_v]))
                    mascara_petalos = cv2.bitwise_or(m1, m2)

                # 2. Máscara de hojas y tallo sanos (Verde en HSV: H: 35..85, S: 30..255, V: 30..255)
                mascara_hojas = cv2.inRange(hsv, np.array([35, 30, 30]), np.array([85, 255, 255]))

                # 3. Máscara sana total = Pétalos sanos + Hojas/Tallo sanos
                mascara_sana = cv2.bitwise_or(mascara_petalos, mascara_hojas)

                # Parte sana aislada
                resultado_sano = cv2.bitwise_and(imagen_np, imagen_np, mask=mascara_sana)

                # 4. Molde total de la flor/planta (Saturación y brillo significativos)
                s_suave = cv2.GaussianBlur(S, (7, 7), 0)
                _, gris_total = cv2.threshold(s_suave, 30, 255, cv2.THRESH_BINARY)
                kernel = np.ones((7, 7), np.uint8)
                gris_total = cv2.morphologyEx(gris_total, cv2.MORPH_CLOSE, kernel)

                # 5. Máscara marchita = molde de la planta − partes sanas
                mascara_marchita = cv2.bitwise_and(gris_total, cv2.bitwise_not(mascara_sana))

                # Contornos y areas (igual que cv_taskbar.py)
                frame_total = imagen_np.copy()
                frame_danio = imagen_np.copy()
                contornos_total,   _ = cv2.findContours(gris_total,       cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contornos_marchito, _ = cv2.findContours(mascara_marchita, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                area_total   = float(np.count_nonzero(gris_total))
                area_marchita = float(np.count_nonzero(mascara_marchita))
                pct_preview  = min(100.0, max(0.0, (area_marchita / area_total * 100.0))) if area_total > 0 else 0.0

                cv2.drawContours(frame_total, contornos_total,    -1, (0, 255, 0), 2)
                cv2.drawContours(frame_danio, contornos_marchito, -1, (0, 0, 255), 2)
                cv2.putText(frame_danio, f"Danio: {pct_preview:.1f}%", (20, 40),
                            cv2.FONT_HERSHEY_COMPLEX, 1.0, (0, 0, 255), 2)

                # Convertir BGR -> RGB para Streamlit
                def bgr2rgb(img): return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # Mostrar las 4 vistas como cv_taskbar.py (2x2)
                st.markdown(f'<div style="font-family:Georgia,serif;font-weight:bold;font-size:0.95rem;color:{TEXT_MAROON};margin-bottom:6px;">Vista de Mascaras en Tiempo Real</div>', unsafe_allow_html=True)
                r1c1, r1c2 = st.columns(2)
                with r1c1:
                    st.markdown(f'<div style="font-size:0.8rem;color:{TEXT_MAROON};font-weight:bold;">1. Original</div>', unsafe_allow_html=True)
                    st.image(bgr2rgb(imagen_np), use_container_width=True)
                with r1c2:
                    st.markdown(f'<div style="font-size:0.8rem;color:{TEXT_MAROON};font-weight:bold;">2. Parte Sana Aislada</div>', unsafe_allow_html=True)
                    st.image(bgr2rgb(resultado_sano), use_container_width=True)

                r2c1, r2c2 = st.columns(2)
                with r2c1:
                    st.markdown(f'<div style="font-size:0.8rem;color:{TEXT_MAROON};font-weight:bold;">3. Molde Flor Completa</div>', unsafe_allow_html=True)
                    st.image(bgr2rgb(frame_total), use_container_width=True)
                with r2c2:
                    st.markdown(f'<div style="font-size:0.8rem;color:{TEXT_MAROON};font-weight:bold;">4. Marchitamiento Detectado</div>', unsafe_allow_html=True)
                    st.image(bgr2rgb(frame_danio), use_container_width=True)

                st.markdown(
                    f'<div style="text-align:center;font-size:1.6rem;font-weight:800;'
                    f'color:{TEXT_MAROON};font-family:Montserrat,sans-serif;margin-top:8px;">'
                    f'{pct_preview:.1f}% <span style="font-size:1rem;font-weight:normal;">marchitamiento (vista previa)</span></div>',
                    unsafe_allow_html=True,
                )

    # ------------------------------------------------------------------
    # BOTÓN ANALIZAR — ejecuta el pipeline completo del agente + IA
    # ------------------------------------------------------------------
    if analizar_btn and imagen_np is not None:
        with st.spinner("Procesando visión por computadora e inferencia con IA..."):
            res_ia = clasificar_flor_ia(imagen_np) if VISION_DISPONIBLE else {"modelo_activo": False}

            # Si la IA identifica la flor con confianza > 40%, usamos esa especie automáticamente
            tipo_evaluado = tipo_flor
            if res_ia.get("modelo_activo") and res_ia.get("confianza", 0) > 40:
                especie_ia = res_ia["especie"].lower()
                if especie_ia in PRECIOS_BASE:
                    tipo_evaluado = especie_ia

            # Utilizar el porcentaje exacto ya calculado en la vista previa de OpenCV para garantizar consistencia 100%
            pct_marchito = pct_preview

            probs = convertir_a_probabilidades(pct_marchito)
            img_b64 = matriz_a_base64(imagen_np)
            resultado_agente = agente.percibir(tipo_evaluado.lower(), probs, cantidad=1, imagen_b64=img_b64)
            if resultado_agente:
                resultado_agente["porcentaje_marchito"] = pct_marchito
                resultado_agente["resultado_ia"] = res_ia
                resultado_agente["imagen_np"] = imagen_np
                st.session_state.ultimo_resultado = resultado_agente
                st.rerun()

    # ------------------------------------------------------------------
    # PANEL DE RESULTADO DEL AGENTE
    # ------------------------------------------------------------------
    res = st.session_state.ultimo_resultado
    if res is not None:
        with st.container(border=True):
            st.subheader("Resultado del Analisis")
            pct       = res.get("porcentaje_marchito", 0)
            estado    = res.get("estado", "Fresca")
            badge     = res.get("badge", "Saludable")
            precio_final = res.get("precio_final", 0)
            descuento = res.get("descuento", 0)
            recomendacion = res.get("recomendacion", "")
            tipo      = res.get("tipo_flor", "")
            ts        = res.get("timestamp", "")
            res_ia    = res.get("resultado_ia", {})

            # Si el modelo de IA está activo, mostrar tarjeta con la predicción de especie y confianza
            if res_ia.get("modelo_activo"):
                badge_corregido = " <span style='background:#C9A227; color:#5C0030; font-size:0.75rem; padding:2px 8px; border-radius:10px;'>🧠 Corregido por Refuerzo</span>" if res_ia.get("corregido_por_refuerzo") else ""
                st.markdown(textwrap.dedent(f"""
                <div style="background: linear-gradient(135deg, {MAROON} 0%, {MAROON_DARK} 100%); color: white; padding: 14px 20px; border-radius: 12px; margin-top: 6px; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(92,0,48,0.25);">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="font-size:0.78rem; letter-spacing:1px; opacity:0.9; text-transform:uppercase; color:#E2DFDF;">&#129302; Modelo IA (MobileNetV2 / Transfer Learning)</span>
                            <div style="font-family:'Montserrat',sans-serif; font-size:1.35rem; font-weight:800; color:#FFFFFF; text-shadow:0px 2px 4px rgba(0,0,0,0.3); margin-top:3px;">
                                Especie Detectada por IA: <span style="color:#FFE87C;">{res_ia.get('especie')}</span>{badge_corregido}
                            </div>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-size:0.78rem; opacity:0.9; color:#E2DFDF;">Confianza IA</span>
                            <div style="font-family:'Montserrat',sans-serif; font-size:1.35rem; font-weight:800; color:#FFE87C; text-shadow:0px 2px 4px rgba(0,0,0,0.3); margin-top:3px;">{res_ia.get('confianza')}%</div>
                        </div>
                    </div>
                </div>
                """), unsafe_allow_html=True)

            badge_color_map = {
                "Saludable": ("#E6F4EA", "#137333"),
                "Riesgo":    ("#FEF7E0", "#B06000"),
                "Enferma":   ("#FCE8E6", "#C5221F"),
            }
            bg, fg = badge_color_map.get(badge, ("#E6F4EA", "#137333"))

            c_badge, c_pct = st.columns([1, 1])
            with c_badge:
                st.markdown(
                    f'<span style="background:{bg};color:{fg};padding:6px 16px;border-radius:20px;'
                    f'font-weight:bold;font-size:0.95rem;">{badge} — {tipo}</span>',
                    unsafe_allow_html=True,
                )
            with c_pct:
                st.markdown(
                    f'<div style="text-align:right;font-size:1.4rem;font-weight:800;color:{TEXT_MAROON};'
                    f'font-family:Montserrat,sans-serif;">{pct:.1f}% marchitamiento</div>',
                    unsafe_allow_html=True,
                )

            st.progress(min(int(pct), 100))
            st.markdown(
                f'<div style="font-size:1rem;color:{TEXT_MAROON};margin-top:8px;">'
                f'<b>Estado:</b> {estado}</div>',
                unsafe_allow_html=True,
            )

            if descuento > 0 and descuento < 100:
                st.markdown(
                    f'<div style="font-size:1rem;color:{TEXT_MAROON};">'
                    f'<b>Precio con descuento ({descuento}%):</b> RD$ {precio_final:.2f}</div>',
                    unsafe_allow_html=True,
                )
            elif descuento == 0:
                st.markdown(
                    f'<div style="font-size:1rem;color:{TEXT_MAROON};">'
                    f'<b>Precio normal:</b> RD$ {precio_final:.2f}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div style="font-size:1rem;color:#C5221F;">'
                    f'<b>Flor no apta para venta — Retirar del inventario</b></div>',
                    unsafe_allow_html=True,
                )

            st.markdown(
                f'<div style="margin-top:10px;font-size:0.95rem;color:{TEXT_MAROON};">'
                f'{recomendacion}</div>',
                unsafe_allow_html=True,
            )
            st.caption(f"Analisis realizado a las {ts}")

            # ------------------------------------------------------------------
            # SECCIÓN DE APRENDIZAJE POR REFUERZO / CORRECCIÓN DE PREDICCIÓN
            # ------------------------------------------------------------------
            st.markdown('<div style="margin-top:16px;"></div>', unsafe_allow_html=True)
            with st.expander("🧠 ¿Predicción incorrecta / La IA se equivocó? Corregir y Entrenar por Refuerzo", expanded=False):
                st.markdown(
                    f'<div style="font-size:0.88rem; color:{TEXT_MAROON}; margin-bottom:8px;">'
                    'Si la IA predijo una flor equivocada, selecciona la especie real. El sistema aplicará '
                    '<b>Aprendizaje por Refuerzo (Reinforcement Fine-Tuning)</b> para actualizar inmediatamente '
                    'los pesos del modelo y recalcular los precios del inventario sin ingresar malas predicciones.</div>',
                    unsafe_allow_html=True
                )
                c_corr1, c_corr2 = st.columns([1.5, 1])
                with c_corr1:
                    especies_disp = ["Rosa", "Girasol", "Margarita", "Clavel", "Lirio", "Orquídea", "Tulipán"]
                    idx_def = especies_disp.index(tipo.capitalize()) if tipo.capitalize() in especies_disp else 0
                    especie_corregida = st.selectbox(
                        "Selecciona la especie correcta:",
                        especies_disp,
                        index=idx_def,
                        key="sel_especie_correcta"
                    )
                with c_corr2:
                    st.markdown('<div style="margin-top:28px;"></div>', unsafe_allow_html=True)
                    btn_refuerzo = st.button("🧠 Aplicar Refuerzo y Corregir", key="btn_aplica_refuerzo", use_container_width=True)

                if btn_refuerzo and "imagen_np" in res:
                    with st.spinner("Ejecutando actualización por refuerzo del modelo de IA..."):
                        resultado_refuerzo = aprender_por_refuerzo(res["imagen_np"], especie_corregida)
                        
                        nuevas_probs = convertir_a_probabilidades(pct)
                        nuevo_res = agente.percibir(
                            especie_corregida.lower(),
                            nuevas_probs,
                            cantidad=1,
                            imagen_b64=res.get("imagen_b64")
                        )
                        if nuevo_res:
                            nuevo_res["porcentaje_marchito"] = pct
                            nuevo_res["resultado_ia"] = {
                                "modelo_activo": True,
                                "especie": especie_corregida,
                                "confianza": 100.0,
                                "corregido_por_refuerzo": True
                            }
                            nuevo_res["imagen_np"] = res["imagen_np"]
                            agente.registrar_feedback(
                                res_ia.get("especie", "Desconocida"),
                                especie_corregida,
                                loss=resultado_refuerzo.get("loss", 0.0)
                            )
                            st.session_state.ultimo_resultado = nuevo_res
                            st.toast(f"🧠 ¡Refuerzo exitoso! Flor corregida a {especie_corregida}")
                            st.success(f"✅ {resultado_refuerzo.get('mensaje')}")
                            st.rerun()

            st.markdown('<div style="margin-top:14px;"></div>', unsafe_allow_html=True)
            col_b1, col_b2, col_b3 = st.columns([1.2, 1.2, 1])
            with col_b1:
                if st.button("➕ Agregar al Inventario", key="btn_add_inv", use_container_width=True):
                    st.session_state.agente.actuar(res)
                    st.success(f"✅ {tipo} ({estado}) guardada en el inventario.")
                    st.toast(f"🌸 {tipo} añadida al inventario")
            with col_b2:
                if st.button("🚫 Descartar Mala Predicción", key="btn_discard", use_container_width=True):
                    st.session_state.ultimo_resultado = None
                    st.toast("❌ Predicción descartada — No se incluyó en el inventario")
                    st.rerun()
            with col_b3:
                if st.button("🔄 Nueva Detección", key="btn_reset", use_container_width=True):
                    st.session_state.ultimo_resultado = None
                    st.rerun()


def normalizar_especie_y_foto(tipo_raw: str, imagen_b64: str | None = None) -> tuple[str, str]:
    """
    Normaliza nombres de especies con errores o plurales (ej. 'erosa' -> 'Rosa', 'girasoles' -> 'Girasol')
    y garantiza una URL/Base64 de foto 100% válida sin romper el layout gráfico.
    """
    clean = tipo_raw.strip().lower() if tipo_raw else "rosa"
    mapeo = {
        "erosa": "Rosa",
        "rosa": "Rosa",
        "rosas": "Rosa",
        "girasol": "Girasol",
        "girasoles": "Girasol",
        "margarita": "Margarita",
        "margaritas": "Margarita",
        "clavel": "Clavel",
        "claveles": "Clavel",
        "lirio": "Lirio",
        "lirios": "Lirio",
        "orquidea": "Orquídea",
        "orquídea": "Orquídea",
        "orquideas": "Orquídea",
        "tulipan": "Tulipán",
        "tulipán": "Tulipán",
        "tulipanes": "Tulipán",
    }
    especie_norm = mapeo.get(clean, tipo_raw.strip().capitalize() if tipo_raw else "Rosa")

    if imagen_b64 and isinstance(imagen_b64, str) and imagen_b64.startswith("data:image"):
        foto_url = imagen_b64
    else:
        foto_url = IMAGENES_DEMO_FLORES.get(especie_norm, IMAGENES_DEMO_FLORES["Rosa"])

    return especie_norm, foto_url


def render_inventario():
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        st.markdown('<div class="section-title">Inventario Floral Categorizado por Especie</div>', unsafe_allow_html=True)
    with col_t2:
        st.markdown('<div style="margin-top:6px;"></div>', unsafe_allow_html=True)
        if st.button("🗑️ Vaciar Inventario", key="btn_clear_all_inv", use_container_width=True):
            st.session_state.agente.vaciar_inventario()
            st.toast("🗑️ Inventario y base de datos reiniciados a 0")
            st.rerun()

    st.markdown(
        f'<div style="font-size:0.92rem; color:{TEXT_MAROON}; margin-bottom:18px;">'
        'Cada especie floral cuenta con su apartado propio. Presiona en cualquier flor para desplegar sus '
        '<b>divisiones de stock según su estado de salud (🟢 Sanas, 🟡 En Riesgo o 🔴 Enfermas)</b>.</div>',
        unsafe_allow_html=True
    )

    agente = st.session_state.agente
    raw_entries = agente.historial

    if not raw_entries:
        st.info("📦 **El inventario se encuentra actualmente vacío (0 tallos).**\n\nAnaliza o escanea flores en la pestaña de **Detección** y presiona **'➕ Agregar al Inventario'** para registrar stock real.")
        return

    # Agrupar por especie normalizada
    especies_dict: dict[str, dict] = {}
    for entrada in raw_entries:
        raw_flor = entrada.get("tipo_flor", "Rosa")
        especie_norm, foto_url = normalizar_especie_y_foto(raw_flor, entrada.get("imagen_b64"))

        if especie_norm not in especies_dict:
            especies_dict[especie_norm] = {
                "nombre": especie_norm,
                "foto_url": foto_url,
                "total_tallos": 0,
                "saludables": [],
                "riesgo": [],
                "enfermas": [],
            }

        if entrada.get("imagen_b64") and isinstance(entrada["imagen_b64"], str) and entrada["imagen_b64"].startswith("data:image"):
            especies_dict[especie_norm]["foto_url"] = entrada["imagen_b64"]

        cant = entrada.get("cantidad", 1)
        especies_dict[especie_norm]["total_tallos"] += cant

        badge = entrada.get("badge", "Saludable")
        if badge == "Saludable":
            especies_dict[especie_norm]["saludables"].append(entrada)
        elif badge == "Riesgo":
            especies_dict[especie_norm]["riesgo"].append(entrada)
        else:
            especies_dict[especie_norm]["enfermas"].append(entrada)

    # ------------------------------------------------------------------
    # BARRA DE FILTROS INTERACTIVOS POR ESPECIE Y ESTADO
    # ------------------------------------------------------------------
    with st.container():
        st.markdown(
            f'<div style="background-color:white; border:2px solid {CARD_BORDER}; border-radius:18px; padding:18px 24px; margin-bottom:20px; box-shadow:0 4px 14px rgba(0,0,0,0.04);">'
            f'<div style="font-family:\'Georgia\',serif; font-weight:bold; font-size:1.1rem; color:{TEXT_MAROON}; margin-bottom:12px;">'
            '🎛️ Filtros de Categorías Florales</div>',
            unsafe_allow_html=True
        )
        col_f1, col_f2, col_f3 = st.columns([1.5, 1.5, 1])
        with col_f1:
            filtro_busqueda = st.text_input("🌸 Buscar por Nombre de Flor", placeholder="ej. Rosa, Girasol...", key="inv_cat_busqueda")
        with col_f2:
            filtro_estado = st.selectbox("🔍 Filtrar por Presencia de Estado", ["Todas las Flores", "Con Sanas 🟢", "Con Riesgo 🟡", "Con Enfermas 🔴"], key="inv_cat_estado")
        with col_f3:
            st.markdown('<div style="margin-top:28px;"></div>', unsafe_allow_html=True)
            if st.button("🔄 Expandir / Colapsar Todo", key="btn_toggle_expand", use_container_width=True):
                st.session_state.expandir_todo = not st.session_state.get("expandir_todo", False)

    # Filtrar especies
    especies_filtradas = {}
    for esp_nombre, esp_datos in especies_dict.items():
        if filtro_busqueda.strip() and filtro_busqueda.strip().lower() not in esp_nombre.lower():
            continue
        if filtro_estado == "Con Sanas 🟢" and not esp_datos["saludables"]:
            continue
        if filtro_estado == "Con Riesgo 🟡" and not esp_datos["riesgo"]:
            continue
        if filtro_estado == "Con Enfermas 🔴" and not esp_datos["enfermas"]:
            continue
        especies_filtradas[esp_nombre] = esp_datos

    st.markdown(
        f'<div style="font-size:0.95rem; color:{TEXT_MAROON}; font-weight:bold; margin-bottom:16px;">'
        f'Mostrando {len(especies_filtradas)} categoría(s) de flores registradas</div>',
        unsafe_allow_html=True
    )

    if not especies_filtradas:
        st.warning("⚠️ No se encontraron especies que coincidan con los filtros.")
        return

    img_fallback_default = IMAGENES_DEMO_FLORES["Rosa"]
    expand_state = st.session_state.get("expandir_todo", False)

    # ------------------------------------------------------------------
    # SECCIONES POR CADA ESPECIE DE FLOR Y SUS SUBDIVISIONES INTERNAS
    # ------------------------------------------------------------------
    for esp_nombre, esp_datos in especies_filtradas.items():
        sanas_count = sum(it.get("cantidad", 1) for it in esp_datos["saludables"])
        riesgo_count = sum(it.get("cantidad", 1) for it in esp_datos["riesgo"])
        enfermas_count = sum(it.get("cantidad", 1) for it in esp_datos["enfermas"])
        total_count = esp_datos["total_tallos"]
        foto_src = esp_datos["foto_url"]

        iconos_flor = {
            "Rosa": "🌹", "Girasol": "🌻", "Orquídea": "🌸",
            "Tulipán": "🌷", "Margarita": "🌼", "Clavel": "🌺", "Lirio": "🪷"
        }
        icon_f = iconos_flor.get(esp_nombre, "🌸")

        with st.container():
            html_especie_card = f"""
            <div style="background-color:white; border:2px solid {CARD_BORDER}; border-radius:20px; padding:18px 24px; margin-top:14px; box-shadow:0 6px 16px rgba(0,0,0,0.05);">
                <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:16px;">
                    <div style="display:flex; align-items:center; gap:16px;">
                        <img src="{foto_src}" 
                             onerror="this.onerror=null; this.src='{img_fallback_default}';" 
                             style="width:85px; height:85px; object-fit:cover; border-radius:16px; border:2px solid {MAROON}; box-shadow:0 4px 10px rgba(0,0,0,0.08);" />
                        <div>
                            <div style="font-family:'Georgia',serif; font-size:1.5rem; font-weight:bold; color:{TEXT_MAROON};">
                                {icon_f} Apartado de {esp_nombre}
                            </div>
                            <div style="font-size:0.88rem; color:#555; margin-top:2px;">
                                Total acumulado en inventario: <b>{total_count} tallo(s)</b>
                            </div>
                        </div>
                    </div>
                    <div style="display:flex; gap:10px; flex-wrap:wrap;">
                        <span style="background:#E6F4EA; color:#137333; padding:6px 14px; border-radius:16px; font-weight:bold; font-size:0.85rem; border:1px solid #C3E6CB;">
                            🟢 {sanas_count} Sanas
                        </span>
                        <span style="background:#FEF7E0; color:#B06000; padding:6px 14px; border-radius:16px; font-weight:bold; font-size:0.85rem; border:1px solid #FFEBAA;">
                            🟡 {riesgo_count} En Riesgo
                        </span>
                        <span style="background:#FCE8E6; color:#C5221F; padding:6px 14px; border-radius:16px; font-weight:bold; font-size:0.85rem; border:1px solid #F5C6CB;">
                            🔴 {enfermas_count} Enfermas
                        </span>
                    </div>
                </div>
            </div>
            """
            st.markdown(textwrap.dedent(html_especie_card), unsafe_allow_html=True)

            # DESPLEGABLE CON LAS SUBDIVISIONES DE SALUD
            with st.expander(f"🔽 Presiona para ver las divisiones de estado (Sanas / Enfermas) de {esp_nombre}", expanded=expand_state):
                col_sub1, col_sub2, col_sub3 = st.columns(3)

                # 🟢 DIVISION 1: SANAS
                with col_sub1:
                    st.markdown(
                        textwrap.dedent(f"""
                        <div style="background:#F4FAF6; border:2px solid #A8DADC; border-radius:16px; padding:14px 16px; height:100%;">
                            <div style="font-family:'Georgia',serif; font-size:1.1rem; font-weight:bold; color:#137333; margin-bottom:8px;">
                                🟢 Division: Sanas ({sanas_count} uds)
                            </div>
                        """),
                        unsafe_allow_html=True
                    )
                    if esp_datos["saludables"]:
                        for item in esp_datos["saludables"]:
                            st.markdown(
                                textwrap.dedent(f"""
                                <div style="background:white; border-radius:12px; padding:12px; margin-bottom:8px; border:1px solid #C3E6CB; box-shadow:0 2px 6px rgba(0,0,0,0.03);">
                                    <div style="font-weight:bold; color:{TEXT_MAROON}; font-size:0.95rem;">
                                        Precio Normal: RD$ {item.get('precio_final', 50.0):.2f}
                                    </div>
                                    <div style="font-size:0.82rem; color:#444; margin-top:2px;">
                                        📦 Cantidad: <b>{item.get('cantidad', 1)} tallo(s)</b>
                                    </div>
                                    <div style="font-size:0.8rem; color:#137333; margin-top:2px;">
                                        Deterioro: {item.get('porcentaje_marchito', 0.0):.1f}% (Excelente)
                                    </div>
                                    <div style="font-size:0.75rem; color:#777; text-align:right; margin-top:4px;">
                                        🕒 {item.get('timestamp', '--:--')}
                                    </div>
                                </div>
                                """),
                                unsafe_allow_html=True
                            )
                    else:
                        st.caption("No hay stock en estado sano actualmente.")
                    st.markdown('</div>', unsafe_allow_html=True)

                # 🟡 DIVISION 2: RIESGO
                with col_sub2:
                    st.markdown(
                        textwrap.dedent(f"""
                        <div style="background:#FFFDF0; border:2px solid #FFE082; border-radius:16px; padding:14px 16px; height:100%;">
                            <div style="font-family:'Georgia',serif; font-size:1.1rem; font-weight:bold; color:#B06000; margin-bottom:8px;">
                                🟡 Division: En Riesgo ({riesgo_count} uds)
                            </div>
                        """),
                        unsafe_allow_html=True
                    )
                    if esp_datos["riesgo"]:
                        for item in esp_datos["riesgo"]:
                            st.markdown(
                                textwrap.dedent(f"""
                                <div style="background:white; border-radius:12px; padding:12px; margin-bottom:8px; border:1px solid #FFE58F; box-shadow:0 2px 6px rgba(0,0,0,0.03);">
                                    <div style="font-weight:bold; color:#B06000; font-size:0.95rem;">
                                        Precio con Descuento: RD$ {item.get('precio_final', 40.0):.2f}
                                    </div>
                                    <div style="font-size:0.82rem; color:#444; margin-top:2px;">
                                        📦 Cantidad: <b>{item.get('cantidad', 1)} tallo(s)</b>
                                    </div>
                                    <div style="font-size:0.8rem; color:#B06000; margin-top:2px;">
                                        Descuento Aplicado: <b>{item.get('descuento', 20)}% OFF</b>
                                    </div>
                                    <div style="font-size:0.8rem; color:#555;">
                                        Deterioro: {item.get('porcentaje_marchito', 0.0):.1f}%
                                    </div>
                                    <div style="font-size:0.75rem; color:#B06000; font-weight:bold; margin-top:4px;">
                                        ⚡ Recomendación: Vender hoy
                                    </div>
                                </div>
                                """),
                                unsafe_allow_html=True
                            )
                    else:
                        st.caption("No hay plantas en estado de riesgo.")
                    st.markdown('</div>', unsafe_allow_html=True)

                # 🔴 DIVISION 3: ENFERMAS / PERDIDA
                with col_sub3:
                    st.markdown(
                        textwrap.dedent(f"""
                        <div style="background:#FFF5F5; border:2px solid #FFCDD2; border-radius:16px; padding:14px 16px; height:100%;">
                            <div style="font-family:'Georgia',serif; font-size:1.1rem; font-weight:bold; color:#C5221F; margin-bottom:8px;">
                                🔴 Division: Enfermas ({enfermas_count} uds)
                            </div>
                        """),
                        unsafe_allow_html=True
                    )
                    if esp_datos["enfermas"]:
                        for item in esp_datos["enfermas"]:
                            st.markdown(
                                textwrap.dedent(f"""
                                <div style="background:white; border-radius:12px; padding:12px; margin-bottom:8px; border:1px solid #FFCDD2; box-shadow:0 2px 6px rgba(0,0,0,0.03);">
                                    <div style="font-weight:bold; color:#C5221F; font-size:0.95rem;">
                                        Flor No Apta para Venta
                                    </div>
                                    <div style="font-size:0.82rem; color:#444; margin-top:2px;">
                                        📦 Cantidad: <b>{item.get('cantidad', 1)} tallo(s)</b>
                                    </div>
                                    <div style="font-size:0.8rem; color:#C5221F; margin-top:2px;">
                                        Deterioro: {item.get('porcentaje_marchito', 0.0):.1f}% (Marchita)
                                    </div>
                                    <div style="font-size:0.75rem; color:#C5221F; font-weight:bold; margin-top:4px;">
                                        🚫 Acción: Retirar del inventario
                                    </div>
                                </div>
                                """),
                                unsafe_allow_html=True
                            )
                    else:
                        st.caption("No hay plantas enfermas actualmente.")
                    st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div style="margin-bottom:10px;"></div>', unsafe_allow_html=True)


def render_dashboard():
    """Slide 4: El Dashboard con Fondo Claro (Separación visual con la barra lateral)"""
    st.markdown('<div class="section-title">Dashboard FloraVision</div>', unsafe_allow_html=True)
    
    # Botón de Filtro Temporal Estilo Canva (Amarillo)
    st.markdown(f'<div style="display:inline-block; background-color:{GOLD}; color:{MAROON}; font-family:Georgia, serif; font-weight:bold; padding: 6px 16px; border-radius:8px; margin-bottom:20px; font-size:0.9rem;">Última Semana</div>', unsafe_allow_html=True)

    # 1. FILA DE METRICAS KPI SUPERIORES — datos reales del agente
    card_col1, card_col2, card_col3 = st.columns(3)
    datos = _get_inventario()
    reporte = st.session_state.agente.obtener_reporte_dict()
    cantidades = datos["Cantidad"]
    estados    = datos["Estado"]
    especies   = datos["Planta"]

    total_evaluados = reporte["total_tallos"] or sum(cantidades)
    enfermas_cnt    = estados.count("Enferma")
    frescas_cnt     = reporte["frescas"] or estados.count("Saludable")

    with card_col1:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Plantas Enfermas</div><div class="kpi-value">{enfermas_cnt}</div></div>', unsafe_allow_html=True)
    with card_col2:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Especies Registradas</div><div class="kpi-value kpi-value-gold">{len(especies)}</div></div>', unsafe_allow_html=True)
    with card_col3:
        st.markdown(f'<div class="kpi-card"><div class="kpi-title">Total Evaluados</div><div class="kpi-value">{total_evaluados}</div></div>', unsafe_allow_html=True)

    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
    
    # 2. SECCIÓN DE GRÁFICAS (Distribución de especies en monitoreo + Distribución de Salud en Stock)
    col_barras, col_dona = st.columns([1.2, 1])
    
    with col_barras:
        st.markdown(f'<div class="dashboard-box-light">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-family:\'Georgia\', serif; font-size:1.15rem; color:{TEXT_MAROON} !important; text-align:center; margin-bottom:15px; font-weight:bold;">Promedio de Especies en Monitoreo</div>', unsafe_allow_html=True)
        
        fig, ax = plt.subplots(figsize=(5, 3.2))
        palette = [MAROON, PINK, GOLD, CARD_BORDER, MAROON_DARK, "#E8B4CB"]
        colores_barras = [palette[i % len(palette)] for i in range(len(especies))]
        ax.bar(especies, cantidades, color=colores_barras, width=0.5, edgecolor="none")
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color((0.36, 0.0, 0.19, 0.4))
        ax.spines['bottom'].set_color((0.36, 0.0, 0.19, 0.4))
        ax.tick_params(colors=MAROON, labelsize=9)
        ax.grid(axis='y', linestyle='--', alpha=0.15, color=MAROON)
        fig.patch.set_facecolor('none')
        ax.set_facecolor('none')
        
        st.pyplot(fig, clear_figure=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_dona:
        st.markdown(f'<div class="dashboard-box-light">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-family:\'Georgia\', serif; font-size:1.15rem; color:{TEXT_MAROON} !important; text-align:center; margin-bottom:15px; font-weight:bold;">Distribución de Salud en Stock</div>', unsafe_allow_html=True)
        
        sanas_cnt   = estados.count("Saludable") or 1
        riesgo_cnt  = estados.count("Riesgo")
        enfermas_cnt_dona = estados.count("Enferma")
        
        fig2, ax2 = plt.subplots(figsize=(4.5, 3.2), subplot_kw=dict(aspect="equal"))
        labels_dona = ['Sana', 'Riesgo', 'Enferma']
        values_dona = [sanas_cnt, riesgo_cnt, enfermas_cnt_dona]
        colors_dona = [PINK, GOLD, MAROON]

        ax2.pie(values_dona, labels=labels_dona, colors=colors_dona, startangle=90,
                counterclock=False, autopct='%1.0f%%', pctdistance=0.72,
                textprops=dict(color=MAROON, weight="bold", size=9),
                wedgeprops=dict(width=0.42, edgecolor='white', linewidth=3))
        
        fig2.patch.set_facecolor('none')
        ax2.set_facecolor('none')
        
        st.pyplot(fig2, clear_figure=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
    
    # 3. SECCIÓN INFERIOR DE MONITOREO (Línea de Tendencia + Alertas de Salud)
    col_linea, col_alertas = st.columns([1.4, 1])
    
    with col_linea:
        st.markdown(f'<div class="dashboard-box-light">', unsafe_allow_html=True)
        st.markdown(f'<div style="font-family:\'Georgia\', serif; font-size:1.15rem; color:{TEXT_MAROON} !important; text-align:center; margin-bottom:15px; font-weight:bold;">Historial de Wilt Detections (Última Semana)</div>', unsafe_allow_html=True)
        
        # Si el agente tiene historial, usar timestamps reales del día
        historial = reporte.get("historial", [])
        if historial:
            from collections import Counter
            horas = [e["timestamp"][:5] for e in historial]  # HH:MM
            conteo_horas = Counter(horas)
            dias = list(conteo_horas.keys())
            detecciones = list(conteo_horas.values())
        else:
            dias = ["Lun", "Mar", "Mie", "Jue", "Vie"]
            detecciones = [3, 5, 2, 7, 4]
        
        fig3, ax3 = plt.subplots(figsize=(6, 3.1))
        ax3.plot(dias, detecciones, color=MAROON, marker='o', linewidth=3, markersize=8, markerfacecolor=GOLD, markeredgecolor=MAROON)
        
        ax3.spines['top'].set_visible(False)
        ax3.spines['right'].set_visible(False)
        ax3.spines['left'].set_color((0.36, 0.0, 0.19, 0.4))
        ax3.spines['bottom'].set_color((0.36, 0.0, 0.19, 0.4))
        ax3.tick_params(colors=MAROON, labelsize=9)
        ax3.grid(axis='both', linestyle='--', alpha=0.15, color=MAROON)
        ax3.set_ylabel("Marchitamientos Detectados", color=MAROON, fontfamily="Georgia", fontsize=9, weight="bold")
        fig3.patch.set_facecolor('none')
        ax3.set_facecolor('none')
        
        st.pyplot(fig3, clear_figure=True, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col_alertas:
        alertas_html = f"""<style>
.alert-box {{
    background-color: white;
    border: 4px solid {CARD_BORDER};
    border-radius: 20px;
    padding: 20px;
    height: 100%;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.02);
}}
.alert-item {{
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 0;
    border-bottom: 1px solid {TRACK_GREY};
}}
.alert-item:last-child {{
    border-bottom: none;
}}
.alert-dot {{
    width: 14px;
    height: 14px;
    border-radius: 50%;
    flex-shrink: 0;
}}
.alert-dot-red {{
    background-color: #C5221F !important;
}}
.alert-dot-yellow {{
    background-color: #C9A227 !important;
}}
.alert-title {{
    font-family: 'Montserrat', sans-serif;
    font-weight: bold;
    font-size: 0.95rem;
    color: {TEXT_MAROON} !important;
}}
.alert-text {{
    font-family: 'Georgia', serif;
    font-size: 0.85rem;
    color: #8C8C8C !important;
    margin: 2px 0 0 0;
}}
</style>
<div class="alert-box">
<div style="font-family: 'Georgia', serif; font-size: 1.15rem; color: {TEXT_MAROON} !important; font-weight: bold; margin-bottom: 15px;">Alertas Sanitarias Críticas</div>"""
        # Alertas reales del agente
        alertas_reales = reporte.get("alertas", [])
        if alertas_reales:
            for alerta_txt in alertas_reales:
                dot_class = "alert-dot-red" if "PÉRDIDA" in alerta_txt else "alert-dot-yellow"
                alertas_html += f"""
<div class="alert-item">
<div class="alert-dot {dot_class}"></div>
<div>
<div class="alert-title">{alerta_txt[:60]}</div>
<div class="alert-text">{alerta_txt}</div>
</div>
</div>"""
        else:
            # Alertas de demostración cuando el agente aún no tiene historial
            alertas_html += """
<div class="alert-item">
<div class="alert-dot alert-dot-red"></div>
<div>
<div class="alert-title">Tulipán - Infección Crítica</div>
<div class="alert-text">Marchitamiento detectado. Se recomienda aislamiento inmediato y control de humedad.</div>
</div>
</div>
<div class="alert-item">
<div class="alert-dot alert-dot-yellow"></div>
<div>
<div class="alert-title">Orquídea - En Riesgo</div>
<div class="alert-text">Estrés detectado. Aumentar frecuencia de monitoreo y regular la exposición solar.</div>
</div>
</div>"""
        alertas_html += """
</div>"""
        st.markdown(alertas_html, unsafe_allow_html=True)

def render_entrenamiento():
    import os, time, subprocess
    st.markdown('<div class="section-title">Entrenamiento de Modelo IA (feature/model-training)</div>', unsafe_allow_html=True)
    st.caption("Transfer Learning con MobileNetV2 / ResNet50, Data Augmentation y exportación de modelo entrenado (.h5 / .keras).")

    base_dir = _BASE_DIR
    h5_path = os.path.join(base_dir, "modelo_flores.h5")
    keras_path = os.path.join(base_dir, "modelo_flores.keras")
    plot_path = os.path.join(base_dir, "feature-training", "training_metrics.png")

    # 1. TARJETAS DE ESTADO DEL MODELO
    col_c1, col_c2, col_c3 = st.columns(3)
    
    modelo_existe = os.path.exists(keras_path) or os.path.exists(h5_path)
    if modelo_existe:
        active_path = keras_path if os.path.exists(keras_path) else h5_path
        mod_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(os.path.getmtime(active_path)))
        size_mb = round(os.path.getsize(active_path) / (1024 * 1024), 2)
        status_html = f'<div style="color:#137333; font-weight:bold;">✅ Modelo Activo ({size_mb} MB)</div><div style="font-size:0.8rem; color:#666;">Guardado: {mod_time}</div>'
    else:
        status_html = '<div style="color:#C5221F; font-weight:bold;">⚠️ Modelo No Encontrado</div><div style="font-size:0.8rem; color:#666;">Presiona iniciar entrenamiento abajo</div>'

    with col_c1:
        st.markdown(f"""
        <div style="background:white; border:2px solid {CARD_BORDER}; border-radius:14px; padding:16px; box-shadow:0 4px 10px rgba(0,0,0,0.03);">
            <div style="font-family:'Montserrat',sans-serif; font-size:0.85rem; color:{TEXT_MAROON}; font-weight:bold; text-transform:uppercase;">Estado de Modelo</div>
            <div style="font-family:'Georgia',serif; font-size:1.1rem; margin-top:8px;">{status_html}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_c2:
        st.markdown(f"""
        <div style="background:white; border:2px solid {CARD_BORDER}; border-radius:14px; padding:16px; box-shadow:0 4px 10px rgba(0,0,0,0.03);">
            <div style="font-family:'Montserrat',sans-serif; font-size:0.85rem; color:{TEXT_MAROON}; font-weight:bold; text-transform:uppercase;">Arquitectura Backbone</div>
            <div style="font-family:'Georgia',serif; font-size:1.1rem; font-weight:bold; color:{TEXT_MAROON}; margin-top:8px;">MobileNetV2 / ResNet50</div>
            <div style="font-size:0.8rem; color:#666;">Preentrenado en ImageNet (7 Clases)</div>
        </div>
        """, unsafe_allow_html=True)

    with col_c3:
        st.markdown(f"""
        <div style="background:white; border:2px solid {CARD_BORDER}; border-radius:14px; padding:16px; box-shadow:0 4px 10px rgba(0,0,0,0.03);">
            <div style="font-family:'Montserrat',sans-serif; font-size:0.85rem; color:{TEXT_MAROON}; font-weight:bold; text-transform:uppercase;">Data Augmentation</div>
            <div style="font-family:'Georgia',serif; font-size:1.1rem; font-weight:bold; color:{TEXT_MAROON}; margin-top:8px;">Flip, Rotate, Zoom, Contrast</div>
            <div style="font-size:0.8rem; color:#666;">Optimizador Adam + Early Stopping</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # 2. SECCIÓN DE MÉTRICAS Y CONTROL DE ENTRENAMIENTO
    col_ctrl, col_plot = st.columns([1, 1.2])

    with col_ctrl:
        with st.container(border=True):
            st.markdown(f'<div style="font-family:Georgia,serif; font-weight:bold; font-size:1.1rem; color:{TEXT_MAROON}; margin-bottom:12px;">Parámetros de Entrenamiento</div>', unsafe_allow_html=True)
            epochs_input = st.slider("Épocas de Entrenamiento", min_value=2, max_value=20, value=6, key="tr_epochs")
            batch_size_input = st.select_slider("Batch Size", options=[8, 16, 32], value=16, key="tr_batch")
            model_type_input = st.selectbox("Modelo Base (Backbone)", ["mobilenet", "resnet"], index=0, key="tr_model")
            
            btn_train = st.button("🚀 Ejecutar Entrenamiento de IA", use_container_width=True, key="btn_exec_train")
            
            if btn_train:
                with st.spinner("Entrenando IA con Transfer Learning y Fine-Tuning... Esto tomará unos segundos."):
                    env_python = os.path.join(base_dir, ".env", "Scripts", "python.exe")
                    if not os.path.exists(env_python):
                        env_python = sys.executable

                    script_path = os.path.join(base_dir, "feature-training", "train_model.py")
                    cmd = [
                        env_python, script_path,
                        "--epochs", str(epochs_input),
                        "--batch-size", str(batch_size_input),
                        "--model-type", model_type_input,
                        "--sample-dataset"
                    ]
                    
                    res = subprocess.run(cmd, capture_output=True, text=True)
                    if res.returncode == 0:
                        st.success("✅ ¡Modelo entrenado y exportado exitosamente a modelo_flores.h5 y modelo_flores.keras!")
                        import analisis_imagen
                        analisis_imagen._MODELO_IA_CACHE = None
                        st.rerun()
                    else:
                        st.error(f"Error durante el entrenamiento: {res.stderr}")

    with col_plot:
        with st.container(border=True):
            st.markdown(f'<div style="font-family:Georgia,serif; font-weight:bold; font-size:1.1rem; color:{TEXT_MAROON}; margin-bottom:12px;">Métricas del Modelo Guardado</div>', unsafe_allow_html=True)
            if os.path.exists(plot_path):
                st.image(plot_path, use_container_width=True, caption="Precisión (Accuracy) y Pérdida (Loss) durante Transfer Learning & Fine-Tuning")
            else:
                st.info("Ejecuta un entrenamiento para visualizar las curvas de rendimiento y métricas.")


# ---------------------------------------------------------------------------
# ENRUTADOR PRINCIPAL
# ---------------------------------------------------------------------------
if st.session_state.pagina_actual == "Inicio":
    render_inicio()
elif st.session_state.pagina_actual == "Detección":
    render_deteccion()
elif st.session_state.pagina_actual == "Entrenamiento IA":
    render_entrenamiento()
elif st.session_state.pagina_actual == "Inventario":
    render_inventario()
elif st.session_state.pagina_actual == "Dashboard":
    render_dashboard()