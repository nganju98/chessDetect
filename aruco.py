
import cv2
from shapely.geometry.polygon import Polygon
import cv2.aruco as aruco
import numpy as np
import numpy.typing
import equipment

def getArucoVars():
    markerSize = 4
    totalMarkers = 50
    key = getattr(aruco, f'DICT_{markerSize}X{markerSize}_{totalMarkers}')
    arucoDict = aruco.Dictionary_get(key)
    arucoParam = aruco.DetectorParameters_create()
    #arucoParam.minMarkerPerimeterRate=.02
    ##arucoParam.maxErroneousBitsInBorderRate=.6
    #arucoParam.errorCorrectionRate=1
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

def findArucoMarkersInPolygon(img, polygon : Polygon, bufferInPixels, drawPolygon = False, drawMarkers = True):

    rect = [
        int(max(0, polygon.bounds[0] - bufferInPixels)), 
        int(max(0, polygon.bounds[1] - bufferInPixels)),
        int(min(img.shape[1] - 1, polygon.bounds[2] + bufferInPixels)),
        int(min(img.shape[0] - 1, polygon.bounds[3] + bufferInPixels))]
    xOffset = rect[0]
    yOffset = rect[1]
    bboxs, ids = findArucoMarkers(img[rect[1]:rect[3], rect[0]:rect[2]], drawMarkers)
    for bbox in bboxs:
            for box in bbox:
                for point in box:
                    point[0] = point[0] + xOffset
                    point[1] = point[1] + yOffset
                    

    return bboxs, ids

def getSizeInPixels(desiredSizeInMm, dpi):
    mmPerInch = 25.4
    pixelsPerMm = dpi / mmPerInch
    retval = pixelsPerMm * desiredSizeInMm
    return retval

def rint(input):
    return np.int32( np.round(input))

def generatePiece(piece : equipment.Piece, markerSizeInMm, bufferSizeInMm, dpi):

    markerSizeInPixels = rint(getSizeInPixels(markerSizeInMm, dpi))
    
    pieceSizeInPixels = getSizeInPixels(piece.diameterInMm, dpi)
    bufferSize = getSizeInPixels(bufferSizeInMm, dpi)

    imgSize = rint(2*markerSizeInPixels + 4 * bufferSize + pieceSizeInPixels)
    

    img = np.zeros((imgSize, imgSize), dtype="uint8")
    img.fill(255)
    arucoDict, _ = getArucoVars()
    cv2.circle(img, [rint(imgSize/2), rint(imgSize/2)], rint(pieceSizeInPixels/2), color=(0,0,0))
    cv2.putText(img, f'{piece.fullName}:{piece.diameterInMm}mm', [rint(imgSize/2 - pieceSizeInPixels/4), rint(imgSize/2)], 
        cv2.FONT_HERSHEY_SIMPLEX, .5, color=(0,0,0), thickness=1, lineType=cv2.LINE_AA)

    arucoImg = np.zeros((markerSizeInPixels, markerSizeInPixels), dtype="uint8") 
    cv2.aruco.drawMarker(arucoDict, piece.markerId, markerSizeInPixels, arucoImg, 1)
    
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
    dpi = 300
    bufferSizeInMm = 1
    pageWidth = 4 * dpi
    pageHeight = 6 * dpi
    
    buffer = 5 # dpi / 4
    sections = [[0,0], 
        [pageWidth / 2, 0], 
        [0, pageHeight / 3], 
        [pageWidth / 2, pageHeight / 3], 
        [0, 2 * pageHeight / 3], 
        [pageWidth / 2, 2 *  pageHeight / 3]]

    page1 = [('p', sections[0]), 
              ('p', sections[1]),
              ('p', sections[2]),
              ('p', sections[3]),
              ('p', sections[4]),
              ('p', sections[5])
    ]


    page2 = [('p', sections[0]), 
              ('p', sections[1]),
              ('q', sections[2]),
              ('k', sections[3]),
              ('r', sections[4]),
              ('r', sections[5])
    ]


    page3 = [('b', sections[0]), 
              ('b', sections[1]),
              ('n', sections[2]),
              ('n', sections[3]),
           
    ]
    pages = [page1, page2, page3]
    
    imageDict = {}
    for piece in equipment.SET2:
        img = generatePiece(piece, markerSizeInMm, bufferSizeInMm, dpi)
        imageDict[piece.abbrev] = img
        
        #cv2.imwrite(f'./images/set2_{piece.fullName}.png', img)
   
        #cv2.imshow("ArUCo Tag", img)
        #cv2.waitKey(0)

    for ctr, page in enumerate(pages):
        pageImage = np.zeros((pageHeight, pageWidth), dtype="uint8")
        pageImage.fill(255)
        for section in page:
            pieceName = section[0]
            pieceCoord = [ int(buffer + section[1][0]), int(buffer + section[1][1]) ]
            image : numpy.typing.NDArray = imageDict[pieceName]
            pageImage[pieceCoord[1]:pieceCoord[1] + image.shape[0], pieceCoord[0]:pieceCoord[0] + image.shape[1]] = image
        
        
        cv2.imwrite(f'./images/set2_black_page{ctr + 1}.png', pageImage)


    for ctr, page in enumerate(pages):
        pageImage = np.zeros((pageHeight, pageWidth), dtype="uint8")
        pageImage.fill(255)
        for section in page:
            pieceName = section[0].upper()
            pieceCoord = [ int(buffer + section[1][0]), int(buffer + section[1][1]) ]
            image : numpy.typing.NDArray = imageDict[pieceName]
            pageImage[pieceCoord[1]:pieceCoord[1] + image.shape[0], pieceCoord[0]:pieceCoord[0] + image.shape[1]] = image
        
        
        cv2.imwrite(f'./images/set2_white_page{ctr + 1}.png', pageImage)
