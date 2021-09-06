from stockfish import Stockfish

class Engine:

    def __init__(self):
        self.stockfish = Stockfish("./bin/stockfish_14_x64_avx2.exe", 20)

    def setFenPosition(self, fen:str):
        self.stockfish.set_fen_position(fen)
        print("Starting eval")
        eval = self.stockfish.get_evaluation()
        print(f'STOCKFISH EVAL: {eval}')








if __name__ == "__main__":
    e = Engine()
    e.setFenPosition("rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")
    

