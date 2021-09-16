
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
from enum import Enum

class GameState(Enum):
    PREGAME = 0
    WAITING_FOR_TURN = 1
    PROCESS_TURN = 2
    INVALID_MOVE = 3

class AlertSound(Enum):
    BUTTON = 0
    RESOLVED = 1
    CLICK = 2
    ERROR = 3
class Runner:
        
    def __init__(self, pieceSet, boardWidthInMm):
        self.zoom = False
        self.zoomX = 0
        self.zoomY = 0
        self.zoomFactor = 8
        self.pieceSet = pieceSet
        self.boardWidthInMm = boardWidthInMm
        self.game = chess.Board.empty()
        self.sounds = {}
        self.gui : ChessGui = ChessGui()
        threading.Thread(target=self.gui.start, args=()).start()
        pygame.init()
        for sound in AlertSound:
            filename = f'./assets/{sound.name.lower()}.wav'
            self.sounds[sound.name] = pygame.mixer.Sound(filename)
        
    def playSound(self, soundName : AlertSound):
        sound = self.sounds[soundName.name]
        threading.Thread(target=sound.play, args=()).start()
                

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



               

    def showImage(self, img, fps : FPS, gameState : GameState):
        show = None
        if (self.zoom):
            img.shape[0]
            show = img[self.zoomY:self.zoomY + int(img.shape[0]/self.zoomFactor), self.zoomX:self.zoomX+int(img.shape[1]/self.zoomFactor)]
            show = imutils.resize(show, 1000)
        else:
            show = imutils.resize(img, 1000)
        
        disp = f'fps:{fps.checkFPS():.2f}, zoomxy={self.zoomX},{self.zoomY}, state={gameState.name}'
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

    def getBoardChanges(self, boardCounts:BoardCountCache):
        disappearedSquares = []
        appearedSquares = []

        if len(boardCounts.count) != 64:
            raise RuntimeError(f'Weird boardcounts, length={len(boardCounts)}')

        sufficientSamples = True
        for key, val in boardCounts.count.items():
            piece, pieceCount = Quad.bestPiece(val, self.pieceSet)
            if (piece is not None and pieceCount < 5):
                sufficientSamples = False
            square : chess.Square = chess.parse_square(key)
            if (piece is not None):
                if (piece !=  self.game.piece_at(square)):
                    appearedSquares.append( (square, piece ))
            else:
                if (self.game.piece_at(square) is not None):
                    disappearedSquares.append(square)
        return sufficientSamples, appearedSquares, disappearedSquares

        
    def pregame(self, frame:Frame, board: Board, recentCounts:BoardCountCache, profiler: Profiler):
        nextState = GameState.PREGAME
        buttonPushed = board.processButtons(frame, profiler)
        if buttonPushed == equipment.Marker.BLACK_BUTTON:
            print(f'f:{frame.frameNumber} Black button press detected')
            success = self.gui.blackButtonPressed()
            if (success):
                nextState = GameState.WAITING_FOR_TURN
                self.playSound(AlertSound.BUTTON)
        boardCounts = board.detectPieces(frame, profiler, True)
        recentCounts.append(boardCounts)
        profiler.log(60, "Processed full board")
        sufficientSamples, appearedSquares, disappearedSquares = self.getBoardChanges(recentCounts)
        if (sufficientSamples):
            changed : bool = False
            for square,piece in appearedSquares:
                self.game.set_piece_at(square, piece)
                changed = True
            for square in disappearedSquares:
                self.game.remove_piece_at(square)
                changed = True        
            if (changed):
                threading.Thread(target=self.gui.updateChessBoard, args=(self.game.copy(),)).start()
                self.playSound(AlertSound.CLICK)
        profiler.log(61, "Updated Gui")
        return nextState

    
    def waitingForTurn(self, frame:Frame, board: Board, recentCounts:BoardCountCache, profiler: Profiler):
        nextState = GameState.WAITING_FOR_TURN
        buttonPushed = board.processButtons(frame, profiler)
        success = self.gui.buttonPressed(buttonPushed)
        if success:
            nextState = GameState.PROCESS_TURN
            recentCounts.clear()
            self.playSound(AlertSound.BUTTON)
            self.processTurn(frame, board, recentCounts, profiler)
        
        return nextState

    
    def processTurn(self, frame:Frame, board: Board, recentCounts:BoardCountCache, profiler: Profiler):
        nextState = GameState.PROCESS_TURN
        
        boardCounts = board.detectPieces(frame, profiler, True)
        recentCounts.append(boardCounts)
        profiler.log(60, "Processed full board")
        sufficientSamples, appearedSquares, disappearedSquares = self.getBoardChanges(recentCounts)
        if (sufficientSamples):
            if (len(disappearedSquares) == 1 and len(appearedSquares) == 1):
                uciMove = chess.Move.from_uci(f'{chess.square_name(disappearedSquares[0])}{chess.square_name(appearedSquares[0][0])}')
                if (uciMove in self.game.legal_moves):
                    print(f'Adding move - {uciMove}')
                    self.game.push(uciMove)
                    threading.Thread(target=self.gui.updateChessBoard, args=(self.game.copy(),)).start()
                    self.playSound(AlertSound.RESOLVED)
                    nextState = GameState.WAITING_FOR_TURN
                else:
                    print(f'{uciMove} is an illegal move')
                    self.gui.undoButtonPress()
                    self.playSound(AlertSound.ERROR)
                    nextState = GameState.WAITING_FOR_TURN
            else:
                print(f'Error: {len(disappearedSquares)} have disappeared pieces and {len(appearedSquares)} have appeared pieces')
                self.gui.undoButtonPress()
                self.playSound(AlertSound.ERROR)
                nextState = GameState.WAITING_FOR_TURN
        profiler.log(61, "Updated Gui")
        return nextState


    def run(self):
        
        cap = Camera()
        fps = FPS(5).start()
        recentCounts = BoardCountCache()
        lastCalibratedBoard = None
        gameState = GameState.PREGAME
        while True:
            profiler = Profiler()
            if self.gui.restartGameFlag:
                gameState = GameState.PREGAME
                recentCounts.clear()
                self.gui.restartGameFlag = False
                self.game = chess.Board.empty()
            frame = cap.read()
            profiler.log(1, "Read the frame")
            board = Board(self.pieceSet, self.boardWidthInMm)
            board.calibrate(frame, lastCalibratedBoard, profiler,False)
            profiler.log(2, "Calibrated board")
            if board.calibrateSuccess:
                lastCalibratedBoard = board
                if gameState == GameState.PREGAME:
                    gameState = self.pregame(frame, board, recentCounts, profiler)
                elif gameState == GameState.WAITING_FOR_TURN:
                    gameState = self.waitingForTurn(frame, board, recentCounts, profiler)
                elif gameState == GameState.PROCESS_TURN:
                    gameState = self.processTurn(frame, board, recentCounts, profiler)
                board.drawOrigSquares(frame.img, recentCounts, self.pieceSet, True)
                profiler.log(4, "Drew squares")
            else:
                print ("Board uncalibrated")
                lastCalibratedBoard = None

            self.showImage(frame.img, fps, gameState)
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
    Runner(equipment.getCurrentSet(), equipment.getCurrentBoardWidthInMm()).run()