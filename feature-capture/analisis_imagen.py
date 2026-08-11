# -*- coding: utf-8 -*-
"""
analisis_imagen.py — FloraVision
Módulo de análisis de marchitamiento por visión por computadora.

Extrae la lógica HSV de cv_taskbar.py como función pura reutilizable
desde Streamlit sin ventanas OpenCV (no usa cv2.imshow ni VideoCapture).

Uso:
    from feature-capture.analisis_imagen import analizar_marchitamiento
    pct = analizar_marchitamiento(imagen_np)
"""

import cv2 as cv
import numpy as np


# ---------------------------------------------------------------------------
# Parámetros HSV predefinidos por tipo de estado de flor
# (Ajustables según el entorno de luz)
# ---------------------------------------------------------------------------
HSV_SANA = {
    "h_min": 20,  "s_min": 50,  "v_min": 50,
    "h_max": 85,  "s_max": 255, "v_max": 255,
}


def hex_a_rangos_hsv(hex_str: str) -> dict:
    """
    Convierte un código de color HEX (ej. '#E60000') en rangos HSV para OpenCV.
    Retorna un diccionario con h_min, h_max, s_min, s_max, v_min, v_max.
    """
    try:
        clean_hex = hex_str.lstrip("#")
        if len(clean_hex) == 6:
            r = int(clean_hex[0:2], 16)
            g = int(clean_hex[2:4], 16)
            b = int(clean_hex[4:6], 16)
        else:
            r, g, b = 230, 0, 0
    except Exception:
        r, g, b = 230, 0, 0

    pixel_bgr = np.uint8([[[b, g, r]]])
    pixel_hsv = cv.cvtColor(pixel_bgr, cv.COLOR_BGR2HSV)[0][0]

    h, s, v = int(pixel_hsv[0]), int(pixel_hsv[1]), int(pixel_hsv[2])

    h_min = max(0, h - 18)
    h_max = min(179, h + 18)

    s_min = max(30, s - 60)
    s_max = 255
    v_min = max(30, v - 60)
    v_max = 255

    if h <= 10 or h >= 170:
        h_min, h_max = 170, 10

    return {
        "h_min": h_min, "h_max": h_max,
        "s_min": s_min, "s_max": s_max,
        "v_min": v_min, "v_max": v_max,
    }


def analizar_marchitamiento(
    imagen_np: np.ndarray,
    h_min: int = HSV_SANA["h_min"],
    s_min: int = HSV_SANA["s_min"],
    v_min: int = HSV_SANA["v_min"],
    h_max: int = HSV_SANA["h_max"],
    s_max: int = HSV_SANA["s_max"],
    v_max: int = HSV_SANA["v_max"],
    es_bgr: bool = True,
) -> dict:
    """
    Analiza una imagen NumPy y devuelve el porcentaje de marchitamiento.
    """
    # Si la imagen no está en BGR, realizar la conversión correspondiente
    if not es_bgr:
        if imagen_np.shape[2] == 4:          # RGBA → BGR
            imagen_np = cv.cvtColor(imagen_np, cv.COLOR_RGBA2BGR)
        else:                                 # RGB → BGR
            imagen_np = cv.cvtColor(imagen_np, cv.COLOR_RGB2BGR)

    hsv = cv.cvtColor(imagen_np, cv.COLOR_BGR2HSV)
    _, S, _ = cv.split(hsv)

    # --- 1. Máscara de pétalos sanos (color seleccionado de la flor) ---
    if h_min <= h_max:
        bajo  = np.array([h_min, s_min, v_min])
        alto  = np.array([h_max, s_max, v_max])
        mascara_petalos = cv.inRange(hsv, bajo, alto)
    else:
        # Modo dual para rojo (el espacio HSV envuelve el rojo)
        m1 = cv.inRange(hsv, np.array([0,      s_min, v_min]), np.array([h_max,  s_max, v_max]))
        m2 = cv.inRange(hsv, np.array([h_min,  s_min, v_min]), np.array([179,    s_max, v_max]))
        mascara_petalos = cv.bitwise_or(m1, m2)

    # --- 2. Máscara de hojas y tallo sanos (Verde en HSV: H: 35..85, S: 30..255, V: 30..255) ---
    mascara_hojas = cv.inRange(hsv, np.array([35, 30, 30]), np.array([85, 255, 255]))

    # --- 3. Máscara sana total = Pétalos sanos + Hojas/Tallo sanos ---
    mascara_sana = cv.bitwise_or(mascara_petalos, mascara_hojas)

    # --- 4. Molde total de la flor/planta (Saturación y brillo significativos de la planta) ---
    s_suave = cv.GaussianBlur(S, (7, 7), 0)
    _, gris_total = cv.threshold(s_suave, 30, 255, cv.THRESH_BINARY)
    kernel = np.ones((7, 7), np.uint8)
    gris_total = cv.morphologyEx(gris_total, cv.MORPH_CLOSE, kernel)

    # --- 5. Máscara marchita = molde de la planta − partes sanas ---
    mascara_marchita = cv.bitwise_and(gris_total, cv.bitwise_not(mascara_sana))

    # --- Cálculo exacto de áreas por recuento de píxeles ---
    area_total = float(np.count_nonzero(gris_total))
    area_marchita = float(np.count_nonzero(mascara_marchita))

    porcentaje_raw = (area_marchita / area_total * 100.0) if area_total > 0 else 0.0
    porcentaje_marchito = min(100.0, max(0.0, porcentaje_raw))

    return {
        "porcentaje_marchito": round(porcentaje_marchito, 1),
        "area_total":          round(area_total,   1),
        "area_marchita":       round(area_marchita, 1),
    }


