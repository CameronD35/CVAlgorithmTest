import cv2 as cv
import numpy as np

# Reads in the image
img = cv.imread('purpleLED.jpg')

# Splits the image into the three different color channels
# ---- IRRELAVENT ----

# height, width = img.shape[:2]

# blank = np.zeros(img.shape[:2], dtype='uint8')

# blue, green, red = cv.split(img)
# blueImg = cv.merge([blue, blank, blank])
# redImg = cv.merge([blank, blank, red])

# lowerBlue = np.array([50, 0, 0], dtype='uint8')
# upperBlue = np.array([255, 255, 255], dtype='uint8')

# colorMask = cv.inRange(img, lowerBlue, upperBlue)
#detectedBlue = cv.bitwise_and(img, img, mask=colorMask)

# ---- RELEVANT ----

# Sets the image to grayscasle
grayscaleImg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

# Thresholds the image to intensities 247 and above
# Lower intensity will make the circles cover more of the LED, but the center will likely remain the same
# The center is key for tracking where the LED actually is
grayThreshold, grayThresholdedImg = cv.threshold(grayscaleImg, 247, 255, cv.THRESH_BINARY)

# Adds a slight blur to compensate for gaps in the thresholding process
grayThreshold_Blurred = cv.blur(grayThresholdedImg, (3,3))

# Uses the canny algorithm to find edges in the thresholded images
# Essentially, this outlines the LEDs
edges = cv.Canny(grayThreshold_Blurred, 0, 255)

# Gets the coordinates of various parts of the edges
contours, hierarchies = cv.findContours(edges, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

# In the format [max, min]
xCoordinatesArray = []
yCoordinatesArray = []

# This loops through the contour coordinates found in the 'contours' variable
# Note how the contours is a 3D array
# This code also finds the max and min of the coordinates since between those points houses most of the contour (LED outline)
i = 1
for contour in contours:
    # print(f'\n\n-------- Contour {i} --------\n\n')
    j = 1
    xArray = []
    yArray = []
    
    for pointArray in contour:

        for point in pointArray:

            # print(f'Point {j}: {point}')
            j+= 1
            xArray.append(point[0])
            yArray.append(point[1])

    xCoordinatesArray.append([np.min(xArray), np.max(xArray)])
    yCoordinatesArray.append([np.min(yArray), np.max(yArray)])
    i += 1

# print('x min and max:', xCoordinatesArray)
# print('y min and max:', yCoordinatesArray)

# Converts the arrays to Numpy format since OpenCV methods require this format
xCoordinatesArray = np.array(xCoordinatesArray, dtype=np.uint32)
yCoordinatesArray = np.array(yCoordinatesArray, dtype=np.uint32)

# Loops through the arrays of coordinates, calculates their centers, and the radii the ellipse would have to be to include the extrema
# The program then circles where the light is detected, provides its center and prints text to indicate the different LEDs
for i in range (0, len(xCoordinatesArray)):

    # [min. max]
    xCoordinate = [xCoordinatesArray[i, 0], xCoordinatesArray[i, 1]]
    yCoordinate = [yCoordinatesArray[i, 0], yCoordinatesArray[i, 1]]

    xCenter = (xCoordinate[1] + xCoordinate[0])/2
    yCenter = (yCoordinate[1] + yCoordinate[0])/2

    center = np.array([xCenter, yCenter], dtype=np.uint32)


    xRadius = xCoordinate[1] - xCenter
    yRadius = yCoordinate[1] - yCenter

    majorAxis = np.maximum(xRadius, yRadius)
    minorAxis = np.minimum(xRadius, yRadius)

    axes = np.array([majorAxis, minorAxis], dtype=np.uint32)

    print(f'center: {center}')
    print(f'radius: ({xRadius}, {yRadius})')
    print(f'axes: {axes}')

    detectedLight = cv.ellipse(img, center, axes, 0, 0, 360, (0, 255, 0), 2)
    detectedLightCenter = cv.circle(img, center, 1, (0, 0, 255), 3)

    textOrigin = center - 25

    print(textOrigin)
    detectedLightText = cv.putText(img, f'LED {i}', textOrigin, cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv.LINE_AA)

# print(len(contours))


# YOU CAN IGNORE ALL THIS. This was used by a different algorithm that detects circlesw.
# However, the glare from LEDs is rarely ever a perfect or near-perfect circle


# detectedCircles = cv.HoughCircles(grayThreshold_Blurred, cv.HOUGH_GRADIENT, 1, 20, param1 = 50, param2 = 30, minRadius = 1, maxRadius = 40)


# if detectedCircles is not None:

#     detectedCircles = np.uint16(np.around(detectedCircles))

#     for pt in detectedCircles[0, :]:
#         a, b, r = pt[0], pt[1], pt[2]

#         cv.circle(img, (a, b), r, (0, 255, 0), 2)

#         cv.circle(img, (a, b), 1, (0, 0, 255), 3)

#         cv.imshow('Detected Circle', img)


# blueThreshold, blueThresholdedImg = cv.threshold(blueImg, 254, 255, cv.THRESH_BINARY)
# redThreshold, redThresholdedImg = cv.threshold(redImg, 254, 255, cv.THRESH_BINARY)

# grayscaleBlueImg = cv.cvtColor(blueThresholdedImg, cv.COLOR_BGR2GRAY)

# scaledThresholdImg = cv.resize(thresholdedImg, (width/2, height/2))

#cv.imshow('Blue LED', img)
# cv.imshow('Blue Only Image', blueImg)
# cv.imshow('Red Only Image', redImg)
# cv.imshow('Grayscale blue LED', grayscaleImg)
# cv.imshow('Blue Thresholded', blueThresholdedImg)
# cv.imshow('Red Thresholded', redThresholdedImg)


cv.imshow('Grayscale Thresholded', grayThreshold_Blurred)
cv.imshow('Circles?????', img)

cv.waitKey(0)