import cv2
import numpy as np
import matplotlib.path as mpltPath

class Quad():
    def __init__(self, tl, tr, br, bl, name):
        self.tl = tl
        self.tr = tr
        self.br = br
        self.bl = bl
        self.name = name
        self.piece = None
        self.path = mpltPath.Path([tl, tr, br, bl])
    
    def coords(self):
        return np.array([self.tl, self.tr, self.br, self.bl])

    def polyCoords(self):
        return [self.coords()]
        
    def warpInverse(self, inverseMatrix):
        #_, inv = cv2.invert(matrix) 
        x = np.array([[self.tl[0], self.tl[1]],
            [self.tr[0], self.tr[1]],
            [self.br[0], self.br[1]],
            [self.bl[0], self.bl[1]]])
        P = np.array([np.float32(x)])
        orig = cv2.perspectiveTransform(P,inverseMatrix)
        
        #print (f'orig={orig}')
        origint = np.around(orig).astype(int)[0]
        
        retval: Quad = Quad(origint[0], origint[1], origint[2], origint[3], self.name)
        return retval;

    def draw(self, img):
        if (self.piece is None):
            cv2.polylines(img, self.polyCoords(), True, thickness=3, color=(0,0,255))
            cv2.putText(img, self.name, [self.bl[0] + 10, self.bl[1] - 10], cv2.FONT_HERSHEY_SIMPLEX, 2, color=(0,0,255), thickness=3, lineType=2)
        else:
            cv2.polylines(img, self.polyCoords(), True, thickness=3, color=(255,255,255))
            cv2.putText(img, f'{self.name} :: {self.piece}', [self.bl[0] + 10, self.bl[1] - 10], cv2.FONT_HERSHEY_SIMPLEX, 2, color=(255,255,255), thickness=3, lineType=2)


    def scanPieces(self, points, ids):
        #polygon = Polygon(self.coords())
        #return polygon.contains(Point(point[0], point[1]))
        #return True
        x = self.path.contains_points(points)
        if (True in x):
            self.piece = ids[np.where(x == True)][0]
            #print ('found a piece')
        return x
