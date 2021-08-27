from enum import Enum

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
    def __init__(self, markerId, type, color, diameterInMm, abbrev):
        self.markerId = markerId
        self.type = type
        self.color = color
        self.diameterInMm = diameterInMm
        self.abbrev = abbrev
        
        

SET1 = [
    Piece(10, PieceType.PAWN, PieceColor.WHITE, 30, 'P'),
    Piece(11, PieceType.BISHOP, PieceColor.WHITE, 36, 'B'),
    Piece(12, PieceType.KNIGHT, PieceColor.WHITE, 36, 'N'),
    Piece(13, PieceType.ROOK, PieceColor.WHITE, 35, 'R'),
    Piece(14, PieceType.QUEEN, PieceColor.WHITE, 38, 'Q'),
    Piece(15, PieceType.KING, PieceColor.WHITE, 41, 'K'),

    Piece(20, PieceType.PAWN, PieceColor.BLACK, 30, 'P'),
    Piece(21, PieceType.BISHOP, PieceColor.BLACK, 36, 'B'),
    Piece(22, PieceType.KNIGHT, PieceColor.BLACK, 36, 'N'),
    Piece(23, PieceType.ROOK, PieceColor.BLACK, 35, 'R'),
    Piece(24, PieceType.QUEEN, PieceColor.BLACK, 38, 'q'),
    Piece(25, PieceType.KING, PieceColor.BLACK, 41, 'K'),
]

SET1_DICT = {x.markerId: x for x in SET1}

def getCurrentSet():
    return SET1_DICT

def getCurrentBoardWidthInMm():
    return 450

print(PieceType(10) == PieceType.PAWN)
print(SET1_DICT[24].color == PieceColor.BLACK)