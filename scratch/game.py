
import chess
import chess.svg
from io import BytesIO
import numpy as np
from PIL import Image
import cv2
import tkinter

import chess.engine




class Game:
    def __init__(self):
        #self.turn = equipment.PieceColor.WHITE
        self.game = chess.Board.empty()
        self.game.clear()




if __name__ == "__main__":

    engine = chess.engine.SimpleEngine.popen_uci("./bin/stockfish_14_x64_avx2.exe")

    with engine.analysis(chess.Board("r1bqkbnr/p1pp1ppp/1pn5/4p3/2B1P3/5Q2/PPPP1PPP/RNB1K1NR w KQkq - 2 4"), multipv=3) as analysis:
    
        for info in analysis:
            print(info.get("score"), info.get("depth"), info.get("multipv"), )
            print(info.get("pv"))
            print("********************************")
            if info.get("depth", 0) > 20:
                break
        print("----------------------------------------------------")
    engine.quit()
    # board = chess.Board()
    # board.push_uci("e2e4")
    # board.push_uci("e7e5")
    # board.push_uci("d2d4")
    # moves = board.move_stack

    # temp = chess.Board()
    # for move in moves:
    #     print(temp.san(move))
    #     temp.push(move)
    # tcl = tkinter.Tcl()
    # print(tcl.call("info", "patchlevel"))

    # g = Game()
    # print(g.game.status())
    # #fen = '8/8/4B3/8/4P3/2P5/8/8 w - - 1 1'
    # #g.game.set_fen(fen)
    # #g.game.set_piece_at(chess.parse_square('e2'), chess.Piece.from_symbol('P'))
    # g.game.push_uci("e2e4")
    # g.game.push_uci("e7e5")
    # moves = g.game.move_stack
    # for move in moves:
    #     print(move)
    # x = g.game.legal_moves
    # print(x.count)
    # print(x[0])
    # for move in x:
    #     print (move)
    # i = chess.svg.board(g.game, squares=[chess.E2], arrows=[(chess.E5, chess.E5)], lastmove=g.game.peek())
    #print(i)
    
    #2.imwrite('cv.png', cv_img)


    