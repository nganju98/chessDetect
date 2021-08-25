import cv2
import imutils
from shapely import coords
import go
import numpy as np
from shapely.geometry import Polygon

class Square():
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
        


class BoardFinder:
        
    def findCorners(self, img):
        print(f'finding corners on: {img.shape}')
        bbox, ids = go.findArucoMarkers(img)
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
                print(bt)
                row.append(bt)
                #cv2.circle(warpedImg, bt, 10, (255,0,0), 3)
            points.append(row)
        print(points)

        for row in points:
            for point in row:
                cv2.circle(warpedImg, point, 10, (255,0,0), 3)
        
        squares = []
        for i in range (0,8):
            row = []
            for j in range(0,8):
                s = Square(points[i][j], points[i][j+1], points[i+1][j+1], points[i+1][j], f'{i}-{j}')
                row.append(s)
                cv2.polylines(warpedImg, s.polyCoords(), True, thickness=3, color=(0,0,255))

            squares.append(row)


        #s : Square = Square(points[0][0], points[0][1], points[1][1], points[1][0], 'a1')
        


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

img = cv2.imread('./images/corners.jpg')
##cv2.imshow('img',img)
#cv2.waitKey(0)
finder = BoardFinder()

rect = finder.findCorners(img)
warpedImg, warpMatrix = finder.getWarpBoard(img, rect)
finder.getSquares(warpedImg)
print(warpedImg.shape)
# print("************")
# print(tl)
# print(tr)

# print(bt)
# cv2.circle(img, tl, 10, (255,0,0), 3)
# cv2.circle(img, tr, 10, (255,0,0), 3)
# cv2.circle(img, bl, 10, (255,0,0), 3)
# cv2.circle(img, br, 10, (255,0,0), 3)

# cv2.line(img, tl, tr, (255,0,0), 3)

resized = imutils.resize(warpedImg, 800)
cv2.imshow('img',resized)
cv2.waitKey(0)
cv2.destroyAllWindows()