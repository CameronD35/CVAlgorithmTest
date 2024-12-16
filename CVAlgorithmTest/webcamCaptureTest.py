import cv2 as cv
import numpy as np

webcam = cv.VideoCapture(0)

while (True):

    _, frame = webcam.read()


    hsvFrame = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    grayFrame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    lowerBlue = np.array([136, 87, 111], np.uint8)
    upperBlue = np.array([180, 255, 255], np.uint8)
    blueMask = cv.inRange(hsvFrame, lowerBlue, upperBlue)

    res_blue = cv.bitwise_and(frame, frame, mask = blueMask)

    cv.imshow("Multiple Color Detection in Real-Time", frame) 
    cv.imshow("Mask", blueMask)
    if cv.waitKey(10) & 0xFF == ord('q'): 
        webcam.release() 
        cv.destroyAllWindows() 
        break