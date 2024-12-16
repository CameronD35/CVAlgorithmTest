import cv2 as cv
import numpy as np

img = cv.imread('blueLED.jpg')
height, width = img.shape[:2]

blank = np.zeros(img.shape[:2], dtype='uint8')

blue, green, red = cv.split(img)
blueImg = cv.merge([blue, blank, blank])

# lowerBlue = np.array([50, 0, 0], dtype='uint8')
# upperBlue = np.array([255, 255, 255], dtype='uint8')

# colorMask = cv.inRange(img, lowerBlue, upperBlue)
#detectedBlue = cv.bitwise_and(img, img, mask=colorMask)

grayscaleImg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)


grayThreshold, grayThresholdedImg = cv.threshold(grayscaleImg, 252, 255, cv.THRESH_BINARY)
blueThreshold, blueThresholdedImg = cv.threshold(blueImg, 254, 255, cv.THRESH_BINARY)

grayscaleBlueImg = cv.cvtColor(blueThresholdedImg, cv.COLOR_BGR2GRAY)

# scaledThresholdImg = cv.resize(thresholdedImg, (width/2, height/2))

cv.imshow('Blue LED', img)
cv.imshow('Blue Only Image', blueImg)
cv.imshow('Grayscale blue LED', grayscaleImg)
cv.imshow('Blue to Gray Thresholded blue LED', grayscaleBlueImg)
cv.imshow('Grayscale Thresholded blue LED', grayThresholdedImg)

cv.waitKey(0)