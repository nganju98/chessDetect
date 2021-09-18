
from functools import partial
from board import Board
import os
import ctypes.util
from tkinter.constants import ANCHOR, N, NSEW,S,E,W
from camera import Camera
import datetime
def set_dll_search_path():
   # Python 3.8 no longer searches for DLLs in PATH, so we have to add
   # everything in PATH manually. Note that unlike PATH add_dll_directory
   # has no defined order, so if there are two cairo DLLs in PATH we
   # might get a random one.
   if os.name != "nt" or not hasattr(os, "add_dll_directory"):
       return
   for p in os.environ.get("PATH", "").split(os.pathsep):
       try:
           os.add_dll_directory(p)
       except OSError:
           pass

print("Running on os: " + os.name)
if os.name == 'nt':
    dllPath = f'{os.path.dirname(os.path.realpath(__file__))}\\bin'
    print("Dll path: " + dllPath)
    os.environ['path'] += ";" + dllPath
    set_dll_search_path()
    path = ctypes.util.find_library('libcairo-2')
    print("Found libcairo at: " + path)
    print ("Total system path = " + os.environ['path'])


from profiler import Profiler

from PIL import ImageTk,Image  
import chess
import chess.engine
import chess.svg
from cairosvg import svg2png
from io import BytesIO
from tkinter import Canvas, StringVar, Tk, ttk
import tkinter as tk
from engine import Engine
import time
from equipment import Marker
from collections import deque
from typing import Deque
class ChessClock():

    def __init__(self):
        self.started = False
        self.paused = False
        self.canUndo = False

    def setAttributes(self, timePerSide,increment):
        self.timePerSide = timePerSide
        self.increment = increment
    
    def blackButtonPressed(self) -> bool:
        if (not self.started):
            self.started = True
            self.whiteRemaining = self.timePerSide
            self.blackRemaning = self.timePerSide
            self.whiteEndTime = self.whiteRemaining + time.time()
            self.turn = chess.WHITE
            self.canUndo = False
            return True
        else:
            finished = self.gameFinished()
            if (self.turn == chess.BLACK and not finished and not self.paused):
                self.whiteEndTime = self.whiteRemaining + time.time()
                self.blackRemaning = (self.blackEndTime - time.time()) + self.increment
                self.turn = chess.WHITE
                self.canUndo = True
                return True
            elif finished:
                return False
            elif self.turn == chess.WHITE:
                return False
            elif self.paused:
                return False
            raise RuntimeError("Shouldnt have arrived at this point")

    def whiteButtonPressed(self) -> bool:
        finished = self.gameFinished()
        if (self.started and self.turn == chess.WHITE and not finished and not self.paused):
            self.blackEndTime = self.blackRemaning + time.time()
            self.whiteRemaining = (self.whiteEndTime - time.time()) + self.increment
            self.turn = chess.BLACK
            self.canUndo = True
            return True
        elif not self.started:
            return False
        elif finished:
            return False
        elif self.turn == chess.BLACK:
            return False
        elif self.paused:
            return False
        raise RuntimeError("Shouldnt have arrived at this point")
    
    def undoButtonPress(self) -> bool:
        if (self.canUndo):
            if (self.turn == chess.WHITE):
                self.turn = chess.BLACK
                self.blackEndTime = (self.blackRemaning - self.increment)  + time.time()

            elif (self.turn == chess.BLACK):
                self.turn = chess.WHITE
                self.whiteEndTime = (self.whiteRemaining - self.increment) + time.time()

            self.canUndo = False
            return True
        else:
            print("Cant undo")
            return False
            

    
    def pause(self) -> bool:
        if self.started and not self.gameFinished() and not self.paused:
            if (self.turn == chess.WHITE):
                self.whiteRemaining = self.whiteEndTime - time.time()
            elif (self.turn == chess.BLACK):
                self.blackRemaning = self.blackEndTime - time.time()
            self.paused = True
            return True
        else:
            return False
    
    def unpause(self) -> bool:
        if self.started and not self.gameFinished() and self.paused:
            self.paused = False
            if self.turn == chess.BLACK:
                self.blackEndTime = self.blackRemaning + time.time()
            elif self.turn == chess.WHITE:
                self.whiteEndTime = self.whiteRemaining + time.time()
            return True
        else:
            return False


    def getRemainingTimes(self):
        if (not self.started):
            return ChessClock.formatTime(self.timePerSide), ChessClock.formatTime(self.timePerSide)
        else:
            if (self.paused):
                blackTime = self.blackRemaning
                whiteTime = self.whiteRemaining
            elif (self.turn == chess.WHITE):
                whiteTime = self.whiteEndTime - time.time()
                blackTime = self.blackRemaning
            elif (self.turn == chess.BLACK):
                whiteTime = self.whiteRemaining
                blackTime = self.blackEndTime - time.time()

            if (whiteTime <= 0):
                whiteTime = 0
            if (blackTime <= 0):
                blackTime = 0
            return ChessClock.formatTime(whiteTime), ChessClock.formatTime(blackTime)
    
    def whiteFinished(self) -> bool:
        if (self.started and not self.paused):
            if self.turn == chess.WHITE:
                whiteTime = self.whiteEndTime - time.time()
                return (whiteTime <= 0)
            elif self.turn == chess.BLACK:
                return self.whiteRemaining <= 0
        else:
            return False
    
    def blackFinished(self) -> bool:
        if (self.started and not self.paused):
            if (self.turn == chess.BLACK):
                blackTime = self.blackEndTime - time.time()
                return (blackTime < 0)
            elif (self.turn == chess.WHITE):
                return self.blackRemaning <= 0 
        else:
            return False

    def gameFinished(self) -> bool:
        return self.whiteFinished() or self.blackFinished()

    def formatTime(time : float):
        retval = "NOTHING"
        hours = int(time / 3600)
        minutes = int((time % 3600) / 60)
        seconds = int(time) % 60
        tenths = int(time * 10) % 10
        
        if hours > 0:
            retval = f'{hours:01}' + ':' + f'{minutes:02}' + ':' + f'{seconds:02}'
        elif minutes > 0:
            retval = f'{minutes:02}' + ':' + f'{seconds:02}'
        else:
           retval=f'{minutes:02}' + ':' + f'{seconds:02}' + '.' + f'{tenths:01}'

        return retval

    
