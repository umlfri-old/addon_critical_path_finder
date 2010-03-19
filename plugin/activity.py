from node import Node
inf = float('inf')

class Activity(Node):
    
    def __init__(self, ref):
        Node.__init__(self, ref)
        self.duration = float(ref.GetObject().GetValue('duration'))
    
    def Duration(self):
        return self.duration
    
    def IsCritical(self):
        return self.time[0][1] == self.time[1][1] > -inf
    
