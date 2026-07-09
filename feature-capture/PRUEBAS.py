import cv2 as cv
from pathlib import Path
import os
import numpy as np


cam = cv.VideoCapture(0, cv.CAP_MSMF)

<<<<<<< HEAD
while True:
    
    ret, frame = cam.read()
    
    gris = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    
    H,S,V = cv.split(hsv)
    
    v_suave = cv.GaussianBlur(V, (7,7), 0)
    
    _, mascara_flor = cv.threshold(v_suave, 0,255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    
    cv.imshow('Tu sabe', mascara_flor)
    cv.waitKey(1)

cam.release()
cam.destroyAllWindows()
=======
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
>>>>>>> b69b6e83e0ab08af8e83b60557b76c32a8586806
