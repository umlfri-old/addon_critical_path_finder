inf = float('inf')

class Node(object):
        
    def __init__(self, ref):
        self.ref = ref
        self.prev = []
        self.next = []
        self.decprev = 0
        self.idx = -1
        self.time = [[-inf, -inf], [inf, inf]]
    
    def AddPrev(self, con, node):
        self.prev.append((con, node))
    
    def AddNext(self, con, node):
        self.next.append((con, node))
    
    def DecPrev(self):
        self.decprev += 1
    
    def SumPrev(self):
        return len(self.prev) - self.decprev
    
    def SetIdx(self, idx):
        self.idx = idx
    
    def NextHops(self):
        for con, node in self.next:
            yield node
    
    def SendNext(self):
        for c, n in self.next:
            n.RecvPrev(self.time[0][1])
    
    def RecvNext(self, time):
        if self.time[1][1] > time and time > -inf:
            self.time[1][1] = time
            self.time[1][0] = time - self.Duration()
    
    def SendPrev(self):
        for c, n in self.prev:
            n.RecvNext(self.time[1][0])
    
    def RecvPrev(self, time):
        if self.time[0][0] < time:
            self.time[0][0] = time
            self.time[0][1] = time + self.Duration()
        if self.time[0][0] > self.time[1][0]:
            self.time[1][0] = self.time[0][0]
            self.time[1][1] = self.time[0][1]
        
