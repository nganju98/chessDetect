
import cv2
import cv2.aruco as aruco


def findArucoMarkers(img, markerSize = 4, totalMarkers=50, draw=True):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    key = getattr(aruco, f'DICT_{markerSize}X{markerSize}_{totalMarkers}')
    arucoDict = aruco.Dictionary_get(key)
    arucoParam = aruco.DetectorParameters_create()
    arucoParam.minMarkerPerimeterRate=.02
    arucoParam.maxErroneousBitsInBorderRate=.6
    arucoParam.errorCorrectionRate=1
    bboxs, ids, rejected = aruco.detectMarkers(gray, arucoDict, parameters = arucoParam)
    #print(rejected)
    #print(ids)
    if draw:
        aruco.drawDetectedMarkers(img, bboxs, ids) 
    return (bboxs, ids)

