from pathlib import Path
import os
import cv2 as cv
import numpy as np

script = Path(__file__).resolve().parent
ruta = os.path.join(script, 'imagenes_prueba/dano.jpg')

img = cv.imread(ruta)
cv.imshow('Prueba', img)
img_gris = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
img_cany = cv.Canny(img_gris, 30,100)

img_hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
marron_bajo = np.array([30,50,50])
marron_alto = np.array([60,255,255])        
rango = cv.inRange(img_hsv,marron_bajo,marron_alto)
mascara = cv.bitwise_and(img,img, mask=rango)
cv.imshow('lsdkjfa', mascara)
cv.waitKey(0)
cv.destroyAllWindows()