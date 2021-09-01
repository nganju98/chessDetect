import cv2
import imutils
from shapely import coords
import aruco
import numpy as np
from shapely.geometry import Polygon
from shapely.geometry import Point
from timeit import default_timer as timer
import datetime
from equipment import Marker, Piece
from boardFinder import BoardFinder



class Board:
        
    def __init__(self, pieceSet, boardWidthInMm):
        self.pieceSet = pieceSet
        self.boardWidthInMm = boardWidthInMm

    def calibrate(self, img, lastBoard : 'Board', profiler, draw=True):
        profiler.log(80, "Start calibrate")
        cornersFound = 0
        self.processed = datetime.datetime.now()
        if (lastBoard is not None and lastBoard.calibrateSuccess):
            cornersFound = BoardFinder.findCornersAtLastLocation(img, lastBoard.corners, lastBoard.pixelsPerMm)
            profiler.log(81, "Tested last corners")

        if (cornersFound >= 2):        
            self.corners = lastBoard.corners   
            self.calibrateSuccess = True
            
        else:
            print("Need to recalibrate corners")
            bboxs, ids = aruco.findArucoMarkers(img)
            self.corners = BoardFinder.findCorners(bboxs, ids, img.shape)

        
        if (self.corners is not None):
            self.calibrateSuccess = True
        else:
            self.calibrateSuccess = False
            
        return self.calibrateSuccess
        
    def ageInMs(self):
        age : datetime.timedelta = datetime.datetime.now() - self.processed
        return age.total_seconds() * 1000

    def detectPieces(self, img, profiler, draw=True):
        
        if (self.corners is None):
            raise RuntimeError("Attempt to detect pieces but self.corners is None")

        self.rect = np.asarray([self.corners[0][0], self.corners[1][0], 
        self.corners[2][0], self.corners[3][0]], dtype=np.float32)
        
        avgLength = ((self.rect[1][0] - self.rect[0][0]) +
                (self.rect[2][0] - self.rect[3][0]) +
                (self.rect[3][1] - self.rect[0][1]) +
                (self.rect[2][1] - self.rect[1][1])) / 4
        self.pixelsPerMm = avgLength/self.boardWidthInMm

        warpedImg, warpMatrix, warpWidth, warpHeight = BoardFinder.getWarpBoard(img, self.rect, draw)
        
        warpedSquares = BoardFinder.getSquares(warpedImg, warpWidth, warpHeight, draw, draw)
        _, inverseMatrix = cv2.invert(warpMatrix)
        self.origSquares = BoardFinder.getOriginalSquares(inverseMatrix, warpedSquares)
        profiler.log(81, "Found original squares")

        bboxs, ids = aruco.findArucoMarkersInPolygon(img, Polygon(self.rect), self.pixelsPerMm * 5)
        
        profiler.log(82, "Detected arucos in board rectangle")

        if ids is None:
            return
        idAry = ids.flatten()
        
        pointList = []
        validIds = []
        for (markerCorner, markerId) in zip(bboxs, idAry):
            if (markerId in self.pieceSet):
                corners = markerCorner.reshape((4, 2))
                
                piece : Piece = self.pieceSet[markerId]
                pixelLength = self.pixelsPerMm * (piece.diameterInMm / 2)
                pieceCenter = BoardFinder.getPieceCenter(corners, pixelLength)
                if draw:
                    cv2.circle(img, pieceCenter, 5, (0,255,0), 2)
                    
                pointList.append(pieceCenter)
                validIds.append(markerId)
                
        if (len(pointList) > 0):
            pointAry = np.asarray(pointList)
            validIdsAry = np.asarray(validIds)
            for row in self.origSquares:
                for square in row:
                    square.scanPieces(pointAry, validIdsAry)

        profiler.log(82, "Processed squares to find contained arucos")


    def drawOrigSquares(self, img):
        for row in self.origSquares:
            for square in row:
                square.draw(img)

    # def cornersChanged(self, bboxs, ids):
    #     if (not BoardFinder.idsPresent(ids)):
    #         return False
    #     newBox = BoardFinder.findCorners(bboxs, ids)
    #     total = 0
    #     for i in range(0,3):
    #         dist = np.sqrt( (newBox[i][0] - self.rect[i][0])**2 + (newBox[i][1] - self.rect[i][1])**2 )
    #         total += dist
    #     #print(f'corner displacement = {dist}')
    #     if (dist > 5):
    #         print (f'corners changed by: {dist}')
    #         return True
    #     else:
    #         return False
        

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