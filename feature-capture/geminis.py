import cv2 as cv
import numpy as np
from pathlib import Path
import os

def nada(x):
    pass

# ==========================================
# 1. INICIALIZACIÓN DE LA INTERFAZ
# ==========================================
cv.namedWindow('Controles')
cv.resizeWindow('Controles', 400, 350)

# Sliders estándar para H, S, V
cv.createTrackbar('H Min', 'Controles', 15, 179, nada)
cv.createTrackbar('S Min', 'Controles', 50, 255, nada)
cv.createTrackbar('V Min', 'Controles', 50, 255, nada)
cv.createTrackbar('H Max', 'Controles', 35, 179, nada)
cv.createTrackbar('S Max', 'Controles', 255, 255, nada)
cv.createTrackbar('V Max', 'Controles', 255, 255, nada)

# Botón virtual (Interruptor) para activar el preset de rosas rojas
cv.createTrackbar('Preset Rojo', 'Controles', 0, 1, nada)

# ==========================================
# 2. CARGA DE IMAGEN / PREPARACIÓN
# ==========================================
script = Path(__file__).resolve().parent
ruta_img = os.path.join(script, 'imagenes_prueba', 'roja2.jpg')
img = cv.imread(ruta_img)
cam = cv.VideoCapture(0,cv.CAP_MSMF)


if img is None:
    print("Error: No se pudo cargar la imagen.")
    exit()


# ==========================================
# 3. BUCLE PRINCIPAL DE PROCESAMIENTO
# ==========================================
while True:
    
    ret, frame = cam.read()
    
    # Copias limpias para que no se acumulen los dibujos entre fotogramas
    copia_visual_total = frame.copy()
    copia_visual_danio = frame.copy()

    

    
    # Convertimos a espacio HSV (Matiz, Saturación, Brillo)
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    
    # --- A. Lógica del Botón "Preset Rojo" ---
    if cv.getTrackbarPos('Preset Rojo', 'Controles') == 1:
        # Movemos los sliders automáticamente a los extremos
        cv.setTrackbarPos('H Min', 'Controles', 170)
        cv.setTrackbarPos('H Max', 'Controles', 10)
        cv.setTrackbarPos('S Min', 'Controles', 50)  
        cv.setTrackbarPos('V Min', 'Controles', 50)
        # Devolvemos el interruptor a 0 inmediatamente
        cv.setTrackbarPos('Preset Rojo', 'Controles', 0)
        
    # --- B. Lectura de variables actuales ---
    h_min = cv.getTrackbarPos('H Min', 'Controles')
    s_min = cv.getTrackbarPos('S Min', 'Controles')
    v_min = cv.getTrackbarPos('V Min', 'Controles')
    h_max = cv.getTrackbarPos('H Max', 'Controles')
    s_max = cv.getTrackbarPos('S Max', 'Controles')
    v_max = cv.getTrackbarPos('V Max', 'Controles')
    
    # --- C. EXTRACCIÓN DE LA PARTE SANA (Con soporte para rojo envolvente) ---
    if h_min <= h_max:
        # MODO NORMAL (Ej. Amarillo, Verde, Naranja)
        bajo = np.array([h_min, s_min, v_min])
        alto = np.array([h_max, s_max, v_max])
        mascara_sana = cv.inRange(hsv, bajo, alto)
    else:
        # MODO DUAL (Rojo: cuando el Mínimo cruza al Máximo)
        rojo_bajo_1 = np.array([0, s_min, v_min])
        rojo_alto_1 = np.array([h_max, s_max, v_max])
        rojo_bajo_2 = np.array([h_min, s_min, v_min])
        rojo_alto_2 = np.array([179, s_max, v_max])
        
        mascara_rojo_1 = cv.inRange(hsv, rojo_bajo_1, rojo_alto_1)
        mascara_rojo_2 = cv.inRange(hsv, rojo_bajo_2, rojo_alto_2)
        mascara_sana = cv.bitwise_or(mascara_rojo_1, mascara_rojo_2)

    # Solo para visualizar en la ventana "Parte Sana Aislada"
    resultado_sano = cv.bitwise_and(frame, frame, mask=mascara_sana)

    # --- D. EXTRACCIÓN DEL MOLDE DE LA FLOR (Ignorando fondo blanco) ---
    _, S, _ = cv.split(hsv)
    s_suave = cv.GaussianBlur(S, (7, 7), 0)
    
    # Binarización por Saturación: Aisla cualquier cosa que tenga color
    _, gris_nueva = cv.threshold(s_suave, 20, 255, cv.THRESH_BINARY)

    # Limpieza Morfológica: Rellena los huecos negros dentro del molde de la flor
    kernel = np.ones((7, 7), np.uint8)
    gris_nueva = cv.morphologyEx(gris_nueva, cv.MORPH_CLOSE, kernel)

    # --- E. CÁLCULO DE MARCHITEZ (La Resta Lógica) ---
    # Lo que pertenece a la flor entera PERO NO está dentro del rango sano
    mascara_marchita = cv.bitwise_and(gris_nueva, cv.bitwise_not(mascara_sana))

    # --- F. MATEMÁTICA DE ÁREAS ---
    # 1. Área Total de la planta
    contornos_total, _ = cv.findContours(gris_nueva, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    area_total = sum([cv.contourArea(c) for c in contornos_total if cv.contourArea(c) > 100])

    # 2. Área del Daño
    contornos_marchitos, _ = cv.findContours(mascara_marchita, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    area_marchita = sum([cv.contourArea(c) for c in contornos_marchitos if cv.contourArea(c) > 30])

    # 3. Fórmula Porcentual
    if area_total > 0:
        porcentaje_marchito = (area_marchita / area_total) * 100
    else:
        porcentaje_marchito = 0

    # --- G. RENDERIZADO VISUAL ---
    # Dibujar silueta total en Verde
    cv.drawContours(copia_visual_total, contornos_total, -1, (0, 255, 0), 2)
    # Dibujar daño en Rojo
    cv.drawContours(copia_visual_danio, contornos_marchitos, -1, (0, 0, 255), 2)

    # Mostrar porcentaje en la ventana de daño
    cv.putText(copia_visual_danio, f"Danio: {porcentaje_marchito:.1f}%", (20, 40),
               cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

    # --- H. DESPLIEGUE EN PANTALLA ---
    cv.imshow('1. Original', frame)
    cv.imshow('2. Parte Sana Aislada', resultado_sano)
    cv.imshow('3. Molde Flor Completa', copia_visual_total)
    cv.imshow('4. Marchitamiento Detectado', copia_visual_danio)

    # Salida controlada
    if cv.waitKey(1) & 0xFF == 27:
        break

cv.destroyAllWindows()