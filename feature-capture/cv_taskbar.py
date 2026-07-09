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


cam = cv.VideoCapture(0, cv.CAP_MSMF)
script = Path(__file__).resolve().parent
img = os.path.join(script,'imagenes_prueba\girasol.jpg')
img = cv.imread(img)
while True:

    #ret,frame = cam.read()
    
    frame_total = img
    frame_danio = img

    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    gris = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        
    h_min = cv.getTrackbarPos('H Min', 'Controles')
    s_min = cv.getTrackbarPos('S Min', 'Controles')
    v_min = cv.getTrackbarPos('V Min', 'Controles')
    h_max = cv.getTrackbarPos('H Max', 'Controles')
    s_max = cv.getTrackbarPos('S Max', 'Controles')
    v_max = cv.getTrackbarPos('V Max', 'Controles')
    #t_value = cv.getTrackbarPos('Tresh Values', 'Controles')

    bajo = np.array([h_min, s_min, v_min])
    alto  = np.array([h_max,s_max,v_max])

    mascara_sana = cv.inRange(hsv, bajo, alto)
    resultado = cv.bitwise_and(img, img, mask=mascara_sana)

    H,S,V = cv.split(hsv)
    v_suave = cv.GaussianBlur(V, (7,7),0)
    
    _, gris_nueva = cv.threshold(v_suave, 0,255, cv.THRESH_BINARY + cv.THRESH_OTSU)


    #gris_canny = cv.Canny(resultado, 30, 200)

    kernel = np.ones((5,5), np.uint8)
    gris_nueva = cv.morphologyEx(gris_nueva, cv.MORPH_CLOSE, kernel)
    

    #_, gris_binaria = cv.threshold(gris_canny,127,255, cv.THRESH_BINARY)        
    #contornos_g, jerarquia = cv.findContours(gris_binaria, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    #mascara_gris = cv.drawContours(resultado, contornos_g, -1, (0,255,0),1)
    
    
    mascara_marchita = cv.bitwise_and(gris_nueva, cv.bitwise_not(mascara_sana))

    contornos_total, _  = cv.findContours(gris_nueva, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contornos_marchito, _  = cv.findContours(mascara_marchita, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    #Funcion para utilizar mas tarde
    #cv.putText(frame, f"Danio {porcentaje_marchito:.1f}", (10,40,)

    cv.drawContours(frame_total, contornos_total, -1, (0, 255, 0), 2)
    cv.drawContours(frame_danio, contornos_marchito, -1, (255, 0, 0), 2)
    
    #cv.imshow('Mascara', mascara_sana)
    #cv.imshow('Flor Completa', resultado)
    #cv.imshow('Original',frame)
    #cv.imshow('gris_canny', gris_canny)
    #cv.imshow('Nueva Gris', gris_nueva)

    cv.imshow('1. Mascara Sana (Sliders)', mascara_sana)
    cv.imshow('2. Molde Flor Completa (Otsu)', frame_total)
    cv.imshow('3. Marchitamiento Detectado', frame_danio)
    
    #print(f'Area total afectada: {area_total}')

    #print(f"bajo = {h_min}, {s_min}, {v_min}")
    #print(f"alto = {h_max}, {s_max}, {v_max}")

    if cv.waitKey(0) & 0xFF == 27:
        print(f"Rango encontrado:")
        print(f"bajo = {h_min}, {s_min}, {v_min}")
        print(f"alto = {h_max}, {s_max}, {v_max}")
        break
    
cam.release()
cv.destroyAllWindows()
    
