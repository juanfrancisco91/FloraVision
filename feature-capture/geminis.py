import cv2 as cv
import numpy as np
from pathlib import Path
import os

def nada(x):
    pass

# --- INICIALIZACIÓN DE INTERFAZ ---
cv.namedWindow('Controles')
cv.resizeWindow('Controles', 400, 320)

# Inicialización de Sliders (Ajustados para arrancar buscando Amarillo de Girasol)
cv.createTrackbar('H Min', 'Controles', 15, 179, nada)
cv.createTrackbar('S Min', 'Controles', 50, 255, nada)
cv.createTrackbar('V Min', 'Controles', 50, 255, nada)
cv.createTrackbar('H Max', 'Controles', 35, 179, nada)
cv.createTrackbar('S Max', 'Controles', 255, 255, nada)
cv.createTrackbar('V Max', 'Controles', 255, 255, nada)

# --- CARGA DE ASSETS ---
script = Path(__file__).resolve().parent
ruta_img = os.path.join(script, 'imagenes_prueba', 'roja2.jpg')
img = cv.imread(ruta_img)

if img is None:
    print("Error: No se pudo cargar la imagen del girasol.")
    exit()

# --- BUCLE PRINCIPAL (Compatible con Video / Frame) ---
while True:
    # NOTA: Si usas video en vivo, descomenta la lectura de la cámara y reemplaza 'img' por 'frame'
    # ret, frame = cam.read()
    # if not ret: break
    # img = frame

    # 1. Copias limpias para dibujar en cada fotograma (Evita que se acumulen líneas)
    copia_visual_total = img.copy()
    copia_visual_danio = img.copy()

    # 2. Espacios de Color Bases
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    
    # 3. Lectura de los Sliders para la PARTE SANA
    h_min = cv.getTrackbarPos('H Min', 'Controles')
    s_min = cv.getTrackbarPos('S Min', 'Controles')
    v_min = cv.getTrackbarPos('V Min', 'Controles')
    h_max = cv.getTrackbarPos('H Max', 'Controles')
    s_max = cv.getTrackbarPos('S Max', 'Controles')
    v_max = cv.getTrackbarPos('V Max', 'Controles')

    bajo = np.array([h_min, s_min, v_min])
    alto = np.array([h_max, s_max, v_max])

    # 4. PARTE SANA: Máscara e Imagen filtrada
    mascara_sana = cv.inRange(hsv, bajo, alto)
    parte_sana_bgr = cv.bitwise_and(img, img, mask=mascara_sana)

    # 5. DETECCIÓN COMPLETA DE LA FLOR (Tu lógica de Otsu optimizada)
    H, S, V = cv.split(hsv)
    v_suave = cv.GaussianBlur(V, (7, 7), 0)
    s_suave = cv.GaussianBlur(S, (7,7),0)
    # 'gris_nueva' es el molde completo de la flor (Sano + Daño)
    _, gris_nueva = cv.threshold(v_suave, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    _, gris_nueva = cv.threshold(s_suave, 20, 255, cv.THRESH_BINARY)

    # Limpieza del molde para rellenar huecos internos de los pétalos
    kernel = np.ones((7, 7), np.uint8)
    gris_nueva = cv.morphologyEx(gris_nueva, cv.MORPH_CLOSE, kernel)

    # 6. DETECCIÓN DE MARCHITACIONES (La Resta Lógica)
    # Molde completo de la flor MENOS la parte que tus sliders dicen que está sana
    mascara_marchita = cv.bitwise_and(gris_nueva, cv.bitwise_not(mascara_sana))

    # 7. CÁLCULO DE ÁREAS (Tu uso de cv.contourArea)
    # Contornos de la Flor Completa
    contornos_total, _ = cv.findContours(gris_nueva, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    area_total = sum([cv.contourArea(c) for c in contornos_total if cv.contourArea(c) > 100])

    # Contornos de las Marchitaciones
    contornos_marchitos, _ = cv.findContours(mascara_marchita, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    area_marchita = sum([cv.contourArea(c) for c in contornos_marchitos if cv.contourArea(c) > 30])

    # 8. CÁLCULO DEL PORCENTAJE (FloraVision Formula)
    if area_total > 0:
        porcentaje_marchito = (area_marchita / area_total) * 100
    else:
        porcentaje_marchito = 0

    # 9. RENDERIZADO VISUAL
    # Dibujamos el contorno total en Verde sobre su copia
    cv.drawContours(copia_visual_total, contornos_total, -1, (0, 255, 0), 2)
    # Dibujamos el contorno del daño en Rojo sobre su copia
    cv.drawContours(copia_visual_danio, contornos_marchitos, -1, (0, 0, 255), 2)

    # Texto en pantalla
    cv.putText(copia_visual_danio, f"Danio: {porcentaje_marchito:.1f}%", (20, 40),
               cv.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

    # --- DESPLIEGUE DE VENTANAS ---
    cv.imshow('Original', img)
    cv.imshow('1. Mascara Sana (Sliders)', mascara_sana)
    cv.imshow('2. Molde Flor Completa (Otsu)', copia_visual_total)
    cv.imshow('3. Marchitamiento Detectado', copia_visual_danio)

    # Condición de salida con ESC
    if cv.waitKey(1) & 0xFF == 27:
        print(f"\nRangos guardados:")
        print(f"bajo = np.array([{h_min}, {s_min}, {v_min}])")
        print(f"alto = np.array([{h_max}, {s_max}, {v_max}])")
        break

cv.destroyAllWindows()