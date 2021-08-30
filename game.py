
import equipment
import chess
import chess.svg
from io import BytesIO
import numpy as np
from PIL import Image
from cairosvg import svg2png
import cv2
import tkinter




class Game:
    def __init__(self):
        self.turn = equipment.PieceColor.WHITE
        self.game = chess.Board.empty()
        self.game.clear()




if __name__ == "__main__":

    tcl = tkinter.Tcl()
    print(tcl.call("info", "patchlevel"))

    g = Game()
    print(g.game.status())
    fen = '8/8/4B3/8/4P3/2P5/8/8 w - - 1 1'
    g.game.set_fen(fen)
    #g.game.set_piece_at(chess.parse_square('e2'), chess.Piece.from_symbol('P'))
    g.game.push_uci("e6h3")
    x = g.game.legal_moves
    print(x.count)
    print(x[0])
    for move in x:
        print (move)
    i = chess.svg.board(g.game, squares=[chess.E2], arrows=[(chess.E5, chess.E5)], lastmove=g.game.peek())
    #print(i)
    png = svg2png(bytestring=i)

    pil_img = Image.open(BytesIO(png)).convert('RGBA')
    
    cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGBA2BGRA)

    cv2.imshow("chessboard", cv_img)
    cv2.waitKey(0)
    #2.imwrite('cv.png', cv_img)


    