import cv2
import numpy as np
import matplotlib.path as mpltPath
import equipment
import chess
import collections

class Quad():
    def __init__(self, tl, tr, br, bl, name):
        self.tl = tl
        self.tr = tr
        self.br = br
        self.bl = bl
        self.name = name
        self.pieces = {}
        self.path = mpltPath.Path([tl, tr, br, bl])
        self.chessSquare = chess.parse_square(name)
    
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
        piece = self.bestPiece()
        if (piece is None):
            cv2.polylines(img, self.polyCoords(), True, thickness=3, color=(0,0,255))
            cv2.putText(img, self.name, [self.bl[0] + 10, self.bl[1] - 10], cv2.FONT_HERSHEY_SIMPLEX, 1, color=(0,0,255), thickness=3, lineType=2)
        else:
            cv2.polylines(img, self.polyCoords(), True, thickness=3, color=(255,255,255))
            piece : equipment.Piece = self.bestPiece()
            #ids = ",".join(map(str,self.pieces))
            cv2.putText(img, f'{self.name}-{piece.abbrev}', [self.bl[0] + 10, self.bl[1] - 10], cv2.FONT_HERSHEY_SIMPLEX, 1, color=(255,255,255), thickness=3, lineType=2)

    def bestPiece(self) -> equipment.Piece:
        if (len(self.pieces) == 0):
            return None
        max = 0
        maxKey = -1
        for key, val in self.pieces.items():
            if (val > max):
                max = val
                maxKey = key
        return equipment.getCurrentSet()[maxKey]

    def scanPieces(self, points, ids):
        self.pieces=[]
        x = self.path.contains_points(points)
        if (True in x):
            self.pieces = collections.Counter(ids[np.where(x == True)])
        return x


if __name__ == "__main__":
    
    ids = np.array([7,8,9,9,7,7])
    freq = collections.Counter(ids)
    print(len(freq))
    #y =  np.array([0,2])  #np.where(x==True)
    #z = ids[[0,2]]
    #print(z)