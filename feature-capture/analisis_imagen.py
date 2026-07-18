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


def analizar_marchitamiento(
    imagen_np: np.ndarray,
    h_min: int = HSV_SANA["h_min"],
    s_min: int = HSV_SANA["s_min"],
    v_min: int = HSV_SANA["v_min"],
    h_max: int = HSV_SANA["h_max"],
    s_max: int = HSV_SANA["s_max"],
    v_max: int = HSV_SANA["v_max"],
) -> dict:
    """
    Analiza una imagen NumPy (BGR o RGB) y devuelve el porcentaje de marchitamiento.

    Parámetros
    ----------
    imagen_np : np.ndarray
        Imagen en formato NumPy (RGB o BGR, uint8).
    h_min, s_min, v_min : int
        Límite inferior del rango HSV que define píxeles «sanos».
    h_max, s_max, v_max : int
        Límite superior del rango HSV que define píxeles «sanos».

    Retorna
    -------
    dict con claves:
        porcentaje_marchito : float  (0.0 – 100.0)
        area_total          : float  (píxeles de la flor detectada)
        area_marchita       : float  (píxeles clasificados como marchitos)
    """
    # Asegurar que la imagen esté en BGR para OpenCV
    if imagen_np.shape[2] == 4:          # RGBA → BGR
        imagen_np = cv.cvtColor(imagen_np, cv.COLOR_RGBA2BGR)
    else:                                 # RGB → BGR
        imagen_np = cv.cvtColor(imagen_np, cv.COLOR_RGB2BGR)

    hsv = cv.cvtColor(imagen_np, cv.COLOR_BGR2HSV)
    _, S, _ = cv.split(hsv)

    # --- Máscara de la parte sana (color saludable según parámetros HSV) ---
    if h_min <= h_max:
        bajo  = np.array([h_min, s_min, v_min])
        alto  = np.array([h_max, s_max, v_max])
        mascara_sana = cv.inRange(hsv, bajo, alto)
    else:
        # Modo dual para rojo (el espacio HSV «envuelve» el rojo)
        m1 = cv.inRange(hsv, np.array([0,      s_min, v_min]), np.array([h_max,  s_max, v_max]))
        m2 = cv.inRange(hsv, np.array([h_min,  s_min, v_min]), np.array([179,    s_max, v_max]))
        mascara_sana = cv.bitwise_or(m1, m2)

    # --- Máscara total de la flor (umbral de saturación) ---
    s_suave = cv.GaussianBlur(S, (7, 7), 0)
    _, gris_total = cv.threshold(s_suave, 20, 255, cv.THRESH_BINARY)
    kernel = np.ones((7, 7), np.uint8)
    gris_total = cv.morphologyEx(gris_total, cv.MORPH_CLOSE, kernel)

    # --- Máscara de la parte marchita = total − sana ---
    mascara_marchita = cv.bitwise_and(gris_total, cv.bitwise_not(mascara_sana))

    # --- Contornos y áreas ---
    contornos_total, _   = cv.findContours(gris_total,       cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contornos_marchito, _ = cv.findContours(mascara_marchita, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    area_total   = sum(cv.contourArea(c) for c in contornos_total    if cv.contourArea(c) > 100)
    area_marchita = sum(cv.contourArea(c) for c in contornos_marchito if cv.contourArea(c) > 30)

    porcentaje_marchito = (area_marchita / area_total * 100) if area_total > 0 else 0.0

    return {
        "porcentaje_marchito": round(porcentaje_marchito, 1),
        "area_total":          round(area_total,   1),
        "area_marchita":       round(area_marchita, 1),
    }


def convertir_a_probabilidades(porcentaje_marchito: float) -> list:
    """
    Convierte el porcentaje de marchitamiento (0–100) al formato de probabilidades
    esperado por AgenteFloraVision: [prob_fresca, prob_deteriorada, prob_perdida].

    Esta función interpola linealmente dentro de los rangos de las REGLAS del agente.
    """
    p = porcentaje_marchito / 100.0  # normalizar a 0–1

    if p < 0.30:
        return [1.0 - p, p, 0.0]
    elif p < 0.60:
        return [0.0, 1.0 - p, p]
    else:
        return [0.0, 0.0, 1.0]
