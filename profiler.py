
from timeit import default_timer as timer


class ProfilerEntry:
    def __init__(self, id, message, timer):
        self.id = id
        self.message = message
        self.timer = timer

class Profiler:
    

    def __init__(self):
        self.entries = [ProfilerEntry(0, "start", timer())]

    def log(self, id, message):
        entry = ProfilerEntry(id, message, timer())
        self.entries.append(entry)

    def output(self):
        for i in range(0, len(self.entries)):
            elapsed = 0
            total = 0
            entry : ProfilerEntry = self.entries[i]
            if (i > 0):
                elapsed = (entry.timer - self.entries[i-1].timer) * 1000
                total =  (entry.timer - self.entries[0].timer) * 1000
            print(f'{entry.id}: e:{elapsed:.2f}ms t:{total:.2f}: {entry.message}')  
            


