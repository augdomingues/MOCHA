"""
    This class prints a visual guidance of the progress of a task
"""
import math
import time


class Bar:
    """
        This class prints a visual guidance of the progress of a task
    """
    def __init__(self, limit, text, initial=0, increment=1):
        """ Creates the bar, and shows it. """
        self.limit = limit
        self.value = initial
        self.increment = increment
        self.points = []
        for _ in range(0, min(int(self.limit), 100)):
            self.points.append("░")
        self.current_point = 0
        self.starting_time = time.time()
        self.info = text
        self.update()

    def progress(self):
        """ Progress the bar by the increment defined. """
        self.value += self.increment
        percentage = (min(self.limit, 100) * self.value)/self.limit
        point = percentage - self.current_point
        if point >= 1:
            self.points[self.current_point % min(self.limit, 100)] = "█"
            self.current_point += 1
            self.update()

    def update(self):
        """ Visually updates the bar. """
        out = "{}".format("".join(self.points))
        rate = " {}/{} ".format(self.current_point, min(self.limit, 100))
        elapsed = time.time() - self.starting_time
        elapsed = self.format_time(elapsed)
        elapsed = " [{}]".format(elapsed)
        print("\r{:<25} {}{}{}".format(self.info, out, rate, elapsed), end="")

    def format_time(self, timestamp):
        """ Format the time from timestamp to hh:mm:ss. """
        hour = 0
        minute = 0
        seconds = 0
        if timestamp > 3600:
            while timestamp >= 3600:
                hour += 1
                timestamp -= 3600
        if timestamp > 60:
            while timestamp >= 60:
                minute += 1
                timestamp -= 60
        seconds = math.floor(timestamp)
        hour = "0" + str(hour) if hour < 10 else hour
        minute = "0" + str(minute) if minute < 10 else minute
        seconds = "0" + str(seconds) if seconds < 10 else seconds
        return "{}:{}:{}".format(hour, minute, seconds)

    def finish(self):
        """ Outputs a clear line. """
        print()
