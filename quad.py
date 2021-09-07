from typing import Any
import cv2
import numpy as np
import matplotlib.path as mpltPath
import equipment
import chess
import collections
from dataclasses import dataclass

@dataclass(frozen=True)
class Quad():

    tl: Any
    tr: Any
    br: Any
    bl: Any
    name:str
    path: Any
    chessSquare: chess.Square

    #def __init__(self, tl, tr, br, bl, name):
        # self.tl = tl
        # self.tr = tr
        # self.br = br
        # self.bl = bl
        # self.name = name
        #self.path = mpltPath.Path([tl, tr, br, bl])
        #self.chessSquare = chess.parse_square(name)
    
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
        
        retval: Quad = Quad.createQuad(origint[0], origint[1], origint[2], origint[3], self.name)
        return retval;

    def createQuad(tl, tr, br, bl, name):
        return Quad(tl, tr, br, bl, name, path=mpltPath.Path([tl, tr, br, bl]), chessSquare=chess.parse_square(name))


    def draw(self, img, pieceCounts, pieceSet, drawCounts):
        piece, count = Quad.bestPiece(pieceCounts, pieceSet)
        
        pieceCountStr = ''
        if drawCounts:
            for key, val in pieceCounts.items():
                pieceCountStr += str(key) + ":" + str(val) + ","

        if (piece is None):
            cv2.polylines(img, self.polyCoords(), True, thickness=3, color=(0,0,255))
            cv2.putText(img, self.name, [self.bl[0] + 10, self.bl[1] - 10], cv2.FONT_HERSHEY_SIMPLEX, .5, color=(0,0,255), thickness=1, lineType=1)
        else:
            color = (255,255,255)
            if (count < 10):
                color = (0,255,255)
            cv2.polylines(img, self.polyCoords(), True, thickness=5, color=color)
            cv2.putText(img, f'{self.name}-{piece.symbol()} {pieceCountStr}', [self.bl[0] + 10, self.bl[1] - 10], cv2.FONT_HERSHEY_SIMPLEX, .5, color=color, thickness=1, lineType=1)

    def bestPiece(pieceCounts, pieceSet) -> chess.Piece:
        if (len(pieceCounts) == 0):
            return None, 0
        max = -1
        maxKey = -1
        for key, val in pieceCounts.items():
            if (val > max):
                max = val
                maxKey = key
        if max == 0:
            return None, 0
        else:
            return pieceSet[maxKey].chessPiece, max

    def scanPieces(self, points, ids):
        pieceCounts={}
        if len(points) > 0:
            results = self.path.contains_points(points)
            if (True in results):
                pieceCounts = collections.Counter(ids[np.where(results == True)])
        return pieceCounts


if __name__ == "__main__":
    
    ids = np.array([7,8,9,9,7,7])
    freq = collections.Counter(ids)
    print(len(freq))
    #y =  np.array([0,2])  #np.where(x==True)
    #z = ids[[0,2]]
    #print(z)