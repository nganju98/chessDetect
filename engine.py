from stockfish import Stockfish
import os
class Engine:

    def __init__(self):
        if os.name == 'nt':
            self.stockfish = Stockfish("./bin/stockfish_14_x64_avx2.exe", 12)
        else:
            self.stockfish=Stockfish('./bin/stockfish_14_x64_avx2', 12)

    def getScoreForPosition(self, fen:str):
        self.stockfish.set_fen_position(fen)
        #print("Starting eval")
        eval = self.stockfish.get_evaluation()
        print(f'STOCKFISH EVAL: {eval}')
        return eval["value"]







if __name__ == "__main__":
    e = Engine()
    e.setFenPosition("rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")
    

