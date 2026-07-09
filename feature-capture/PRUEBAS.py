import cv2 as cv
from pathlib import Path
import os
import numpy as np


script = Path(__file__).resolve().parent
ruta = os.path.join(script, 'imagenes_prueba/rosa_roja.jpg')
img = cv.imread(ruta)

if img is None:
    print('No hay nada')
else:
    img_hsv = cv.cvtColor(img ,cv.COLOR_BGR2HSV)
    cv.imshow('Origen', img)
    cv.imshow('HSV BASE', img_hsv)
    azul_bajo =  np.array([35, 50, 50])
    azul_alto = np.array([70, 255, 255])
    mod = cv.inRange(img_hsv, azul_bajo, azul_alto)
    mod = cv.bitwise_and(img, img, mask=mod)
    mod_rojo = cv.inRange(img_hsv, azul_bajo, azul_alto)
    mod_rojo = cv.bitwise_or(img,img,mask=mod_rojo)
    cv.imshow('Modificada', mod)
    cv.imshow('ROJA', mod_rojo)
    cv.waitKey(0)
    cv.destroyAllWindows()


