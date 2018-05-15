class User:
    
    def __init__(self, id, x, y):
        self.id = id;       
        self.x = x;
        self.y = y;
 
    def compareTo(self, o):
        if(self.id == o.id and self.x == o.x and self.y == o.y):
            return 0
        else:
            return 1
     
    def toString(self):
        return str(self.id)