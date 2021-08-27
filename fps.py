import datetime

class FPS:
    def __init__(self, interval=1):
        self._start = None
        self.interval = interval
        self._numFrames = 0

    def start(self):
        self._start = datetime.datetime.now()
        self._numFrames = 0
        return self
        
    def updateAndPrint(self):
        self._numFrames += 1
        intervalElapsed = self.elapsed()
        if (intervalElapsed > self.interval):
            perf = self._numFrames / intervalElapsed
            print (f'FPS = {perf:.2f}, one frame = {int(1000 * intervalElapsed / self._numFrames)}ms')
            return True
        else:
            return False

    def checkFPS(self):
        return self._numFrames/self.elapsed()

    def updateAndPrintAndReset(self):
        if (self.updateAndPrint()):
            self.reset()
            return True
        else:
            return False
    
    def reset(self):
        self.start()

    def elapsed(self):
        el : datetime = (datetime.datetime.now() - self._start)
        return el.total_seconds()

