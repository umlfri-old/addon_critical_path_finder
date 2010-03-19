from node import Node
inf = float('inf')

class Condition(Node):
    
    def __init__(self, ref):
        Node.__init__(self, ref)
        self.name = ref.GetObject().GetValue('condition')
        self.neg = ref.GetObject().GetValue('negate') == 'True'
    
    def SetConditions(self, cond):
        self.val = cond[self.name] ^ self.neg
    
    def Duration(self):
        if self.val:
            return 0
        else:
            return -inf
    
    def IsCritical(self):
        return self.time[0][1] == self.time[1][1] > -inf and self.val
