import cv2
import cv2.aruco as aruco
import numpy as np
import os
from fps import FPS
import imutils
from imutils.video import WebcamVideoStream
from shapely.geometry import Polygon
import datetime
import time

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

def doKeys(k, cap, img):

    if k == ord('1'):
        start = datetime.datetime.now()
        cap.set(3, 3264)
        cap.set(4, 2448)
        elapsed = (datetime.datetime.now() - start).total_seconds()
        print (f'elapsed = {elapsed}')
    if k == ord('2'):
        cap.set(3, 640)
        cap.set(4, 480)
    if k == ord('c'):
        timestr = time.strftime("%Y%m%d-%H%M%S")
        path = f'./images/{timestr}.jpg'
        cv2.imwrite(path, img)
        print (f'wrote image to {timestr}')
    if k == 27:
        return True
    else:
        return False

def drawStatus(bboxs, fps):
    if (bboxs is not None and len(bboxs) > 0):
        pgon = Polygon(bboxs[0][0]) # Assuming the OP's x,y coordinates
        
        disp = f'id: {ids[0][0]}    area: {pgon.area}    x:{bboxs[0][0][0][0]}  y:{bboxs[0][0][0][1]}   fps:{fps.checkFPS():.2f}'
        print(disp)
       
        fontScale              = 2
        fontColor              = (0,0,255)
        lineType               = 2
        cv2.putText(img,disp, 
            (100,100), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            fontScale,
            fontColor,
            thickness=6,
            lineType=lineType)
    else:
        print("------------")
            

if __name__ == "__main__":
    cap = cv2.VideoCapture(0)
    cap.set(3, 3264)
    cap.set(4, 2448)
    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
    fps = FPS(5).start()

    while True:
        ret, img = cap.read()
        bboxs, ids = findArucoMarkers(img)
        #drawStatus(bboxs, fps)
        resized = imutils.resize(img, 1000)
        cv2.imshow('img',resized)
        fps.updateAndPrintAndReset()
        
        k = cv2.waitKey(1) & 0xff
        quit = doKeys(k, cap, img)
        if (quit):
            break

    cap.release()
    cv2.destroyAllWindows()
