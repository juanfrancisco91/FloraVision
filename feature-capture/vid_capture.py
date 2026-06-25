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

    while True:
        
        ret, frame = camara.read()
        frame_color = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        marron_bajo = np.array([0,50,50])
        marron_alto = np.array([75,255,255])
        rango = cv.inRange(frame_color,marron_bajo,marron_alto)
        mascara = cv.bitwise_and(frame,frame, mask=rango)
        cv.imshow('Camara_1', mascara)
        
        if cv.waitKey(1) & 0xFF == ord('`'):
            break

        
    camara.release()
    cv.destroyAllWindows()

l= captura_vid()