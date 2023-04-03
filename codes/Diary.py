"""
Created in 2016

@author: Xingpeng Li (xplipower@gmail.com)

Website: https://rpglab.github.io/resources/RT-SCED_Python/

Example:

import Diary
logger = Diary.Diary()
logger.hotline("tets l;")
logger.hotline("tets 2;")
logger.close()

"""


import time

class Diary:
    'Diary or Log for information records'
    def __init__(self):
        self.start_time = time.time()
        timeMark = str(time.ctime(time.time()))
        fileName = timeMark[4:].replace(' ', '_').replace(':', '_')
#        self.logger = open('log\Log_'+fileName+'.txt', 'w')
        self.logger = open('Log_'+fileName+'.txt', 'w')
        heading = 'LogItem 1 , t=' +  Diary.getElapsedTime(self) + 's , ' \
                    + Diary.getLogType(self, 3) + ' , '
        self.logger.write(heading + 'this log file was created @ ' + timeMark + "\n")
        self.logger.flush()
        self.count = 1
    
    def hotline(self, message):
        Diary.hotlineWithLogType(self, 0, message)
        
    def hotlineWithLogType(self, mType, message):
        self.count += 1
        heading = "LogItem " + str(self.count) + ' , t=' + Diary.getElapsedTime(self) + 's , ' \
                    + Diary.getLogType(self, mType) + ' , '
        self.logger.write(heading + message + '\n')
        self.logger.flush()
    
    def close(self):
        self.count += 1
        timeMark = str(time.ctime(time.time()))
        heading = "LogItem " + str(self.count) + ' , t=' + Diary.getElapsedTime(self) + 's , ' \
                    + Diary.getLogType(self, 4) + ' , '
        self.logger.write(heading + 'this log file was finished @ ' + timeMark + '\n')
        self.logger.flush()
        self.logger.close()

    def getElapsedTime(self):
        elapsed_time = time.time() - self.start_time
        return format(elapsed_time, '.2f')

    def getLogType(self, num):
        if num == 0:
            return 'Normal'
        elif num == 1:
            return 'Warning'
        elif num == 2:
            return 'Error'
        elif num == 3:
            return 'Start'
        elif num == 4:
            return 'End'
        elif num == 5:
            return 'Milestone'
        elif num == 6:
            return 'Summary'
        elif num == 7:
            return 'Notice'
        else:
            return 'Unknown'


