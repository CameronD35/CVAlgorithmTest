import cv2 as cv
import numpy as np

# Reads in the image
ledImage = cv.imread('purpleLED.jpg')

def detectLEDs(img):

    blank = np.zeros(img.shape[:2], dtype='uint8')

    #cv.imshow('blank', blank)

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

        innerArea = cv.ellipse(blank.copy(), center, axes, 0, 0, 360, 255, -1)
        findAvgColor((xCoordinate[0], yCoordinate[0]), (xCoordinate[1], yCoordinate[1]), img, innerArea, drawShape = True, surroundingSizeFactor = 0.005)

        detectedLight = cv.ellipse(img, center, axes, 0, 0, 360, (0, 255, 0), 2)
        detectedLightCenter = cv.circle(img, center, 1, (0, 0, 255), 3)

        textOrigin = center - 25

        #cv.imshow(f'hi{i}',innerArea)


        #print(textOrigin)

        detectedLightText = cv.putText(img, f'LED {i}', textOrigin, cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv.LINE_AA)

    return img
    # print(len(contours))

# innerArea is a binary image which contains the high intensity pixels (essentially where the LED is detected)

# interpretInnerArea is a boolean that tells the program to include interpretation of the detected LED. 
# IN most cases, due to the nature of cameras this will pollute the average with a TON of average

# surroundingSizeFactor is the amount of which to increase the image area which is considered by this function
# Based on the size of the entire image (ex. if the image is 300x300, a 0.01 scale factor would add 3 pixels to each side of the rectangle of which is assessed in the averaging)
# Be aware that generally small scale factors are required. Negative values are accepted.
def findAvgColor(startCoordinates, endCoordinates, img, innerArea, interpretInnerArea=False, drawShape=None, surroundingSizeFactor=0):

    # Create a blank to generate binary image later
    blank = np.zeros(img.shape[:2], dtype='uint8')
    X1, Y1 = startCoordinates
    X2, Y2 = endCoordinates

    imageSection = 0

    # If a surrounding size factor is selected, the area under consideration is changed (inc for +, dec for -)
    if surroundingSizeFactor != 0:
        X1 = np.uint16(X1 - img.shape[1] * surroundingSizeFactor)
        Y1 = np.uint16(Y1 - img.shape[0] * surroundingSizeFactor)
        X2 = np.uint16(X2 + img.shape[1] * surroundingSizeFactor)
        Y2 = np.uint16(Y2 + img.shape[0] * surroundingSizeFactor)

        # Skips interpretting the inner area
        if not interpretInnerArea:

            analysisArea = cv.rectangle(blank.copy(), (X1, Y1), (X2, Y2), 255, -1)

            mask = cv.bitwise_xor(innerArea, analysisArea)

            maskedImg = cv.bitwise_and(img, img, mask=mask)
            # cv.imshow(f'hi{i}', maskedImg)

            imageSection = maskedImg[Y1:Y2, X1:X2]

        # Includes inner area in interpretation
        else:

            imageSection = img[Y1:Y2, X1:X2]

    # Only interprets inner area
    else:

        imageSection = img[Y1:Y2, X1:X2]

    #hsvImageSection = cv.cvtColor(imageSection, cv.COLOR_BGR2HSV)

    #cv.imshow('hi', hsvImageSection)
    # print(imageSection)
    # print(imageSection)

    filteredSection = []

    # Removes any black pixels form the image as it can pollute averaging
    for pixelSet in imageSection:

        for pixel in pixelSet:

            pixelValue = sum(pixel)

            if pixelValue != 0:
                # print(pixel)
                filteredSection.append(pixel)

    # print(filteredSection)

    averageRGBColor = np.mean(filteredSection, axis = (0))


    hsvArray = convertBGRToHSV(averageRGBColor)

    color, colorDesc = determineColor(hsvArray)

    print(color, colorDesc)

    # Draws rectangle on the original image
    if drawShape:
        rec = cv.rectangle(img, (X1, Y1), (X2, Y2), (255, 0, 0), 2)

    #print(averageHSVColor)


    # print(X1, X2)
    # print(Y1, Y2)

# This function created with help from https://www.geeksforgeeks.org/program-change-rgb-color-model-hsv-color-model/
# This function takes an array of [b, g, r] format and converts it to [h, s, v]
def convertBGRToHSV(bgrArray):

    reducedArray = bgrArray/255

    # cMax is the color with the most intensity 
    cMax = np.max(reducedArray)

    # cMin is the color with the least intensity 
    cMin = np.min(reducedArray)

    diff = cMax - cMin

    blue, green, red = reducedArray

    hue, saturation, value = [0, 0, 0]

    if cMax == cMin:
        hue = 0

    if cMax == red:

        hue = ((60 * ((green - blue) / diff) + 360) % 360)

    elif cMax == green:

        hue = ((60 * ((blue - red) / diff) + 120) % 360)

    else:

        hue = ((60 * ((red - green) / diff) + 240) % 360)
    
    if cMax == 0:
        saturation = 0
    else:
        saturation = (diff / cMax) * 100
    
    value = cMax * 100

    hsvArray = np.array([hue, saturation, value])
    hsvArray = hsvArray.astype('uint16')

    return hsvArray

# This function takes a color array in the format of [h, s, v] and gets a rough determination of the color
def determineColor(hsvArray):

    saturation = hsvArray[1]
    saturationType = ''
    # Saturation Type Calculation
    if saturation >= 65:
        saturationType = 'Vivid'
    elif saturation >= 30:
        saturationType = 'Intermediate'
    else:
        saturationType = 'Dull'

    value = hsvArray[2]
    valueType = ''

    # Value Type Calculation
    if value >= 65:
        valueType = 'Bright'
    elif value >= 30:
        valueType = 'Midtone'
    else:
        valueType = 'Dark'

    hue = hsvArray[0]
    color = ''

    # A beautiful and elegant set of code
    # Trust me, I'm a professional
    if hue >= 300:
        color = 'Red'
    elif hue >= 250:
        color = 'Purple'
    elif hue >= 165:
        color = 'Purple'
    elif hue >= 85:
        color = 'Green'
    elif hue >= 55:
        color = 'Yellow'
    elif hue >= 15:
        color = 'Orange'
    else:
        color = 'Red'

    colorDescription = saturationType + ' ' + valueType + ' ' + color

    return color, colorDescription
    

updatedImg = detectLEDs(ledImage)
cv.imshow('Circles?????', updatedImg)
cv.waitKey(0)
