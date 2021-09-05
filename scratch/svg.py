from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM
import chess
import chess.svg
from io import StringIO
g = chess.Board.empty()
print(g.status())
fen = '8/8/4B3/8/8/8/8/8 w - - 1 1'
g.set_fen(fen)
i = chess.svg.board(g)
text_file = open("svg2.txt", "w")
n = text_file.write(i)
text_file.close()
drawing = svg2rlg(StringIO(i))
renderPM.drawToFile(drawing, "temp2.png", fmt="PNG")
