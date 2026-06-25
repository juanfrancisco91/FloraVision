import cv2 as cv
import time

def captura_vid():
    camara = cv.VideoCapture(1, cv.CAP_MSMF)
    fotogramas = []

    time.sleep(3)
    
    if not camara.isOpened():
        print("No se pudo abrir la Camara")
        exit()

    while True:
        
        ret, frame = camara.read()
        l.append(frame)
        cv.imshow('Camara_1', frame)
        
        if cv.waitKey(1) & 0xFF == ord('`'):
            break

        
    camara.release()
    cv.destroyAllWindows()

    return fotogramas