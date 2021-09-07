
from camera import *
import pygame
from quad import Quad
import numpy as np
#from game import Game
import cv2
from fps import FPS
import imutils

from shapely.geometry import Polygon
import datetime
import time
from board import *
import equipment
from boardFinder import BoardFinder
import threading
from aruco import findArucoMarkers
from profiler import Profiler
import chess
import chess.svg
from gui import ChessGui

class Runner:
        
    def __init__(self):
        self.zoom = False
        self.zoomX = 0
        self.zoomY = 0
        self.zoomFactor = 8
        self.buttonLocations = None
        self.game = chess.Board.empty()
        
        

    def doKeys(self, k, cap, img, profiler:Profiler):

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
        if k == ord('p'):
            profiler.output()
        if k == ord('f'):
            print(cap.get(cv2.CAP_PROP_FOCUS))

        if k == 27:
            return True
        else:
            return False


               

    def processButtons(self, img, profiler):
        ids = None
        if self.buttonLocations is None:
            bboxs, ids = findArucoMarkers(img)
            if (ids is None):
                ids = np.empty([1,1])
            ids = ids.flatten()
            marks = []
            whiteButtons = BoardFinder.markerFromId(bboxs, ids, equipment.Marker.WHITE_BUTTON)
            marks.extend(whiteButtons)
            blackButtons = BoardFinder.markerFromId(bboxs, ids, equipment.Marker.BLACK_BUTTON)
            marks.extend(blackButtons)
            self.buttonLocations =[]
           
            for mark in marks:
                polygon = Polygon(mark)
                bufferSize = (polygon.bounds[2] - polygon.bounds[0]) / 2
                rect = [
                    int(max(0, polygon.bounds[0] - bufferSize)), 
                    int(max(0, polygon.bounds[1] - bufferSize)),
                    int(min(img.shape[1] - 1, polygon.bounds[2] + bufferSize)),
                    int(min(img.shape[0] - 1, polygon.bounds[3] + bufferSize))]
                self.buttonLocations.append(rect)
        else:
            ids = []
            for location in self.buttonLocations:
                subImg = img[location[1]:location[3],location[0]:location[2]]
                bboxs, subIds = findArucoMarkers(subImg)
                if (subIds is not None):
                    ids.extend(subIds.flatten())
                cv2.rectangle(img, [location[0], location[1]], [location[2], location[3]], color=(0,255,0), thickness=2)

        result = None
        if (len(ids) > 1):
            if (equipment.Marker.WHITE_BUTTON.value not in ids):
                result = equipment.Marker.WHITE_BUTTON
                print('White button pressed ' + str(ids))
                
                    
            elif (equipment.Marker.BLACK_BUTTON.value not in ids):
                result = equipment.Marker.BLACK_BUTTON
                print('Black button pressed ' + str(ids))
        else:
            print("Couldn't find buttons")

        return result    

    def showImage(self, img, fps : FPS):
        show = None
        if (self.zoom):
            img.shape[0]
            show = img[self.zoomY:self.zoomY + int(img.shape[0]/self.zoomFactor), self.zoomX:self.zoomX+int(img.shape[1]/self.zoomFactor)]
            show = imutils.resize(show, 1000)
        else:
            show = imutils.resize(img, 1000)
        
        disp = f'fps:{fps.checkFPS():.2f}, zoomxy={self.zoomX},{self.zoomY}'
        #print(disp)
    
        fontScale              = 0.5
        fontColor              = (0,255,0)
        lineType               = 2
        cv2.putText(show,disp, 
            (20,20), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            fontScale,
            fontColor,
            thickness=1,
            lineType=lineType)
        cv2.imshow('img',show)

    def updateGame(self, boardCounts:BoardCount, gameStarted:bool, pieceSet : dict, gui:ChessGui, profiler: Profiler):
        
        #empty = chess.STATUS_EMPTY in self.game.status()
        fromSquares = []
        toSquares = []

        if len(boardCounts.count) != 64:
            raise RuntimeError(f'Weird boardcounts, length={len(boardCounts)}')

        for key, val in boardCounts.count.items():
            piece, _ = Quad.bestPiece(val, pieceSet)
            square : chess.Square = chess.parse_square(key)
            if (piece is not None):
                if (piece !=  self.game.piece_at(square)):
                    toSquares.append(square)
                    if(not gameStarted):
                        self.game.set_piece_at(square, piece)
            else:
                if (self.game.piece_at(square) is not None):
                    fromSquares.append(square)
                    if(not gameStarted):
                        self.game.remove_piece_at(square)
           
        profiler.log(51, "Updated game")

        if (len(fromSquares) > 0 or len(toSquares) > 0):
           
            if (gameStarted):
                if (len(fromSquares) == 1 and len(toSquares) == 1):
                    uciMove = f'{chess.square_name(fromSquares[0])}{chess.square_name(toSquares[0])}'
                    print(f'Adding move - {uciMove}')
                    self.game.push_uci(uciMove)
                else:
                    print(f'Error: {len(fromSquares)} have disappeared pieces and {len(toSquares)} have appared pieces')
            
            #svg = chess.svg.board(self.game, lastmove=lastmove)
            
            threading.Thread(target=gui.updateChessBoard, args=(self.game.copy(),)).start()
            #gui.updateChessBoard(self.game.copy())
            profiler.log(52, "Generated SVG")
  
            
        return True
       
            

    def run(self, pieceSet, boardWidthInMm):
        gui : ChessGui = ChessGui()
        threading.Thread(target=gui.start, args=()).start()

        cap = Camera()
        pygame.init()
        buttonSound = pygame.mixer.Sound('./assets/blurp.wav')
        #cap.set(cv2.CAP_PROP_FPS, 30)
        fps = FPS(5).start()
        lastCalibratedBoard = None
        gameStarted = False
        buttonDepressed = False
        processTurn = False
        recentCounts = BoardCountCache()
        
        while True:
            profiler = Profiler()
            frame = cap.read()
            profiler.log(1, "Read the frame")

            buttonPushed = self.processButtons(frame.img, profiler)
            if (buttonPushed is None):
                buttonDepressed = False
            else:
                if (not buttonDepressed):
                    threading.Thread(target=buttonSound.play, args=()).start()
                buttonDepressed = True
                processTurn = True
                gameStarted = True

            profiler.log(2, "processed buttons")
            board = Board(pieceSet, boardWidthInMm)
            board.calibrate(frame.img, lastCalibratedBoard, profiler,False)
            profiler.log(3, "Calibrated board")
            if(board.calibrateSuccess):
                lastCalibratedBoard = board
                profiler.log(4, "Drew squares")
                boardCounts = {}
                if (processTurn or not gameStarted):
                    boardCounts = board.detectPieces(frame, profiler, True)
                    recentCounts.append(boardCounts)
                    profiler.log(60, "Processed full board")
                    resolved = self.updateGame(recentCounts, gameStarted, pieceSet, gui, profiler)
                    if (processTurn and resolved):
                        processTurn = False
                        #threading.Thread(target=beepy.beep, args=("ready",)).start()

                    profiler.log(61, "Updated game")
                board.drawOrigSquares(frame.img, recentCounts, pieceSet, True)
            
            self.showImage(frame.img, fps)
            profiler.log(4, "Show image")
            
            k = cv2.waitKey(1) & 0xff
            quit = self.doKeys(k, cap, frame.img, profiler)
            if (quit):
                break
            profiler.log(6, "Did keys")
            fps.updateAndPrintAndReset(profiler)

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    Runner().run(equipment.getCurrentSet(), equipment.getCurrentBoardWidthInMm())