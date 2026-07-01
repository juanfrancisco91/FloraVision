import cv2 as cv
import time
import numpy as np

# FUNCION PARA ACTIVAR LA CAMARA
def captura_vid():
    camara = cv.VideoCapture(0, cv.CAP_MSMF) # FORZAMOS LA CAMARA DE WINDOWS Y SELECCIONAMOS LA CAMAR A UTILIZAR (0 POR DEFECTO)
    #time.sleep(3)

    if not camara.isOpened(): # BUCLE QUE NOS ARROJE UN ERROR SI LA CAMARA NO SE ABRIO CORRECATAMENTE
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
    # BUCLE QUE MANTIENE LOS FOTOGRAMAS CORRIENDO
    while True:
         
        ret, frame = camara.read() 
        img_gris = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

        # DETECCION DE BORDES
        _, img_binaria = cv.threshold(img_gris, 127,255,cv.THRESH_BINARY_INV) # IMGAEN BINARIA
        contornos, jerarquia = cv.findContours(img_binaria, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE) #CONTORNOS

        print(f'Numero de Contornos: {len(contornos)}')

        img_resultado = frame.copy()
        cv.drawContours(img_resultado, contornos, -1, (0,255,0),1)

        # Deteccion de Pixeles Marrones
        frame_color = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
        marron_bajo = np.array([0,50,50])
        marron_alto = np.array([75,255,255])
        rango = cv.inRange(frame_color,marron_bajo,marron_alto)
        mascara = cv.bitwise_and(frame,frame, mask=rango)
        
        # Deteccion de mascar marron
        marron_gris = cv.cvtColor(mascara, cv.COLOR_HSV2BGR)
        marron_gris = cv.cvtColor(marron_gris, cv.COLOR_BGR2GRAY)
        _, marron_binaria = cv.threshold(marron_gris,68,255, cv.THRESH_BINARY)
        contornos_m, jerarquia_m = cv.findContours(marron_binaria, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        copia_marron = mascara.copy()
        mascara_marron = cv.drawContours(copia_marron, contornos_m, -1, (0,255,0),1)

        # Resultados
        cv.imshow('1. Umbral / Binaria', img_binaria)
        cv.imshow('2. Contornos Detectados', img_resultado)
        cv.imshow('3. Probando', marron_binaria)
        cv.imshow('Camara_1', mascara)
        cv.imshow('Contorno del Marron', mascara_marron)

        cv.waitKey(1)
        
    
    camara.release()
    cv.destroyAllWindows()

l = captura_vid()