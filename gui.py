
import os
import ctypes.util
from profiler import Profiler
import threading
import time
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
    dllPath = f'{os.path.dirname(os.path.realpath(__file__))}\\cairo_dlls'
    print("Dll path: " + dllPath)
    os.environ['path'] += ";" + dllPath
    set_dll_search_path()
    path = ctypes.util.find_library('libcairo-2')
    print("Found libcairo at: " + path)
    print ("Total system path = " + os.environ['path'])


from tkinter import *  
from PIL import ImageTk,Image  
import chess
import chess.svg
from cairosvg import svg2png
from io import BytesIO
import cv2
import numpy as np
from tkinter import ttk

class ChessGui:
    def __init__(self):
        pass

        
    def start(self):
        self.root = Tk()  
        self.canvas = Canvas(self.root, width = 300, height = 300)  
        self.canvas.pack()  
        self.img = ImageTk.PhotoImage(Image.open("./assets/blank.png"))  
        self.imageContainer = self.canvas.create_image(0, 0, anchor=NW, image=self.img) 
        self.text = StringVar()
        self.text.set("Update Text")
        self.button= ttk.Button(self.root, textvariable=self.text,command=lambda:self.updateChessBoard())
        self.button.pack()
        self.root.mainloop()
        #pass #self.root.mainloop()

    # def doMainLoop(self):
        
    #     self.root.mainloop()

    def updateChessBoard(self, svgImage, profiler):
        
        #i = chess.svg.board(self.game, squares=[chess.E2], arrows=[(chess.E5, chess.E5)], lastmove=lastmove)
        # profiler.log(52, "Generated SVG")
        # #print(i)
        png = svg2png(bytestring=svgImage, output_width=300)
        # profiler.log(52, "Made png from svg")
        
        pil_img = Image.open(BytesIO(png))

        
        # cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGBA2BGRA)
        #cv2.imwrite("board.png", cv_img)
        self.text.set("Updagte 2")
        #ImageTk.PhotoImage(Image.open("board.png"))  
        self.img = ImageTk.PhotoImage(pil_img)  
        #self.canvas.photo = img
        self.canvas.itemconfig(self.imageContainer, image=self.img)
        
        #self.canvas.pack()
        #profiler.log(53, "Made image")
  

if __name__ == "__main__":
    
    # c = ChessGui()
    # threading.Thread(target=c.start, args=()).start()
    # time.sleep(2)
    
    board = chess.Board().empty()
    svg = chess.svg.board(board)
    png = svg2png(bytestring=svg, output_width=300)
    pil_img = Image.open(BytesIO(png))

        
    cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGBA2BGRA)
    cv2.imwrite("blank.png", cv_img)
    #board.set_piece_at(chess.A1, chess.Piece.from_symbol('q'))
    

    c.updateChessBoard(svg, Profiler())
  