class Variant():
    def __init__(self, score, depth, pvNum, moves, board : Board):
        self.score = score
        self.depth = depth
        self.pvNum = pvNum
        self.moves = moves
        self.board = board
#self.score.relative.cp/100
    def toString(self):
        if (self.score.is_mate()):
            score = f'M{self.score.relative.moves}'
        else:
            score = f'{self.score.relative.cp/100:+}'
        retval = f'L{self.pvNum}({self.depth}): {score} {ChessGui.generateForward(self.board, self.moves)}'
        return retval


class ChessGui:
    def __init__(self):
        self.cameras = [] # Camera.listPorts()
        
        
    def start(self, showDebugButtons = False):

        self.restartGameFlag = False
        self.changeCameraFlag = -1
        self.doLayout(showDebugButtons)
        self.clock = ChessClock()
        self.clock.setAttributes(5400, 5)
        self.updateClock()
        self.root.mainloop()
        #pass #self.root.mainloop()

    # def doMainLoop(self):
        
    #     self.root.mainloop()

    def doLayout(self, showDebugButtons):
        
        self.root = Tk()  
        style = ttk.Style(self.root)
        self.root.geometry("800x400")
        self.root.configure()
        
        self.whiteRemaining = StringVar()
        self.whiteClock = ttk.Label(self.root, font=("Arial", 36), background="white", textvariable=self.whiteRemaining)
        self.whiteClock.grid(column=0, row=0, sticky=E, pady=2)
        
        
        self.blackRemaining = StringVar()
        self.blackClock = ttk.Label(self.root, font=("Arial", 36), background="white", textvariable=self.blackRemaining)   
        self.blackClock.grid(column=2, row=0, sticky=W, pady=2)
        
        if (showDebugButtons):
            self.whiteTurn = ttk.Button(self.root, text="White Finished", command=self.whiteButtonPressed)
            self.whiteTurn.grid(column=0, row=10, sticky=N, pady=10)
            self.blackTurn = ttk.Button(self.root, text="Black Finished", command=self.blackButtonPressed)
            self.blackTurn.grid(column=3, row=10, sticky=NSEW, pady=10)
            self.undoButton = ttk.Button(self.root, text="Undo", command=self.undoButtonPress)
            self.undoButton.grid(column=1, row=10, sticky=S, pady=10)

        # self.pauseButton = ttk.Button(self.root, text="Pause", command=self.togglePause)
        # self.pauseButton.grid(column=1, row=2, sticky=S, pady=10)
        
        self.historyFrame = ttk.LabelFrame(self.root, text="Turn history")
        self.historyFrame.grid(column=0, row=1, rowspan=1, sticky=NSEW)
        self.historyString=StringVar()
        self.history = ttk.Label(self.historyFrame, textvariable=self.historyString)
        self.history.grid(column=0, row=0)
        

        self.engineFrame = ttk.LabelFrame(self.root, text="Engine Analysis")
        self.engineFrame.grid(column=2, row=1, rowspan=1, sticky=NSEW)
        self.engineString=StringVar()
        self.engineLabel = ttk.Label(self.engineFrame, textvariable=self.engineString, wraplength=270)
        self.engineLabel.grid(column=0, row=0)
        

        self.canvas = Canvas(self.root, width = 300, height = 300)  
        self.canvas.grid(column=1,row=0, rowspan=2, columnspan=1, sticky=NSEW, pady=2, padx=2)
        #self.canvas.pack()  
        self.imageContainer = self.canvas.create_image(0, 0, anchor=tk.NW) 
        self.updateChessBoard(chess.Board.empty())
        #self.img = ImageTk.PhotoImage(Image.open("./assets/blank.png"))  
        

        menubar = tk.Menu(self.root)
        self.gameMenu = tk.Menu(menubar, tearoff=0)
        self.gameMenu.add_command(label="New Game", command=self.restartGame)
        self.gameMenu.add_command(label="Pause", command=self.togglePause)
        menubar.add_cascade(label="Game", menu=self.gameMenu)

        self.cameraMenu = tk.Menu(menubar, tearoff=0)
        
        for camera in self.cameras:
            handler = partial(self.changeCamera, camera.port)
            self.cameraMenu.add_command(label=camera.description(), command=handler)
        
        menubar.add_cascade(label="Camera", menu=self.cameraMenu)

        self.root.config(menu=menubar)

        
        
        # self.root.rowconfigure(2, weight=3)
        self.root.rowconfigure(1, weight=3)
        self.root.columnconfigure(0, weight=3)
        self.root.columnconfigure(2, weight=3)

    def changeCamera(self, port):
        print(f'changing camera to: {port}')
        self.changeCameraFlag = port

    def restartGame(self):
        self.restartGameFlag = True
        print("setting restartGame to true")
        self.clock = ChessClock()
        self.clock.setAttributes(300, 5)
        self.updateClock()
        self.whiteClock.config(background="white")
        self.blackClock.config(background="white")

    def whiteButtonPressed(self):
        success = self.clock.whiteButtonPressed()
        if success:
            self.blackClock.config(background="light yellow")
            self.whiteClock.config(background="white")
        return success

    def togglePause(self):
        if self.clock.paused:
            success = self.clock.unpause()
            if success:
                self.pauseButton.configure(text="Pause")
                self.gameMenu.entryconfigure(1, label="Pause")
        elif not self.clock.paused:
            success = self.clock.pause()
            if success:
                self.pauseButton.configure(text="Unpause")
                self.gameMenu.entryconfigure(1, label="Unpause")
        
    def blackButtonPressed(self):
        success = self.clock.blackButtonPressed()
        if success:
            self.whiteClock.config(background="light yellow")
            self.blackClock.config(background="white")
        return success

        
    def undoButtonPress(self):
        success = self.clock.undoButtonPress()
        if success:
            if self.clock.turn == chess.WHITE:
                self.whiteClock.config(background="light yellow")
                self.blackClock.config(background="white")
            elif self.clock.turn == chess.BLACK:
                self.blackClock.config(background="light yellow")
                self.whiteClock.config(background="white")
        return success

    def buttonPressed(self, button : Marker):
        if button == Marker.WHITE_BUTTON:
            return self.whiteButtonPressed()
        elif button == Marker.BLACK_BUTTON:
            return self.blackButtonPressed()
        else:
            return False

    def updateClock(self):
        white, black = self.clock.getRemainingTimes()
        self.whiteRemaining.set(white)
        self.blackRemaining.set(black)
        if (self.clock.whiteFinished()):
            self.whiteClock.config(background="red")
        if (self.clock.blackFinished()):
            self.blackClock.config(background="red")
        #self.whiteRemaining, self.blackRemaining = self.clock.getRemainingTimes()
        self.root.after(20, self.updateClock)

    def updateChessBoard(self, board : chess.Board):
        #self.text.set("Scoring...")
        self.lastUpdated = datetime.datetime.now()
        localUpdated = self.lastUpdated
        lastmove = None
        if len(board.move_stack) > 0:
            lastmove = board.peek()
        svgImage = chess.svg.board(board, lastmove=lastmove)
        # profiler.log(52, "Generated SVG")
        png = svg2png(bytestring=svgImage, output_width=300)
        # profiler.log(52, "Made png from svg")
        
        pil_img = Image.open(BytesIO(png))

        
        self.img = ImageTk.PhotoImage(pil_img)  
        self.canvas.itemconfig(self.imageContainer, image=self.img)
        self.historyString.set(ChessGui.generateHistory(board))
        exe = "./bin/stockfish_14_x64_avx2.exe"
        if os.name != 'nt':
            exe = './bin/stockfish_14_x64_avx2'
        engine = chess.engine.SimpleEngine.popen_uci(exe)
        if (localUpdated == self.lastUpdated and board.is_valid()):
            print(f'Starting engine on {board.fen()}')
            with engine.analysis(board, multipv=3) as analysis:
                pvs = {}
                for info in analysis:
                    if info.get("multipv") is not None:
                        pvs[info.get("multipv")] = Variant(info.get("score"), info.get("depth"), info.get("multipv"), info.get("pv"), board)
                        analysis = ""
                        for key in sorted(pvs.keys()):
                            analysis += pvs[key].toString() + "\n"
                        self.engineString.set(analysis)
                    #print(info.get("score"), info.get("depth"), info.get("multipv"))
                    
                    #print(info.get("pv"))
                    #print("********************************")
                    if info.get("depth", 0) > 20:
                        print(f'Stopping for {board.fen()}, max depth reached')
                        break
                    if localUpdated != self.lastUpdated:
                        print(f'Stopping for {board.fen()}, board was updated')
                        break
                #print("----------------------------------------------------")
            engine.quit()

        #profiler.log(53, "Made image")
    
    def generateHistory(board:Board):
        
        moves = board.move_stack

        temp = chess.Board()
        retval = ""
        for ctr, move in enumerate(moves):
            if ctr % 2 == 0:
                retval += f'{int(ctr/2) + 1}. {temp.san(move)}  '
            else:
                retval += f'{temp.san(move)} \n'
            #print(temp.san(move))
            temp.push(move)
        return retval

    def generateForward(board:chess.Board, moves):
        
        temp = board.copy()
        retval = ""
        history = len(board.move_stack)
        first = True
        for ctr, move in enumerate(moves):
            moveCtr = ctr + history
            if moveCtr % 2 == 0:
                retval += f'{int(moveCtr/2) + 1}.{temp.san(move)}  '
                first = False
            else:
                if first:
                    retval += f'{int(moveCtr/2) + 1}...'
                    first = False
                retval += f'{temp.san(move)} '
            #print(temp.san(move))
            temp.push(move)
        return retval

