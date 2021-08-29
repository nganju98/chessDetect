
import equipment
import chess
import chess.svg
from io import BytesIO
import numpy as np
from PIL import Image
from cairosvg import svg2png
import cv2


class Game:
    def __init__(self):
        self.turn = equipment.PieceColor.WHITE
        self.game = chess.Board()
        self.game.clear()




if __name__ == "__main__":
    g = Game()
    g.game.set_piece_at(chess.parse_square('d2'), chess.Piece.from_symbol('K'))
    g.game.push_uci("d2d3")
    i = chess.svg.board(g.game)
    print(i)
    png = svg2png(bytestring=i)

    pil_img = Image.open(BytesIO(png)).convert('RGBA')
    
    cv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGBA2BGRA)

    cv2.imshow("chessboard", cv_img)
    cv2.waitKey(0)
    #2.imwrite('cv.png', cv_img)


    