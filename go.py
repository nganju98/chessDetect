import cv2

import os

import numpy as np
from fps import FPS
import imutils

from shapely.geometry import Polygon
import datetime
import time
from board import Board
import pieces

from boardFinder import BoardFinder

from aruco import findArucoMarkers

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
    cfps = cap.get(cv2.CAP_PROP_FPS)
    print (f'capture fps = {cfps}')
    #cap.set(cv2.CAP_PROP_FPS, 30)
    fps = FPS(5).start()
    board = None
    while True:
        ret, img = cap.read()
        bbox = None
        ids = None
        if (board is not None and board.calibrateSuccess):
            #tl, tr, br, bl = board.rect
            bounding = np.asarray(Polygon(board.rect).bounds, dtype=np.int32)
            bboxs, ids = findArucoMarkers(img)
            
            #bboxs, ids = findArucoMarkers(img[bounding[1]:bounding[3], bounding[0]:bounding[2]])
        else:
            bboxs, ids = findArucoMarkers(img)
        
        if (board is None or not board.calibrateSuccess or
            board.cornersChanged(bboxs, ids) or
           (BoardFinder.idsPresent(ids) and board.ageInMs() > 4000)):
            board = Board(pieces.getCurrentSet(), pieces.getCurrentBoardWidthInMm())
            #print("procesing board")
            board.calibrate(img, bboxs, ids, False)
                
        if (board.calibrateSuccess):
            #print(board.ageInMs())
            board.markPieces(bboxs, ids, img)
            board.drawOrigSquares(img)
        
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
