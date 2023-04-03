"""
Created in 2016

@author: Xingpeng Li (xplipower@gmail.com)

Website: https://rpglab.github.io/resources/RT-SCED_Python/
"""
# GeneralClasses

class Date:
    def __init__(self, month, day, year):
        self.month = month
        self.day = day
        self.year = year

class Time:
    def __init__(self, hour, minute, second):
        self.hour = hour
        self.minute = minute
        self.second = second
    
    # e.g. for a 5-minute interval, then 00:00:00 - 00:04:59 is the 0th period, for a day, it starts from 0 to 287.
    def getIdxPeriod(self, timeIntervalMinute):
        currentMinute = self.hour * 60 + self.minute
        import math
        return int(math.floor(currentMinute/timeIntervalMinute))

def isSameDate(date1, date2):
    if date1.month != date2.month:
        return False
    if date1.day != date2.day:
        return False
    if date1.year != date2.year:
        return False
    return True

# return how many hours away between two times
def calcDiffHours(date1, hr1, date2, hr2):
    diffHr = (date1.year - date2.year)*365*24  # TODO: a year may have 366 days, however, for this sced tool, that case may never occur.
    diffHr = diffHr + (date1.month - date2.month)*30*24 # TODO: THIS IS JUST a roughly estimation. Again, for this sced tool, it is good enough.
    diffHr = diffHr + (date1.day - date2.day)*24
    diffHr = diffHr + hr1 - hr2
    return abs(diffHr)
