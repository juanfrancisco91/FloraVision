import cv2 as cv
import numpy as np
from pathlib import Path
import os

def nada(x):
    pass

cv.namedWindow('Controles')
cv.resizeWindow('Controles', 400,300)
area_total = 0       
# Creacion de barras de desplazamiento
cv.createTrackbar('H Min', 'Controles', 0,179, nada)
cv.createTrackbar('S Min', 'Controles', 50,255, nada)
cv.createTrackbar('V Min', 'Controles', 50,255, nada)
cv.createTrackbar('H Max', 'Controles', 179,179, nada)
cv.createTrackbar('S Max', 'Controles', 255,255, nada)
cv.createTrackbar('V Max', 'Controles', 255,255, nada)
#cv.createTrackbar('Tresh Values', 'Controles',0,255, nada)
cv.createTrackbar('Preset Rojo', 'Controles', 0, 1, nada)


cam = cv.VideoCapture(0, cv.CAP_MSMF)
script = Path(__file__).resolve().parent
img = os.path.join(script,'imagenes_prueba\girasol.jpg')
img = cv.imread(img)
while True:

    ret,frame = cam.read()
    
    frame_total = frame.copy()
    frame_danio = frame.copy()

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    gris = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    
    if cv.getTrackbarPos('Preset Rojo', 'Controles') == 1:
        # Movemos los sliders automáticamente a los extremos
        cv.setTrackbarPos('H Min', 'Controles', 170)
        cv.setTrackbarPos('H Max', 'Controles', 10)
        cv.setTrackbarPos('S Min', 'Controles', 50)  
        cv.setTrackbarPos('V Min', 'Controles', 50)
        # Devolvemos el interruptor a 0 inmediatamente
        cv.setTrackbarPos('Preset Rojo', 'Controles', 0)

    h_min = cv.getTrackbarPos('H Min', 'Controles')
    s_min = cv.getTrackbarPos('S Min', 'Controles')
    v_min = cv.getTrackbarPos('V Min', 'Controles')
    h_max = cv.getTrackbarPos('H Max', 'Controles')
    s_max = cv.getTrackbarPos('S Max', 'Controles')
    v_max = cv.getTrackbarPos('V Max', 'Controles')
    #t_value = cv.getTrackbarPos('Tresh Values', 'Controles')

    if h_min <= h_max:

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


    #mascara_sana = cv.inRange(hsv, bajo, alto)
    resultado = cv.bitwise_and(frame, frame, mask=mascara_sana)


    H,S,V = cv.split(hsv)
    s_suave = cv.GaussianBlur(S, (7,7),0)
    
    _, gris_nueva = cv.threshold(s_suave, 20,255, cv.THRESH_BINARY)


    #gris_canny = cv.Canny(resultado, 30, 200)

    kernel = np.ones((7,7), np.uint8)
    gris_nueva = cv.morphologyEx(gris_nueva, cv.MORPH_CLOSE, kernel)
    

    #_, gris_binaria = cv.threshold(gris_canny,127,255, cv.THRESH_BINARY)        
    #contornos_g, jerarquia = cv.findContours(gris_binaria, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    #mascara_gris = cv.drawContours(resultado, contornos_g, -1, (0,255,0),1)
    
    mascara_marchita = cv.bitwise_and(gris_nueva, cv.bitwise_not(mascara_sana))

    contornos_total, _  = cv.findContours(gris_nueva, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    area_total = sum([cv.contourArea(c) for c in contornos_total if cv.contourArea(c) > 100])


    contornos_marchito, _  = cv.findContours(mascara_marchita, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    area_marchita = sum([cv.contourArea(c) for c in contornos_marchito if cv.contourArea(c) > 30])

    if area_total > 0:
        porcentaje_marchito = (area_marchita / area_total) * 100
    else:
        porcentaje_marchito = 0

    #Funcion para utilizar mas tarde
    #cv.putText(frame, f"Danio {porcentaje_marchito:.1f}", (10,40,)

    cv.drawContours(frame_total, contornos_total, -1, (0, 255, 0), 2)
    cv.drawContours(frame_danio, contornos_marchito, -1, (0, 0, 255), 2)
    
    #cv.imshow('Mascara', mascara_sana)
    #cv.imshow('Flor Completa', resultado)
    #cv.imshow('Original',frame)
    #cv.imshow('gris_canny', gris_canny)
    #cv.imshow('Nueva Gris', gris_nueva)

    cv.putText(frame_danio, f'Danio: {porcentaje_marchito:.1f}%', (20,40),
               cv.FONT_HERSHEY_COMPLEX,1.0,(0,0,255),2)
    
    cv.imshow('1. Original', frame)
    cv.imshow('2. Parte Sana Aislada', resultado)
    cv.imshow('3. Molde Flor Completa', frame_total)
    cv.imshow('4. Marchitamiento Detectado', frame_danio)
    #print(f'Area total afectada: {area_total}')

    #print(f"bajo = {h_min}, {s_min}, {v_min}")
    #print(f"alto = {h_max}, {s_max}, {v_max}")

    if cv.waitKey(1) & 0xFF == 27:
        print(f"Rango encontrado:")
        print(f"bajo = {h_min}, {s_min}, {v_min}")
        print(f"alto = {h_max}, {s_max}, {v_max}")
        break
    
cam.release()
cv.destroyAllWindows()
    
