import cv2 as cv

cam = cv.VideoCapture(0, cv.CAP_MSMF)
while True:

    ret,frame = cam.read()
    cv.imshow('dfaf', frame)