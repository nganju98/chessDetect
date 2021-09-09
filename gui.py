
import os
import ctypes.util
from tkinter.constants import N,S,E,W

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
import chess.svg
from cairosvg import svg2png
from io import BytesIO
from tkinter import Canvas, StringVar, Tk, ttk
import tkinter as tk
from engine import Engine
import time

class ChessClock():
    def __init__(self):
        self.started = False
        self.paused = False

    def setAttributes(self, timePerSide,increment):
        self.timePerSide = timePerSide
        self.increment = increment
    
    def blackButtonPressed(self):
        if (not self.started):
            self.started = True
            self.whiteRemaining = self.timePerSide
            self.blackRemaning = self.timePerSide
            self.whiteEndTime = self.whiteRemaining + time.time()
            self.turn = chess.WHITE
        else:
            if (self.turn == chess.BLACK):
                self.whiteEndTime = self.whiteRemaining + time.time()
                self.blackRemaning = (self.blackEndTime - time.time()) + self.increment
                self.turn = chess.WHITE
        
            

    def whiteButtonPressed(self):
        if (self.turn == chess.WHITE):
            self.blackEndTime = self.blackRemaning + time.time()
            self.whiteRemaining = (self.whiteEndTime - time.time()) + self.increment
            self.turn = chess.BLACK
        
    def getRemainingTimes(self):
        if (not self.started):
            return ChessClock.formatTime(self.timePerSide), ChessClock.formatTime(self.timePerSide)
        else:
            if (self.turn == chess.WHITE):
                whiteTime = self.whiteEndTime - time.time()
                blackTime = self.blackRemaning
            if (self.turn == chess.BLACK):
                whiteTime = self.whiteRemaining
                blackTime = self.blackEndTime - time.time()
            return ChessClock.formatTime(whiteTime), ChessClock.formatTime(blackTime)

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

    



class ChessGui:
    def __init__(self):
        pass

        
    def start(self):
        self.root = Tk()  
        style = ttk.Style(self.root)
        self.root.geometry("800x400")
        self.root.configure()
        self.root.rowconfigure(0, weight=0)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(2, weight=1)
        
        self.whiteRemaining = StringVar()
        self.whiteClock = ttk.Label(self.root, font=("Arial", 48), background="white", textvariable=self.whiteRemaining)
        self.whiteClock.grid(column=0, row=0, sticky=N, pady=10)
        self.whiteTurn = ttk.Button(self.root, text="White Finished", command=self.whiteButtonPressed)
        self.whiteTurn.grid(column=0, row=1, sticky=S, pady=10)
        
        self.blackRemaining = StringVar()
        self.blackClock = ttk.Label(self.root, font=("Arial", 48), background="white", textvariable=self.blackRemaining)   
        self.blackClock.grid(column=2, row=0, sticky=N, pady=10)
        self.blackTurn = ttk.Button(self.root, text="Black Finished", command=self.blackButtonPressed)
        self.blackTurn.grid(column=2, row=1, sticky=S, pady=10)
        

        self.canvas = Canvas(self.root, width = 300, height = 300)  
        self.canvas.grid(column=1,row=0, sticky=N, pady=10)
        #self.canvas.pack()  
        self.img = ImageTk.PhotoImage(Image.open("./assets/blank.png"))  
        self.imageContainer = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.img) 
        self.text = StringVar()
        self.text.set("Update Text")
        self.label= ttk.Label(self.root, font=("Arial"), textvariable=self.text)
        self.label.grid(row=1, column=1)
        self.clock = ChessClock()
        self.clock.setAttributes(300, 5)
        self.updateClock()
        self.root.mainloop()
        #pass #self.root.mainloop()

    # def doMainLoop(self):
        
    #     self.root.mainloop()
    def whiteButtonPressed(self):
        self.clock.whiteButtonPressed()
        self.blackClock.config(background="light yellow")
        self.whiteClock.config(background="white")

        
    def blackButtonPressed(self):
        self.clock.blackButtonPressed()
        self.whiteClock.config(background="light yellow")
        self.blackClock.config(background="white")

    def updateClock(self):
        white, black = self.clock.getRemainingTimes()
        self.whiteRemaining.set(white)
        self.blackRemaining.set(black)
        #self.whiteRemaining, self.blackRemaining = self.clock.getRemainingTimes()
        self.root.after(20, self.updateClock)


    def updateChessBoard(self, board : chess.Board):
        self.text.set("Scoring...")
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
        if board.is_valid():
            engine = Engine()
            score = engine.getScoreForPosition(board.fen())
            self.text.set(str(score))
        else:
            self.text.set("Invalid board")
        #profiler.log(53, "Made image")
  

if __name__ == "__main__":
    print(ChessClock.formatTime(300))
    print(ChessClock.formatTime(3725.5))
    print(ChessClock.formatTime(12.1))
    x = 23
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
    c.start()
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
  