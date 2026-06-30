import cv2 as cv
import time
import numpy as np

def captura_vid():
    camara = cv.VideoCapture(0, cv.CAP_MSMF)
    fotogramas = []
    #time.sleep(3)

    if not camara.isOpened():
        print("No se pudo abrir la Camara")
        exit()

    '''while True:
        
        ret, frame = camara.read()
        frame_color = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        marron_bajo = np.array([0,50,50])
        marron_alto = np.array([75,255,255])
        rango = cv.inRange(frame_color,marron_bajo,marron_alto)
        mascara = cv.bitwise_and(frame,frame, mask=rango)
        cv.imshow('Camara_1', mascara)
        #cv.imshow('camara2', frame)
        
        if cv.waitKey(1) & 0xFF == ord('`'):
            break'''
    while True:
         
        ret, frame = camara.read()
        img_gris = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        _, img_binaria = cv.threshold(img_gris, 127,255,cv.THRESH_BINARY)
        contornos, jerarquia = cv.findContours(img_binaria, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        print(f'Numero de Contornos: {len(contornos)}')

        img_resultado = frame.copy()
        cv.drawContours(img_resultado, contornos, -1, (0,255,0),1)

        frame_color = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        marron_bajo = np.array([0,50,50])
        marron_alto = np.array([75,255,255])
        rango = cv.inRange(frame_color,marron_bajo,marron_alto)
        mascara = cv.bitwise_and(frame,frame, mask=rango)
        
        # Resultados
        cv.imshow('1. Umbral / Binaria', img_binaria)
        cv.imshow('2. Contornos Detectados', img_resultado)
        cv.imshow('Camara_1', mascara)

        cv.waitKey(1)
        
    
    camara.release()
    cv.destroyAllWindows()

l = captura_vid()