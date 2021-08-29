
import cv2
import cv2.aruco as aruco
import numpy as np


def getArucoVars():
    markerSize = 4
    totalMarkers = 50
    key = getattr(aruco, f'DICT_{markerSize}X{markerSize}_{totalMarkers}')
    arucoDict = aruco.Dictionary_get(key)
    arucoParam = aruco.DetectorParameters_create()
    arucoParam.minMarkerPerimeterRate=.02
    arucoParam.maxErroneousBitsInBorderRate=.6
    arucoParam.errorCorrectionRate=1
    return arucoDict, arucoParam


def findArucoMarkers(img, draw=True):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    arucoDict, arucoParam = getArucoVars()
    bboxs, ids, rejected = aruco.detectMarkers(gray, arucoDict, parameters = arucoParam)
    #print(rejected)
    #print(ids)
    if draw:
        aruco.drawDetectedMarkers(img, bboxs, ids) 
    return (bboxs, ids)


def getSizeInPixels(desiredSizeInMm, dpi = 300):
    mmPerInch = 25.4
    pixelsPerMm = dpi / mmPerInch
    retval = pixelsPerMm * desiredSizeInMm
    return retval

def rint(input):
    return np.int32( np.round(input))

def generatePiece(markerId, markerSizeInMm, pieceSizeInMm, bufferSizeInMm = 1):

    markerSizeInPixels = rint(getSizeInPixels(markerSizeInMm))
    
    pieceSizeInPixels = getSizeInPixels(pieceSizeInMm)
    bufferSize = getSizeInPixels(bufferSizeInMm)

    imgSize = rint(2*markerSizeInPixels + 4 * bufferSize + pieceSizeInPixels)
    

    img = np.zeros((imgSize, imgSize), dtype="uint8")
    img.fill(255)
    arucoDict, _ = getArucoVars()
    cv2.circle(img, [rint(imgSize/2), rint(imgSize/2)], rint(pieceSizeInPixels/2), color=(0,0,0))


    arucoImg = np.zeros((markerSizeInPixels, markerSizeInPixels), dtype="uint8") 
    cv2.aruco.drawMarker(arucoDict, markerId, markerSizeInPixels, arucoImg, 1)
    
    y = rint(bufferSize)
    x = rint(imgSize / 2 - markerSizeInPixels / 2)
    img[y: y+markerSizeInPixels, x:x+markerSizeInPixels] = arucoImg

    upsideDown = cv2.rotate(arucoImg, cv2.ROTATE_180)
    y= rint(imgSize - bufferSize - markerSizeInPixels)
    x = rint(imgSize / 2 - markerSizeInPixels / 2)
    img[y: y+markerSizeInPixels, x:x+markerSizeInPixels] = upsideDown

    rightSide = cv2.rotate(arucoImg, cv2.ROTATE_90_CLOCKWISE)
    y = rint(imgSize / 2 - markerSizeInPixels / 2)
    x = rint(imgSize - bufferSize - markerSizeInPixels)
    img[y: y+markerSizeInPixels, x:x+markerSizeInPixels] = rightSide

    leftSide = cv2.rotate(arucoImg, cv2.ROTATE_90_COUNTERCLOCKWISE)
    y = rint(imgSize / 2 - markerSizeInPixels / 2)
    x = rint(bufferSize)
    img[y: y+markerSizeInPixels, x:x+markerSizeInPixels] = leftSide

    borderedImg = cv2.copyMakeBorder(img, 
        1, 1, 1, 1, 
        cv2.BORDER_CONSTANT, value=[0,0,0])
    return borderedImg

if __name__ == "__main__":
    markerSizeInMm = 7
    pieceSizeInMm = 30
    img = generatePiece(10, markerSizeInMm, pieceSizeInMm)
    cv2.imwrite("./images/pawn.png", img)
    cv2.imshow("ArUCo Tag", img)
    cv2.waitKey(0)