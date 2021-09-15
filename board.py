#from functools import cache
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
from quad import Quad
from copy import deepcopy
from camera import Frame
from collections import deque
from typing import Deque

class BoardCount:
    def __init__(self, count, frameNumber, frameTime):
        self.count = count
        self.frameNumber = frameNumber
        self.frameTime = frameTime
        

class BoardCountCache:
    def __init__(self, cacheSize = 10):
        self.cache : Deque = deque()
        self.count = {}
        self.cacheSize = cacheSize

    def append(self, boardCount: BoardCount):
        self.cache.append(boardCount)
        self.update(boardCount, True)
        if (len(self.cache) > self.cacheSize):
            removed = self.cache.popleft()
            self.update(removed, False)

    
    def update(self, boardCount : BoardCount, accumulate : bool):
        for key, val in boardCount.count.items():
            if (key not in self.count):
                self.count[key] = {}
            squareCounts = self.count[key]
            for markerId, count in val.items():
                if (markerId not in squareCounts):
                    squareCounts[markerId] = 0
                addend = count if accumulate else -count
                squareCounts[markerId] += addend

    def refresh(self):
        self.count = {}
        for boardCount in self.cache:
            self.update(boardCount, True)

    def clear(self):
        self.cache : Deque = deque()
        self.count = {}


class Board:
        
    def __init__(self, pieceSet, boardWidthInMm):
        self.pieceSet = pieceSet
        self.boardWidthInMm = boardWidthInMm
        self.buttonLocations = None

    def calibrate(self, frame : Frame, lastBoard : 'Board', profiler, draw=True):
        profiler.log(80, "Start calibrate")
        cornersFound = 0
        self.processed = datetime.datetime.now()
        img = frame.img
        if (lastBoard is not None and lastBoard.calibrateSuccess):
            cornersFound = BoardFinder.findCornersAtLastLocation(img, lastBoard.corners, lastBoard.pixelsPerMm)
            profiler.log(81, "Tested last corners")

        if (cornersFound >= 2):        
            self.corners = deepcopy(lastBoard.corners)
            self.buttonLocations = deepcopy(lastBoard.buttonLocations)
            self.rect = deepcopy(lastBoard.rect)
            self.pixelsPerMm = lastBoard.pixelsPerMm
            self.origSquares = lastBoard.origSquares #Quad is immutable so we can just take the references
            profiler.log(86, "Copied 5 params from last board")    
            self.calibrateSuccess = True      
        else:
            print(f'f:{frame.frameNumber} Need to recalibrate corners')
            bboxs, ids = aruco.findArucoMarkers(img, False)
            self.corners = BoardFinder.findCorners(bboxs, ids, img.shape)
            self.buttonLocations = Board.findButtonLocations(frame, bboxs, ids)
            if (self.corners is not None and self.buttonLocations is not None):
                print(f'f:{frame.frameNumber} Found corners and buttons')
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
                self.calibrateSuccess = True
            else:
                self.calibrateSuccess = False
            
        return self.calibrateSuccess
    

    def processButtons(self, frame: Frame, profiler):
        ids = None
        result = None
        img = frame.img
        if self.buttonLocations is None:
            print(f'f:{frame.frameNumber}: Cant process buttons, have no button locations')
        else:
            ids = []
            for location in self.buttonLocations:
                subImg = img[location[1]:location[3],location[0]:location[2]]
                bboxs, subIds = aruco.findArucoMarkers(subImg)
                if (subIds is not None):
                    ids.extend(subIds.flatten())
                cv2.rectangle(img, [location[0], location[1]], [location[2], location[3]], color=(0,255,0), thickness=2)

        
            if (len(ids) == 2):
                if (Marker.WHITE_BUTTON.value not in ids):
                    result = Marker.WHITE_BUTTON
                    #print('White button pressed ' + str(ids))
                    
                        
                elif (Marker.BLACK_BUTTON.value not in ids):
                    result = Marker.BLACK_BUTTON
                    #print('Black button pressed ' + str(ids))
        

        return result    

    def findButtonLocations(frame : Frame, bboxs, ids):
        if (ids is None):
            return None       
        ids = ids.flatten()
        marks = []
        whiteButtons = BoardFinder.markerFromId(bboxs, ids, Marker.WHITE_BUTTON)
        marks.extend(whiteButtons)
        blackButtons = BoardFinder.markerFromId(bboxs, ids, Marker.BLACK_BUTTON)
        marks.extend(blackButtons)
        if (len(marks) == 4):
            buttonLocations =[]
            for mark in marks:
                polygon = Polygon(mark)
                bufferSize = (polygon.bounds[2] - polygon.bounds[0]) / 4
                rect = [
                    int(max(0, polygon.bounds[0] - bufferSize)), 
                    int(max(0, polygon.bounds[1] - bufferSize)),
                    int(min(frame.img.shape[1] - 1, polygon.bounds[2] + bufferSize)),
                    int(min(frame.img.shape[0] - 1, polygon.bounds[3] + bufferSize))]
                buttonLocations.append(rect)
            print (f'f:{frame.frameNumber}: Success, found 4 buttons')
            return buttonLocations
        else:
            print(f'f:{frame.frameNumber}: Only found {len(marks)} buttons')
            return None


    def ageInMs(self):
        age : datetime.timedelta = datetime.datetime.now() - self.processed
        return age.total_seconds() * 1000

    def detectPieces(self, frame : Frame, profiler, draw=True):
        
        if (self.corners is None or self.rect is None or self.pixelsPerMm is None or not self.calibrateSuccess):
            raise RuntimeError("Attempt to detect pieces but self.corners is None")

        bboxs, ids = aruco.findArucoMarkersInPolygon(frame.img, Polygon(self.rect), self.pixelsPerMm * 5)
        
        profiler.log(82, "Detected arucos in board rectangle")

        if ids is None:
            ids = np.empty((0,0))
            
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
                    cv2.circle(frame.img, pieceCenter, 5, (0,255,0), 2)
                    
                pointList.append(pieceCenter)
                validIds.append(markerId)

        
        if (len(pointList)== 0):
            pass

        pointAry = np.asarray(pointList)
        validIdsAry = np.asarray(validIds)
        boardCounts = {} 
        for row in self.origSquares:
            square : Quad
            for square in row:
                squareCount = square.scanPieces(pointAry, validIdsAry)
                boardCounts[square.name] = squareCount
            
        
        profiler.log(82, "Processed squares to find contained arucos")
        return BoardCount(boardCounts, frame.frameNumber, frame.frameTime)


    def drawOrigSquares(self, img, boardCounts : BoardCount, pieceSet, drawPieceCount = False):
        for row in self.origSquares:
            square : Quad
            for square in row:
                pieceCounts = boardCounts.count[square.name] if square.name in boardCounts.count else {}
                square.draw(img, pieceCounts, pieceSet, drawPieceCount)

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
    #img = cv2.imread('./images/corners.jpg')
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