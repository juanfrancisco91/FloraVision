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

<<<<<<< HEAD
    alto = np.array([75, 255, 255])
    bajo = np.array([0, 50, 50])
    
    H, S, V = cv.split(hsv)

    v_suave = cv.GaussianBlur(V,(7,7),0)

    _, mascara_flor = cv.threshold(v_suave, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    
    cv.imshow('Tu sabe',mascara_flor)
    cv.waitKey(1)

cam.release()
cv.destroyAllWindows()
=======

>>>>>>> b8b59c5c1a5879b5e85367b1219c51685273a8ca
