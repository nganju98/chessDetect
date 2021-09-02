from enum import Enum

import chess
class Marker(Enum):
    BOARD_TOP_LEFT = 0
    BOARD_TOP_RIGHT = 1
    BOARD_BOTTOM_RIGHT = 2
    BOARD_BOTTOM_LEFT = 3
    WHITE_BUTTON = 4
    BLACK_BUTTON = 5
    WHITE_PAWN = 10
    WHITE_BISHOP = 11
    WHITE_KNIGHT = 12
    WHITE_ROOK = 13
    WHITE_QUEEN = 14
    WHITE_KING = 15
    BLACK_PAWN = 20
    BLACK_BISHOP = 21
    BLACK_KNIGHT = 22
    BLACK_ROOK = 23
    BLACK_QUEEN = 24
    BLACK_KING = 25


class PieceType(Enum) :
    PAWN = 10
    BISHOP = 11
    KNIGHT = 12
    ROOK = 13
    QUEEN = 14
    KING = 15


class PieceColor(Enum):
    WHITE = 0
    BLACK = 1




class Piece:
    def __init__(self, type : PieceType, color : PieceColor, diameterInMm):
        self.markerId = Marker[f'{color.name}_{type.name}'].value
        self.type = type
        self.color = color
        self.diameterInMm = diameterInMm
        if (type == PieceType.KNIGHT):
            self.abbrev = 'N'
        else:
            self.abbrev = self.type.name[0]
        if (color == PieceColor.BLACK):
            self.abbrev = self.abbrev.lower()
        self.chessPiece : chess.Piece = chess.Piece.from_symbol(self.abbrev)
        self.fullName = f'{self.color.name}_{self.type.name}'
        #print (self.abbrev)
        
        

SET1 = [
    Piece(PieceType.PAWN, PieceColor.WHITE, 30),
    Piece(PieceType.BISHOP, PieceColor.WHITE, 36),
    Piece(PieceType.KNIGHT, PieceColor.WHITE, 36),
    Piece(PieceType.ROOK, PieceColor.WHITE, 35),
    Piece(PieceType.QUEEN, PieceColor.WHITE, 38),
    Piece(PieceType.KING, PieceColor.WHITE, 41),

    Piece(PieceType.PAWN, PieceColor.BLACK, 30),
    Piece(PieceType.BISHOP, PieceColor.BLACK, 36),
    Piece(PieceType.KNIGHT, PieceColor.BLACK, 36),
    Piece(PieceType.ROOK, PieceColor.BLACK, 35),
    Piece(PieceType.QUEEN, PieceColor.BLACK, 38),
    Piece(PieceType.KING, PieceColor.BLACK, 41),
]

SET1_DICT = {x.markerId: x for x in SET1}



SET2 = [
    Piece(PieceType.PAWN, PieceColor.WHITE, 20),
    Piece(PieceType.BISHOP, PieceColor.WHITE, 23),
    Piece(PieceType.KNIGHT, PieceColor.WHITE, 23),
    Piece(PieceType.ROOK, PieceColor.WHITE, 23),
    Piece(PieceType.QUEEN, PieceColor.WHITE, 30),
    Piece(PieceType.KING, PieceColor.WHITE, 31),

    Piece(PieceType.PAWN, PieceColor.BLACK, 20),
    Piece(PieceType.BISHOP, PieceColor.BLACK, 23),
    Piece(PieceType.KNIGHT, PieceColor.BLACK, 23),
    Piece(PieceType.ROOK, PieceColor.BLACK, 23),
    Piece(PieceType.QUEEN, PieceColor.BLACK, 30),
    Piece(PieceType.KING, PieceColor.BLACK, 31),
]

SET2_DICT = {x.markerId: x for x in SET1}


def getCurrentSet():
    return SET2_DICT

def getCurrentBoardWidthInMm():
    return 450


if __name__ == "__main__":
    print(PieceType(10) == PieceType.PAWN)
    print(SET1_DICT[24].color == PieceColor.BLACK)
    print(SET1_DICT[24].chessPiece.symbol())
    print(SET1_DICT[24].fullName)