def convertir_a_probabilidades(porcentaje_marchito: float) -> list:
    """
    Convierte el porcentaje de marchitamiento (0–100%) al formato de probabilidades
    esperado por AgenteFloraVision: [prob_fresca, prob_deteriorada, prob_perdida].
    """
    p = max(0.0, min(100.0, porcentaje_marchito)) / 100.0  # 0.0 a 1.0

    if p <= 0.25:
        return [1.0 - p, p, 0.0]
    elif p <= 0.50:
        frac = (p - 0.25) / 0.25
        return [0.75 * (1.0 - frac), 0.25 + 0.5 * frac, 0.25 * frac]
    elif p <= 0.75:
        frac = (p - 0.50) / 0.25
        return [0.0, 0.75 * (1.0 - frac), 0.25 + 0.75 * frac]
    else:
        return [0.0, 0.0, 1.0]


# ---------------------------------------------------------------------------
# INFERENCIA Y CLASIFICACIÓN CON MODELO DE DEEP LEARNING (MobileNetV2 / ResNet50)
# ---------------------------------------------------------------------------
_MODELO_IA_CACHE = None
CLASES_FLORES = ["Rosa", "Girasol", "Margarita", "Clavel", "Lirio", "Orquídea", "Tulipán"]

def cargar_modelo_ia():
    """
    Intenta cargar el modelo Keras entrenado (.keras o .h5) desde el directorio raíz.
    Devuelve la instancia del modelo o None si aún no se ha entrenado.
    """
    global _MODELO_IA_CACHE
    if _MODELO_IA_CACHE is not None:
        return _MODELO_IA_CACHE

    import os
    import tensorflow as tf

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    posibles_rutas = [
        os.path.join(base_dir, "modelo_flores.keras"),
        os.path.join(base_dir, "feature-training", "modelo_flores.keras"),
        os.path.join(base_dir, "modelo_flores.h5"),
        os.path.join(base_dir, "feature-training", "modelo_flores.h5"),
    ]

    for ruta in posibles_rutas:
        if os.path.exists(ruta):
            try:
                # Carga segura en Keras 3 / TensorFlow
                _MODELO_IA_CACHE = tf.keras.models.load_model(ruta, compile=False, safe_mode=False)
                return _MODELO_IA_CACHE
            except Exception as e:
                print(f"⚠️ Error cargando modelo desde {ruta}: {e}")

    return None


def clasificar_flor_ia(imagen_np: np.ndarray) -> dict:
    """
    Clasifica una imagen NumPy RGB/BGR con el modelo Deep Learning preentrenado.
    
    Retorna
    -------
    dict con claves:
        modelo_activo   : bool   (True si el modelo .h5/.keras está cargado)
        especie         : str    (Nombre de la flor predicha)
        confianza       : float  (Porcentaje de confianza 0–100)
        probabilidades  : dict   ({especie: prob})
    """
    modelo = cargar_modelo_ia()
    if modelo is None:
        return {
            "modelo_activo": False,
            "especie": None,
            "confianza": 0.0,
            "probabilidades": {}
        }

    try:
        # Preprocesar imagen
        if imagen_np.shape[2] == 4:
            img_rgb = cv.cvtColor(imagen_np, cv.COLOR_RGBA2RGB)
        elif len(imagen_np.shape) == 3 and imagen_np.shape[2] == 3:
            img_rgb = cv.cvtColor(imagen_np, cv.COLOR_BGR2RGB)
        else:
            img_rgb = imagen_np

        img_resized = cv.resize(img_rgb, (224, 224))
        img_tensor = np.expand_dims(img_resized, axis=0)

        predictions = modelo.predict(img_tensor, verbose=0)[0]
        idx_max = int(np.argmax(predictions))
        especie_predicha = CLASES_FLORES[idx_max] if idx_max < len(CLASES_FLORES) else "Desconocida"
        confianza_pct = round(float(predictions[idx_max]) * 100, 1)

        prob_dict = {
            cls: round(float(p) * 100, 1)
            for cls, p in zip(CLASES_FLORES, predictions)
        }

        return {
            "modelo_activo": True,
            "especie": especie_predicha,
            "confianza": confianza_pct,
            "probabilidades": prob_dict
        }
    except Exception as err:
        print(f"⚠️ Error en clasificar_flor_ia: {err}")
        return {
            "modelo_activo": False,
            "especie": None,
            "confianza": 0.0,
            "probabilidades": {}
        }

