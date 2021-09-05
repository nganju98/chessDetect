import cv2
import cv2.aruco as aruco
import numpy as np
from shapely.geometry import Polygon
import os
from imutils.video import FPS
from imutils.video import WebcamVideoStream

def findArucoMarkers(img, markerSize = 6, totalMarkers=250, draw=True):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    key = getattr(aruco, f'DICT_{markerSize}X{markerSize}_{totalMarkers}')
    arucoDict = aruco.Dictionary_get(key)
    arucoParam = aruco.DetectorParameters_create()
    bboxs, ids, rejected = aruco.detectMarkers(gray, arucoDict, parameters = arucoParam)
    #print(ids)
    if (ids is not None):
        size = bboxs[0][0][1][0] - bboxs[0][0][0][0] 
        print(f'{ids} :: {size} :: {bboxs[0][0]}')
        pgon = Polygon(bboxs[0][0]) # Assuming the OP's x,y coordinates
        print(f'area = {pgon.area}' )
    else:
        print ("-------")
    if draw:
        aruco.drawDetectedMarkers(img, bboxs) 


img = cv2.imread('./test1.bmp')
print(img.shape)
findArucoMarkers(img, 4, 50)
#gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
cv2.imshow('img',img)
cv2.imwrite('./test1.jpg', img)
cv2.waitKey(0)
cv2.destroyAllWindows()
#k = cv2.waitKey(30) & 0xff

#cap.release()
#cv2.destroyAllWindows()
