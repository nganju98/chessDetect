import cv2
import imutils
from shapely import coords
import aruco
import numpy as np
from shapely.geometry import Polygon
from shapely.geometry import Point
from timeit import default_timer as timer
import datetime

from boardFinder import BoardFinder


class Board:
        
    def __init__(self, img, bboxs, ids):
        self.img = img
        self.bboxs = bboxs
        self.ids = ids

    def calibrate(self, draw=True):
        self.processed = datetime.datetime.now()
        self.rect = BoardFinder.findCorners(self.bboxs, self.ids)
        if (self.rect is not None):
            self.warpedImg, self.warpMatrix, self.warpWidth, self.warpHeight = BoardFinder.getWarpBoard(self.img, self.rect, draw)
            
            self.warpedSquares = BoardFinder.getSquares(self.warpedImg, self.warpWidth, self.warpHeight, draw, draw)
            
            self.origSquares = BoardFinder.getOriginalSquares(self.warpMatrix, self.warpedSquares)
            self.calibrateSuccess = True
        else:
            self.calibrateSuccess = False
        return self.calibrateSuccess
        
    def ageInMs(self):
        age : datetime.timedelta = datetime.datetime.now() - self.processed
        return age.total_seconds() * 1000

       

    def markPieces(self, bboxs, ids):
        
        if ids is None:
            return
        idAry = ids.flatten()
        for row in self.origSquares:
            for square in row:
                square.piece = None
        pointList = []
        validIds = []
        for (markerCorner, markerId) in zip(bboxs, idAry):
		# extract the marker corners (which are always returned in
		# top-left, top-right, bottom-right, and bottom-left order)
            if (markerId >= 10):
                if (markerId >= 28):
                    print(markerId)
                corners = markerCorner.reshape((4, 2))
                (topLeft, topRight, bottomRight, bottomLeft) = corners
                pointList.append(bottomLeft)
                validIds.append(markerId)
                #print(f'found one at {bottomLeft}')
                #self.markOrigSquare(bottomLeft, markerId)
        pointAry = np.asarray(pointList)
        validIdsAry = np.asarray(validIds)
        for row in self.origSquares:
            for square in row:
                square.scanPieces(pointAry, validIdsAry)


    def drawOrigSquares(self, img):
        for row in self.origSquares:
            for square in row:
                square.draw(img)

    def cornersChanged(self, bboxs, ids):
        if (not BoardFinder.idsPresent(ids)):
            return False
        newBox = BoardFinder.findCorners(bboxs, ids)
        total = 0
        for i in range(0,3):
            dist = np.sqrt( (newBox[i][0] - self.rect[i][0])**2 + (newBox[i][1] - self.rect[i][1])**2 )
            total += dist
        #print(f'corner displacement = {dist}')
        if (dist > 5):
            print (f'corners changed by: {dist}')
            return True
        else:
            return False
        

if __name__ == "__main__":
    img = cv2.imread('./images/corners.jpg')
    ##cv2.imshow('img',img)
    #cv2.waitKey(0)
    #board = BoardFinder(img).process(True)
    #board.drawOrigSquares(img)
    #board.drawOrigSquares(img)
    # finder = BoardFinder()

    # rect = finder.findCorners(img)
    # print(f'rect= {rect}')
    # warpedImg, warpMatrix = finder.getWarpBoard(img, rect)
    # warpedSquares = finder.getSquares(warpedImg)
    # origSquares :  List[List[Quad]]= finder.getOriginalSquares(warpMatrix, warpedSquares)
    # for row in origSquares:
    #     for square in row:
    #         square.draw(img)
    #test : Quad = squares[0][0].warpInverse(warpMatrix)
    #cv2.polylines(img, test.polyCoords(), True, thickness=3, color=(0,0,255))
                
    # print("************")
    # print(tl)
    # print(tr)

    # print(bt)
    # cv2.circle(img, tl, 10, (255,0,0), 3)
    # cv2.circle(img, tr, 10, (255,0,0), 3)
    # cv2.circle(img, bl, 10, (255,0,0), 3)
    # cv2.circle(img, br, 10, (255,0,0), 3)

    # cv2.line(img, tl, tr, (255,0,0), 3)

    resized = imutils.resize(img, 800)
    cv2.imshow('img',resized)
    cv2.waitKey(0)
    cv2.destroyAllWindows()