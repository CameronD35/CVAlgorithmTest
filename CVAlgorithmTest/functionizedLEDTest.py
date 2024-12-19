import cv2 as cv
import numpy as np

# Reads in the image
ledImage = cv.imread('purpleLED.jpg')

def detectLEDs(img):
    # Sets the image to grayscasle
    grayscaleImg = cv.cvtColor(img, cv.COLOR_BGR2GRAY)


    # Thresholds the image to intensities 247 and above
    # Lower intensity will make the circles cover more of the LED, but the center will likely remain the same
    # The center is key for tracking where the LED actually is
    grayThreshold, grayThresholdedImg = cv.threshold(grayscaleImg, 247, 255, cv.THRESH_BINARY)


    # Adds a slight blur to compensate for gaps in the thresholding process
    grayThreshold_Blurred = cv.blur(grayThresholdedImg, (3,3))
    # cv.imshow('Grayscale Thresholded', grayThreshold_Blurred)


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

        # print(f'center: {center}')
        # print(f'radius: ({xRadius}, {yRadius})')
        # print(f'axes: {axes}')

        detectedLight = cv.ellipse(img, center, axes, 0, 0, 360, (0, 255, 0), 2)
        detectedLightCenter = cv.circle(img, center, 1, (0, 0, 255), 3)

        textOrigin = center - 25
        findAvgColor((xCoordinate[0], yCoordinate[0]), (xCoordinate[1], yCoordinate[1]), img, True, 0.005)

        #print(textOrigin)

        detectedLightText = cv.putText(img, f'LED {i}', textOrigin, cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv.LINE_AA)

    return img
    # print(len(contours))

# surroundingSizeFactor is the amount of which to increase the image area which is considered by this function
# Based on the size of the entire image (ex. if the image is 300x300, a 0.01 scale factor would add 3 pixels to each side of the rectangle of which is assessed in the averaging)
# Be aware that generally small scale factors are required.
def findAvgColor(startCoordinates, endCoordinates, img, drawShape=None, surroundingSizeFactor=0):
    X1, Y1 = startCoordinates
    X2, Y2 = endCoordinates

    if surroundingSizeFactor != 1:
        X1 = np.uint16(X1 - img.shape[1] * surroundingSizeFactor)
        Y1 = np.uint16(Y1 - img.shape[0] * surroundingSizeFactor)
        X2 = np.uint16(X2 + img.shape[1] * surroundingSizeFactor)
        Y2 = np.uint16(Y2 + img.shape[0] * surroundingSizeFactor)


    imageSection = img[Y1:Y2, X1:X2]

    #hsvImageSection = cv.cvtColor(imageSection, cv.COLOR_BGR2HSV)

    #cv.imshow('hi', hsvImageSection)

    # print(imageSection)
    averageRGBColor = np.mean(imageSection, axis = (0, 1))

    #averageHSVColor = np.mean(hsvImageSection, axis = (0, 1))


    if drawShape:
        rec = cv.rectangle(img, (X1, Y1), (X2, Y2), (255, 0, 0), 2)

    #print(averageHSVColor)


    # print(X1, X2)
    # print(Y1, Y2)

updatedImg = detectLEDs(ledImage)
cv.imshow('Circles?????', updatedImg)
cv.waitKey(0)
