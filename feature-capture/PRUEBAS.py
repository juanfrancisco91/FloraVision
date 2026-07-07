import cv2 as cv
import numpy as np

cam = cv.VideoCapture(0, cv.CAP_MSMF)

while True:

    ret, frame = cam.read()
    
    gris = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

    alto = np.array([75, 255, 255])
    bajo = np.array([0, 50, 50])
    
    mascara_flor = cv.inRange(hsv, bajo, alto)
    resultado = cv.bitwise_and(frame, frame, mask=mascara_flor)

    _, mascara_flor_completa = cv.threshold(gris, 40,255, cv.THRESH_BINARY) 
    contorno_total, jerarquia = cv.findContours(mascara_flor_completa, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    cv.drawContours(frame, contorno_total, -1, (255,0,0),1)

    cv.imshow('Contorno', mascara_flor_completa)
    cv.imshow('Result',resultado)
    cv.waitKey(1)

cam.release()
cv.destroyAllWindows()