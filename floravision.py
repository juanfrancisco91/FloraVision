import streamlit as st
import matplotlib.pyplot as plt
import datetime
import sys
import os
import numpy as np

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
    from analisis_imagen import analizar_marchitamiento, convertir_a_probabilidades
    VISION_DISPONIBLE = True
except ImportError:
    VISION_DISPONIBLE = False

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
    """Retorna datos del agente si tiene historial, o los datos demo."""
    agente = st.session_state.agente
    if agente.historial:
        return agente.inventario_agrupado()
    return DATOS_INVENTARIO_DEMO

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
        div.stButton > button[key="btn_logo_home"] {{
            background: transparent !important;
            border: none !important;
            padding: 0 !important;
            width: 100% !important;
            text-align: left !important;
            box-shadow: none !important;
            display: block !important;
            font-family: 'Montserrat', sans-serif !important;
            font-size: 2.3rem !important;
            font-weight: 800 !important;
            letter-spacing: -0.5px !important;
            line-height: 1.1 !important;
            cursor: pointer !important;
            background: linear-gradient(90deg, {PINK} 0%, {PINK} 43%, {GOLD} 43%, {GOLD} 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
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

        /* 1. Forzar color de texto Maroon en absolutamente todos los elementos de la aplicación */
        * {{
            color: #5C0030 !important;
        }}
        
        /* 2. Exceptuar explícitamente los badges de inventario, la métrica de oro y cabeceras de tabla */
        .badge-saludable {{
            color: #137333 !important;
        }}
        .badge-riesgo {{
            color: #B06000 !important;
        }}
        .badge-enferma {{
            color: #C5221F !important;
        }}
        .kpi-value-gold {{
            color: {GOLD} !important;
        }}
        .custom-table th, .custom-table th * {{
            color: #FFFFFF !important;
        }}
        /* 3b. Selectbox: texto blanco en el valor seleccionado y las opciones del dropdown */
        [data-testid="stSelectbox"] div[data-baseweb="select"] div {{
            color: #FFFFFF !important;
        }}
        [data-testid="stSelectbox"] span {{
            color: #FFFFFF !important;
        }}
        [role="listbox"] li, [role="option"] {{
            color: {TEXT_MAROON} !important;
        }}
        
        /* 3. Forzar fondo blanco y borde lila en el cargador de archivos (File Uploader) */
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

        /* TARJETAS KPI GENERALES */
        .kpi-card {{
            background-color: white !important;
            border: 4px solid {CARD_BORDER} !important;
            border-radius: 20px !important;
            padding: 1.5rem !important;
            text-align: center !important;
        }}
        .kpi-title {{
            font-family: 'Georgia', serif !important;
            font-weight: bold !important;
            font-size: 1.1rem !important;
            color: {TEXT_MAROON} !important;
            margin-bottom: 0.5rem !important;
        }}
        .kpi-value {{
            font-family: 'Montserrat', sans-serif !important;
            font-weight: 800 !important;
            font-size: 2.2rem !important;
            color: {TEXT_MAROON} !important;
        }}
        .kpi-value-gold {{
            color: {GOLD} !important;
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
    st.button("FloraVision", key="btn_logo_home", on_click=ir_a_inicio)
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
            st.markdown(f'<div style="font-family:Georgia,serif;font-weight:bold;font-size:1rem;color:{TEXT_MAROON};margin-bottom:8px;">Tipo de Flor</div>', unsafe_allow_html=True)
            tipo_flor = st.selectbox(
                "Tipo de Flor",
                flores_disponibles,
                index=0,
                key="selectbox_flor",
                label_visibility="collapsed",
            )

            st.divider()

            # Sliders HSV — equivalentes exactos a los trackbars de cv_taskbar.py
            st.markdown(f'<div style="font-family:Georgia,serif;font-weight:bold;font-size:1rem;color:{TEXT_MAROON};margin-bottom:4px;">Mascara de Color (HSV)</div>', unsafe_allow_html=True)
            st.caption("Ajusta los rangos hasta aislar la parte sana de la flor.")

            # Inicializar valores HSV en un dict separado (NO en las mismas keys de los sliders)
            # Esto evita el error: "cannot be modified after the widget is instantiated"
            if "hsv_vals" not in st.session_state:
                st.session_state.hsv_vals = {
                    "h_min": 20, "h_max": 85,
                    "s_min": 50, "s_max": 255,
                    "v_min": 50, "v_max": 255,
                }

            hv = st.session_state.hsv_vals
            h_min = st.slider("H Min", 0,   179, hv["h_min"], key="sl_h_min")
            h_max = st.slider("H Max", 0,   179, hv["h_max"], key="sl_h_max")
            s_min = st.slider("S Min", 0,   255, hv["s_min"], key="sl_s_min")
            s_max = st.slider("S Max", 0,   255, hv["s_max"], key="sl_s_max")
            v_min = st.slider("V Min", 0,   255, hv["v_min"], key="sl_v_min")
            v_max = st.slider("V Max", 0,   255, hv["v_max"], key="sl_v_max")

            # Sincronizar hsv_vals con los valores actuales de los sliders
            st.session_state.hsv_vals = {
                "h_min": h_min, "h_max": h_max,
                "s_min": s_min, "s_max": s_max,
                "v_min": v_min, "v_max": v_max,
            }

            # Preset Rojo — escribe en hsv_vals (no en las keys de los sliders)
            if st.button("Aplicar Preset Rojo", use_container_width=True, key="btn_preset_rojo"):
                st.session_state.hsv_vals = {
                    "h_min": 170, "h_max": 10,
                    "s_min": 50,  "s_max": 255,
                    "v_min": 50,  "v_max": 255,
                }
                st.rerun()

            st.divider()

            metodo_entrada = st.radio(
                "Metodo de entrada:",
                ["Subir archivo", "Usar camara"],
                horizontal=True,
            )

            imagen_np = None

            if metodo_entrada == "Subir archivo":
                archivo = st.file_uploader(
                    "Sube una foto para analisis",
                    type=["jpg", "jpeg", "png"],
                )
                if archivo:
                    bytes_data = archivo.read()
                    imagen_np = np.frombuffer(bytes_data, np.uint8)
                    imagen_np = cv2.imdecode(imagen_np, cv2.IMREAD_COLOR)
            else:
                imagen_camara = st.camera_input("Captura con la camara")
                if imagen_camara:
                    bytes_data = imagen_camara.getvalue()
                    imagen_np = np.frombuffer(bytes_data, np.uint8)
                    imagen_np = cv2.imdecode(imagen_np, cv2.IMREAD_COLOR)

            analizar_btn = st.button(
                "Analizar Marchitamiento",
                disabled=(imagen_np is None),
                use_container_width=True,
                key="btn_analizar",
            )

    # ------------------------------------------------------------------
    # COLUMNA DERECHA: Vista previa de mascaras (replica las 4 ventanas
    # de cv_taskbar.py: Original, Parte Sana, Molde Total, Marchitamiento)
    # ------------------------------------------------------------------
    with col_vista:
        with st.container(border=True):
            if imagen_np is None:
                st.info("Carga una imagen para ver las mascaras en tiempo real.")
            else:
                # ----- Replicar exactamente la logica de cv_taskbar.py -----
                # Los valores HSV vienen directamente de los sliders (ya son variables locales)
                h_min_v = h_min
                h_max_v = h_max
                s_min_v = s_min
                s_max_v = s_max
                v_min_v = v_min
                v_max_v = v_max

                hsv = cv2.cvtColor(imagen_np, cv2.COLOR_BGR2HSV)
                _, S, _ = cv2.split(hsv)

                # Mascara sana (parte del color seleccionado)
                if h_min_v <= h_max_v:
                    bajo  = np.array([h_min_v, s_min_v, v_min_v])
                    alto  = np.array([h_max_v, s_max_v, v_max_v])
                    mascara_sana = cv2.inRange(hsv, bajo, alto)
                else:
                    # Modo dual rojo
                    m1 = cv2.inRange(hsv, np.array([0,       s_min_v, v_min_v]), np.array([h_max_v, s_max_v, v_max_v]))
                    m2 = cv2.inRange(hsv, np.array([h_min_v, s_min_v, v_min_v]), np.array([179,     s_max_v, v_max_v]))
                    mascara_sana = cv2.bitwise_or(m1, m2)

                # Parte sana aislada
                resultado_sano = cv2.bitwise_and(imagen_np, imagen_np, mask=mascara_sana)

                # Molde total de la flor (umbral de saturacion + morfologia)
                s_suave = cv2.GaussianBlur(S, (7, 7), 0)
                _, gris_total = cv2.threshold(s_suave, 20, 255, cv2.THRESH_BINARY)
                kernel = np.ones((7, 7), np.uint8)
                gris_total = cv2.morphologyEx(gris_total, cv2.MORPH_CLOSE, kernel)

                # Mascara marchita = total - sana
                mascara_marchita = cv2.bitwise_and(gris_total, cv2.bitwise_not(mascara_sana))

                # Contornos y areas (igual que cv_taskbar.py)
                frame_total = imagen_np.copy()
                frame_danio = imagen_np.copy()
                contornos_total,   _ = cv2.findContours(gris_total,       cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contornos_marchito, _ = cv2.findContours(mascara_marchita, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                area_total   = sum(cv2.contourArea(c) for c in contornos_total    if cv2.contourArea(c) > 100)
                area_marchita = sum(cv2.contourArea(c) for c in contornos_marchito if cv2.contourArea(c) > 30)
                pct_preview  = (area_marchita / area_total * 100) if area_total > 0 else 0.0

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
    # BOTÓN ANALIZAR — ejecuta el pipeline completo del agente
    # ------------------------------------------------------------------
    if analizar_btn and imagen_np is not None:
        with st.spinner("Procesando con el agente..."):
            if VISION_DISPONIBLE:
                resultado_cv = analizar_marchitamiento(
                    imagen_np,
                    h_min=h_min_v, s_min=s_min_v, v_min=v_min_v,
                    h_max=h_max_v, s_max=s_max_v, v_max=v_max_v,
                )
                pct_marchito = resultado_cv["porcentaje_marchito"]
            else:
                pct_marchito = pct_preview

            probs = convertir_a_probabilidades(pct_marchito)
            resultado_agente = agente.percibir(tipo_flor.lower(), probs, cantidad=1)
            if resultado_agente:
                resultado_agente["porcentaje_marchito"] = pct_marchito
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

            if st.button("Nueva deteccion", key="btn_reset", use_container_width=True):
                st.session_state.ultimo_resultado = None
                st.rerun()


def render_inventario():
    st.markdown('<div class="section-title">Inventario</div>', unsafe_allow_html=True)
    
    # Construir tabla HTML/CSS personalizada (sin espacios al inicio para evitar que markdown lo interprete como código)
    html_tabla = f"""<style>
.custom-table-container {{
    background-color: white;
    border: 12px solid {CARD_BORDER};
    border-radius: 24px;
    padding: 30px 40px;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.04);
    margin-top: 10px;
}}
.custom-table {{
    width: 100%;
    border-collapse: collapse;
    font-family: 'Georgia', serif;
    color: {BLANCO_TABLA};
    font-size: 1.1rem;
}}
.custom-table th {{
    background-color: {MAROON};
    color: {BLANCO_TABLA};
    padding: 14px 20px;
    text-align: left;
    font-family: 'Montserrat', sans-serif;
    font-weight: 600;
    text-transform: uppercase;
    font-size: 0.9rem;
    letter-spacing: 0.5px;
}}
.custom-table th:first-child {{
    border-top-left-radius: 12px;
    border-bottom-left-radius: 12px;
}}
.custom-table th:last-child {{
    border-top-right-radius: 12px;
    border-bottom-right-radius: 12px;
}}
.custom-table td {{
    padding: 18px 20px;
    border-bottom: 1px solid {TRACK_GREY};
}}
.custom-table tr:last-child td {{
    border-bottom: none;
}}
.badge {{
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 0.85rem;
    display: inline-block;
}}
.badge-saludable {{
    background-color: #E6F4EA;
    color: #137333;
}}
.badge-riesgo {{
    background-color: #FEF7E0;
    color: #B06000;
}}
.badge-enferma {{
    background-color: #FCE8E6;
    color: #C5221F;
}}
</style>
<div class="custom-table-container">
    <table class="custom-table">
        <thead>
            <tr>
                <th>Planta</th>
                <th>Cantidad</th>
                <th>Estado</th>
            </tr>
        </thead>
        <tbody>"""
    
    datos = _get_inventario()
    tiene_precio = "Precio" in datos

    for i in range(len(datos["Planta"])):
        planta  = datos["Planta"][i]
        cantidad = datos["Cantidad"][i]
        estado  = datos["Estado"][i]

        if estado == "Saludable":
            badge_class = "badge-saludable"
        elif estado == "Riesgo":
            badge_class = "badge-riesgo"
        else:
            badge_class = "badge-enferma"

        precio_td = ""
        if tiene_precio:
            desc = datos["Descuento"][i]
            pf   = datos["Precio"][i]
            precio_td = f'<td>RD$ {pf:.2f}' + (f' <small>(-{desc}%)</small>' if desc > 0 else '') + '</td>'

        html_tabla += f"""
<tr>
<td style="font-weight: bold;">{planta}</td>
<td>{cantidad} unidades</td>
<td><span class="badge {badge_class}">{estado}</span></td>
{precio_td}
</tr>"""

    html_tabla += """
</tbody>
</table>
</div>"""
    # Agregar columna Precio al thead si hay datos reales
    if tiene_precio:
        html_tabla = html_tabla.replace(
            "<th>Estado</th>\n            </tr>",
            "<th>Estado</th>\n                <th>Precio Final</th>\n            </tr>",
        )
    st.markdown(html_tabla, unsafe_allow_html=True)


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