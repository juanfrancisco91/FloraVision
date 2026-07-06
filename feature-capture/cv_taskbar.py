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
while True:

    ret,frame = cam.read()

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    gris = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        
    h_min = cv.getTrackbarPos('H Min', 'Controles')
    s_min = cv.getTrackbarPos('S Min', 'Controles')
    v_min = cv.getTrackbarPos('V Min', 'Controles')
    h_max = cv.getTrackbarPos('H Max', 'Controles')
    s_max = cv.getTrackbarPos('S Max', 'Controles')
    v_max = cv.getTrackbarPos('V Max', 'Controles')
    #t_value = cv.getTrackbarPos('Tresh Values', 'Controles')

    bajo = np.array([h_min, s_min, v_min])
    alto  = np.array([h_max,s_max,v_max])

    mascara = cv.inRange(hsv, bajo, alto)
    resultado = cv.bitwise_and(frame, frame, mask=mascara)

    gris_canny = cv.Canny(resultado, 30, 200)

    _, gris_binaria = cv.threshold(gris_canny,60,255, cv.THRESH_BINARY)        
    contornos_g, jerarquia = cv.findContours(gris_binaria, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    mascara_gris = cv.drawContours(resultado, contornos_g, -1, (0,255,0),1)

    
    umbral = 50

    area = frame.copy()
    for c in contornos_g:
        area = cv.contourArea(c)
        
        if area > umbral:
            area_total += area
            cv.drawContours(resultado, [c], -1,(0,0,255),2)
    

    cv.imshow('Mascara', mascara)
    cv.imshow('Resultado Filtrado', resultado)
    cv.imshow('Original', frame)
    cv.imshow('gris_canny', gris_canny)
    
    print(f'Area total afectada: {area_total}')

    print(f"bajo = {h_min}, {s_min}, {v_min}")
    print(f"alto = {h_max}, {s_max}, {v_max}")

    if cv.waitKey(1) & 0xFF == 27:
        print(f"Rango encontrado:")
        print(f"bajo = {h_min}, {s_min}, {v_min}")
        print(f"alto = {h_max}, {s_max}, {v_max}")
        break
    
cam.release()
cv.destroyAllWindows()
    
