import math
import time

class Bar:
    
    def __init__(self,limit,text,initial = 0,increment = 1):
        self.limit = limit
        self.value = initial
        self.increment = 1
        self.points = []
        for i in range(0,min(self.limit,100)):
            self.points.append("░")
        self.current_point = 0
        self.starting_time = time.time()
        self.info = text
        self.update()

    def progress(self):
        self.value += self.increment
        percentage = (min(self.limit,100) * self.value)/self.limit
        point = percentage - self.current_point
        if point >= 1:
            self.points[self.current_point % min(self.limit,100)] = "█"
            self.current_point += 1
            self.update()

    def update(self):
        out = "{}".format("".join(self.points))
        rate = " {}/{} ".format(self.current_point,min(self.limit,100))
        elapsed = time.time() - self.starting_time
        elapsed = self.format_time(elapsed)
        elapsed = " [{}]".format(elapsed)
        print("\r{:<55} {}{}{}".format(self.info,out,rate,elapsed),end="")

    def format_time(self,time):
        hour = 0
        minute = 0
        seconds = 0
        if time > 3600:
            while time >= 3600:
                hour += 1
                time -= 3600
        if time > 60:
            while time >= 60:
                minute += 1
                time -= 60
        seconds = math.floor(time)
        hour = "0" + str(hour) if hour < 10 else hour
        minute = "0" + str(minute) if minute < 10 else minute
        seconds = "0" + str(seconds) if seconds < 10 else seconds
        return "{}:{}:{}".format(hour,minute,seconds)

    def finish(self):
        print()

