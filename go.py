
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
        
        

    def doKeys(self, k, cap : Camera, img, profiler:Profiler):

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
            auto, focus = cap.getFocusParams()
            print(f'camera auto={auto}, focus={focus}' )
        if k == ord('j'):
            cap.focusDown()
        if k == ord('k'):
            cap.focusUp()


        if k == 27:
            return True
        else:
            return False


               

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

    def updateGame(self, boardCounts:BoardCount, gameStarted:bool, pieceSet : dict, gui:ChessGui, clickSound:pygame.mixer.Sound, profiler: Profiler):
        
        #empty = chess.STATUS_EMPTY in self.game.status()
        disappearedSquares = []
        appearedSquares = []

        if len(boardCounts.count) != 64:
            raise RuntimeError(f'Weird boardcounts, length={len(boardCounts)}')

        sufficientSamples = True
        for key, val in boardCounts.count.items():
            piece, pieceCount = Quad.bestPiece(val, pieceSet)
            if (piece is not None and pieceCount < 5):
                sufficientSamples = False
            square : chess.Square = chess.parse_square(key)
            if (piece is not None):
                if (piece !=  self.game.piece_at(square)):
                    appearedSquares.append( (square, piece ))
            else:
                if (self.game.piece_at(square) is not None):
                    disappearedSquares.append(square)
           
        profiler.log(51, "Looked at piece locations")
        if (gameStarted):
            if (sufficientSamples):
                if ( (len(disappearedSquares) > 0 or len(appearedSquares) > 0)):
                    
                    if (gameStarted and len(disappearedSquares) == 1 and len(appearedSquares) == 1):
                        uciMove = chess.Move.from_uci(f'{chess.square_name(disappearedSquares[0])}{chess.square_name(appearedSquares[0][0])}')
                        if (uciMove in self.game.legal_moves):
                            print(f'Adding move - {uciMove}')
                            self.game.push(uciMove)
                            threading.Thread(target=gui.updateChessBoard, args=(self.game.copy(),)).start()
                        else:
                            print(f'{uciMove} is an illegal move')
                    else:
                        print(f'Error: {len(disappearedSquares)} have disappeared pieces and {len(appearedSquares)} have appeared pieces')
                else:
                    print(f'Processed turn but insufficient moves detected: fromSquares={disappearedSquares}, toSquares={appearedSquares}')
            
            else:
                print("Insufficient samples")
                
        else:
            if (sufficientSamples):
                changed : bool = False
                for square,piece in appearedSquares:
                    self.game.set_piece_at(square, piece)
                    changed = True

                for square in disappearedSquares:
                    self.game.remove_piece_at(square)
                    changed = True
                
                if (changed):
                    threading.Thread(target=gui.updateChessBoard, args=(self.game.copy(),)).start()
                    threading.Thread(target=clickSound.play, args=()).start()
                
        
  
            
        return sufficientSamples
       
            

    def run(self, pieceSet, boardWidthInMm):
        gui : ChessGui = ChessGui()
        threading.Thread(target=gui.start, args=()).start()

        cap = Camera()
        pygame.init()
        buttonSound = pygame.mixer.Sound('./assets/blurp.wav')
        resolvedSound = pygame.mixer.Sound('./assets/resolved.wav')
        clickSound = pygame.mixer.Sound('./assets/click.wav')
        #cap.set(cv2.CAP_PROP_FPS, 30)
        fps = FPS(5).start()
        lastCalibratedBoard = None
        gameStarted = False
        buttonAlreadyDepressed = False
        processTurn = False
        recentCounts = BoardCountCache()
        
        while True:
            profiler = Profiler()
            frame = cap.read()
            profiler.log(1, "Read the frame")

            board = Board(pieceSet, boardWidthInMm)
            board.calibrate(frame, lastCalibratedBoard, profiler,False)
            profiler.log(2, "Calibrated board")
            if (board.calibrateSuccess):
                lastCalibratedBoard = board
                buttonPushed = board.processButtons(frame, profiler)
                if (buttonPushed is None):
                    buttonAlreadyDepressed = False
                elif (not buttonAlreadyDepressed):
                    threading.Thread(target=buttonSound.play, args=()).start()
                    if buttonPushed == equipment.Marker.WHITE_BUTTON:
                        print("White button press detected")
                        gui.whiteButtonPressed()
                    elif buttonPushed == equipment.Marker.BLACK_BUTTON:
                        print("Black button press detected")
                        gui.blackButtonPressed()
                    if (gameStarted):
                        processTurn = True
                        recentCounts = BoardCountCache()
                    else: 
                        gameStarted = True
                    buttonAlreadyDepressed = True

                profiler.log(3, "processed buttons")
            
                if (processTurn or not gameStarted):
                    boardCounts = board.detectPieces(frame, profiler, True)
                    recentCounts.append(boardCounts)
                    profiler.log(60, "Processed full board")
                    resolved = self.updateGame(recentCounts, gameStarted, pieceSet, gui, clickSound, profiler)
                    if (processTurn and resolved):
                        processTurn = False
                        threading.Thread(target=resolvedSound.play, args=()).start()
                        #threading.Thread(target=beepy.beep, args=("ready",)).start()

                    profiler.log(61, "Updated game")
                board.drawOrigSquares(frame.img, recentCounts, pieceSet, True)
                profiler.log(4, "Drew squares")
            else:
                print ("Board uncalibrated")
                lastCalibratedBoard = None

            self.showImage(frame.img, fps)
            profiler.log(4, "Show image")
            
            k = cv2.waitKey(1) & 0xff
            quit = self.doKeys(k, cap, frame.img, profiler)
            if (quit):
                break
            profiler.log(6, "Did keys")
            #fps.updateAndPrintAndReset(profiler)

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    Runner().run(equipment.getCurrentSet(), equipment.getCurrentBoardWidthInMm())