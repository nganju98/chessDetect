import cv2

import os
from fps import FPS
import imutils

from shapely.geometry import Polygon
import datetime
import time
from board import Board
import pieces

from boardFinder import BoardFinder

from aruco import findArucoMarkers

class Runner:
        
    def __init__(self):
        self.zoom = False
        self.zoomX = 0
        self.zoomY = 0
        self.zoomFactor = 8
        self.imgShape = None

    def doKeys(self, k, cap, img):

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
        if k == ord('z'):
            self.zoom = not self.zoom
        if k == ord('s'):
            self.zoomY +=  int(0.75 * img.shape[0]/self.zoomFactor)
            self.zoomY = min(self.zoomY,int( img.shape[0] - img.shape[0]/self.zoomFactor))
        if k == ord('w'):
            self.zoomY -= int((0.75 * img.shape[0]/self.zoomFactor))
            self.zoomY = max(0, self.zoomY)
        if k == ord('a'):
            self.zoomX -= int(0.75 * img.shape[1]/self.zoomFactor)
            self.zoomX = max(0, self.zoomX)
        if k == ord('d'):
            self.zoomX += int(0.75 * img.shape[1]/self.zoomFactor)
            self.zoomX = min(self.zoomX, int( img.shape[1] - img.shape[1]/self.zoomFactor ))

        if k == 27:
            return True
        else:
            return False

    def drawStatus(self, bboxs, fps, img):
        if (bboxs is not None and len(bboxs) > 0):
            
            disp = f'   fps:{fps.checkFPS():.2f}'
            #print(disp)
        
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
                

    def run(self):
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
            
            self.drawStatus(bboxs, fps, img)
            show = None
            if (self.zoom):
                img.shape[0]
                show = img[self.zoomY:self.zoomY + int(img.shape[0]/self.zoomFactor), self.zoomX:self.zoomX+int(img.shape[1]/self.zoomFactor)]
                show = imutils.resize(show, 1000)
            else:
                show = imutils.resize(img, 1000)
            
            cv2.imshow('img',show)
            fps.updateAndPrintAndReset()
            
            k = cv2.waitKey(1) & 0xff
            quit = self.doKeys(k, cap, img)
            if (quit):
                break

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    Runner().run()