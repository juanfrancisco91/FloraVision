import cv2 as cv

def captura_vid():
    camara = cv.VideoCapture(0)
    l = []

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

    return l
a=0
l = captura_vid()
for i in l:
    a+=1
    cv.imshow('preuba', i)
    cv.imwrite(f'{a}.jpg',i)
    cv.waitKey(0)
    cv.destroyAllWindows()
