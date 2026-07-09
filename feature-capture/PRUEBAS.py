import cv2 as cv
from pathlib import Path
import os
import numpy as np


cam = cv.VideoCapture(0, cv.CAP_MSMF)


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

