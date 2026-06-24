import cv2 as cv
import time

camara = cv.VideoCapture(0,cv.CAP_DSHOW)
print("Esperando a que el teléfono conecte y mande señal...")
time.sleep(3)

if not camara.isOpened():
    print("Error: OpenCV no pudo engancharse a la cámara de Windows.")
    exit()

while True:
    
    ret, frame = camara.read()
    
    cv.imshow('asfasdfdsa', frame)
    if cv.waitKey(1) & 0xFF == ord('q'):
        break
    
camara.release()
cv.destroyAllWindows()