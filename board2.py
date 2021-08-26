import cv2
import imutils
from shapely import coords
import aruco
import numpy as np
from shapely.geometry import Polygon
from typing import List

class Quad():
    def __init__(self, tl, tr, br, bl, name):
        self.tl = tl
        self.tr = tr
        self.br = br
        self.bl = bl
        self.name = name
    
    def coords(self):
        return np.array([self.tl, self.tr, self.br, self.bl])

    def polyCoords(self):
        return [self.coords()]
        
    def warpInverse(self, matrix):
        _, inv = cv2.invert(matrix) 
        x = np.array([[self.tl[0], self.tl[1]],
            [self.tr[0], self.tr[1]],
            [self.br[0], self.br[1]],
            [self.bl[0], self.bl[1]]])
        P = np.array([np.float32(x)])
        orig = cv2.perspectiveTransform(P,inv)
        
        print (f'orig={orig}')
        origint = np.around(orig).astype(int)[0]
        
        retval: Quad = Quad(origint[0], origint[1], origint[2], origint[3], self.name)
        return retval;

    def draw(self, img):
        cv2.polylines(img, self.polyCoords(), True, thickness=3, color=(0,0,255))
        cv2.putText(img, self.name, [self.bl[0] + 10, self.bl[1] - 10], cv2.FONT_HERSHEY_SIMPLEX, 2, color=(0,0,255), thickness=3, lineType=2)



class BoardFinder:
        
    def __init__(self, img):
        self.img = img


    def process(self, draw=True):
        self.rect = self.findCorners(self.img, draw)
        print(f'rect= {self.rect}')
        self.warpedImg, self.warpMatrix = self.getWarpBoard(self.img, self.rect)
        self.warpedSquares = self.getSquares(self.warpedImg, draw, draw)
        self.origSquares :  List[List[Quad]]= self.getOriginalSquares(self.warpMatrix, self.warpedSquares)
        return self
        
    def drawOrigSquares(self, img):
        for row in self.origSquares:
            for square in row:
                square.draw(img)

    
    def findCorners(self, img, draw=True):
        print(f'finding corners on: {img.shape}')
        bbox, ids = aruco.findArucoMarkers(img, draw=draw)
        ids = ids.flatten()
        tl = bbox[np.where(ids == 0)[0][0]][0][0].astype(int)
        tr = bbox[np.where(ids == 1)[0][0]][0][0].astype(int)
        br = bbox[np.where(ids == 2)[0][0]][0][0].astype(int)
        bl = bbox[np.where(ids == 3)[0][0]][0][0].astype(int)
        return np.array([tl, tr, br, bl], np.float32)

    def between(self, p1, p2, distance):
        x = (p2[0] - p1[0]) * distance + p1[0]
        y = (p2[1] - p1[1]) * distance + p1[1]
        return [int(x), int(y)]

    def getSquares(self, warpedImg, drawPoints=True, drawSquares=True):
        print(warpedImg.shape)
        maxHeight, maxWidth,  _ = warpedImg.shape
        points = []
        for j in range(0,9):
            yl = self.between([0,0], [0,maxHeight-1], j/8)
            row = []
            for i in range(0,9):
                bt = self.between(yl, [maxWidth-1,yl[1]], i/8)
                #print(bt)
                row.append(bt)
                #cv2.circle(warpedImg, bt, 10, (255,0,0), 3)
            points.append(row)
        #print(points)
        if drawPoints:
            for row in points:
                for point in row:
                    cv2.circle(warpedImg, point, 10, (255,0,0), 3)
            
        squares = []
        for i in range (0,8):
            row = []
            rowLabel = 8-i
            for j in range(0,8):
                columnLabel = chr(97 + j)
                s = Quad(points[i][j], points[i][j+1], points[i+1][j+1], points[i+1][j], f'{columnLabel}{rowLabel}')
                row.append(s)
                if drawSquares:
                    cv2.polylines(warpedImg, s.polyCoords(), True, thickness=3, color=(0,0,255))
                    cv2.putText(warpedImg, s.name, [s.bl[0] + 10, s.bl[1] - 10], cv2.FONT_HERSHEY_SIMPLEX, 2, color=(0,0,255), thickness=3, lineType=2)

            squares.append(row)

        return squares
        #s : Square = Square(points[0][0], points[0][1], points[1][1], points[1][0], 'a1')
        
    def getOriginalSquares(self, matrix, warpedSquares):
        retval = []
        for row in warpedSquares:
            newRow = []
            for square in row:
                newSquare = square.warpInverse(matrix)
                newRow.append(newSquare)
            retval.append(newRow)
        return retval

    def getWarpBoard(self, img, rect):
        tl, tr, br, bl = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        # ...and now for the height of our new image
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        # take the maximum of the width and height values to reach
        # our final dimensions
        maxWidth = max(int(widthA), int(widthB))
        maxHeight = max(int(heightA), int(heightB))
        # construct our destination points which will be used to
        # map the screen to a top-down, "birds eye" view
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]], dtype = "float32")
        # calculate the perspective transform matrix and warp
        # the perspective to grab the screen
        #print(rect)
        #print(dst)
        warpMatrix = cv2.getPerspectiveTransform(rect, dst)
        warp = cv2.warpPerspective(img, warpMatrix, (maxWidth, maxHeight))
        return warp, warpMatrix



if __name__ == "__main__":
    img = cv2.imread('./images/corners.jpg')
    ##cv2.imshow('img',img)
    #cv2.waitKey(0)
    board = BoardFinder(img).process(True)
    board.drawOrigSquares(img)
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