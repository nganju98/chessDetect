from tinydb import TinyDB, Query

class Persistence:

    CLOCK_TABLE = "clock"

    def __init__(self):
        self.db = TinyDB('db.json')

    def getClockParams(self):
        clocks = self.db.table(Persistence.CLOCK_TABLE).all()
        if (len(clocks) == 1):
            return clocks[0]["timePerSide"], clocks[0]["increment"]
        elif(len(clocks) == 0):
            return None
        else:
            raise RuntimeError("Shouldn't be more than one clock entry")

    def setClockParams(self, timePerSide, increment):
        self.db.table(Persistence.CLOCK_TABLE).truncate()
        self.db.table(Persistence.CLOCK_TABLE).insert({"timePerSide": timePerSide, "increment": increment})


if __name__ == "__main__":
    p = Persistence()
    p.setClockParams(15, 10)
    print(p.getClockParams())