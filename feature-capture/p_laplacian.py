from pathlib import Path
import os
import cv2 as cv
import numpy as np

script = Path(__file__).resolve().parent
ruta = os.path.join(script, 'imagenes_prueba/')

lista_img = []

for i in os.listdir(ruta):
    print(i)
    lista_img.append(i)



for i in lista_img:
    img = cv.imread(os.path.join(script, f'imagenes_prueba/{i}'))
    gris = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    laplacian = cv.Laplacian(gris, cv.CV_64F)
    laplacian = cv.convertScaleAbs(laplacian)

    _, zonas_rugosas = cv.threshold(laplacian,50,255, cv.THRESH_BINARY)

    cv.imshow('Pa lo rio', zonas_rugosas)
    cv.imshow('Origen', img)
    cv.waitKey(0)
    cv.destroyAllWindows