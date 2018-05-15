class Cell:
 
    def __init__(self, k, l):
        self.k = k;
        self.l = l;
 
    def compareTo(self, o):
        if(self.k == o.k and self.l == o.l):
            return 0
        return 1
     
    def toString(self):
        return str(self.k) + " " + str(self.l)