if __name__ == "__main__":
    pass
    # board = chess.Board()
    # board.push_uci("e2e4")
    # board.push_uci("e7e5")
    # board.push_uci("d2d4")
    # print(ChessGui.generateHistory(board))
    # print(ChessClock.formatTime(300))
    # print(ChessClock.formatTime(3725.5))
    # print(ChessClock.formatTime(12.1))
    # x = 23
    # clock = ChessClock()
    # clock.setAttributes(300, 5)

    # print(clock.getRemainingTimes())

    # clock.blackButtonPressed()
    # time.sleep(2)
    # print(clock.getRemainingTimes())
    # clock.whiteButtonPressed()
    
    # time.sleep(3)
    # print(clock.getRemainingTimes())
    
    # time.sleep(3)
    # print(clock.getRemainingTimes())
    c = ChessGui()
    c.start(False)
    # threading.Thread(target=c.start, args=()).start()
    # time.sleep(2)
    
    # board = chess.Board().empty()
    # svg = chess.svg.board(board)
    # png = svg2png(bytestring=svg, output_width=300)
    # pil_img = Image.open(BytesIO(png))

        
    #cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGBA2BGRA)
    #cv2.imwrite("blank.png", cv_img)
    #board.set_piece_at(chess.A1, chess.Piece.from_symbol('q'))
    

    #c.updateChessBoard(svg, Profiler())
  