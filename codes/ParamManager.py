"""
Created in 2016

# Author: Xingpeng Li
# Email: xplipower@gmail.com 

Website: https://rpglab.github.io/resources/RT-SCED_Python/
"""

import os

class ParamManager:

    def __init__(self, configFilePath, myDiary):
        self.solverName = "glpk"
        self.solverTimLimit = 300   # in second
        self.solverOptGap = 0.01
        
        self.pathRealCase = os.getcwd() + "/real_case/"
        self.pyomoDataFormatInputFileRC = 'pyomoDataForSmallRealCase.dat'   
        
        self.pathGenericCase = os.getcwd() + "/generic_case/"
        self.pyomoDataFormatInputFileGC = 'pyomoDataForGenericCaseModel.dat'   

        self.isPositivePgPmaxPminNeeded = False
        
        # parse the configure file
        with open(configFilePath, 'r') as configFile:
            for line in configFile:
                line = line.strip()
                if not line:
                    continue
                if ParamManager.isCommentLine(self, line) == True:
                    continue
                line = ParamManager.removeCommentString(self, line)
                tokens = ParamManager.getTwoTokens(self, line)
                key = tokens[0]
                value = tokens[1]
                if key == 'isRunSCED':
                    if value.lower() == 'true':
                        self.isRunSCED = True
                    else:
                        self.isRunSCED = False
                elif key == 'isPyomoDataFilesAvailable':
                    if value.lower() == 'true':
                        self.isPyomoDataFilesAvailable = True
                    else:
                        self.isPyomoDataFilesAvailable = False
                elif key == 'generatePyomoDataFiles':
                    if value.lower() == 'true':
                        self.generatePyomoDataFiles = True
                    else:
                        self.generatePyomoDataFiles = False
                elif key == 'needHeading':
                    if value.lower() == 'true':
                        self.needHeading = True
                    else:
                        self.needHeading = False
                elif key == 'isPositivePgPmaxPminNeeded':
                    if value.lower() == 'true':
                        self.isPositivePgPmaxPminNeeded = True
                    else:
                        self.isPositivePgPmaxPminNeeded = False
                elif key == 'handle_CostCurveSegment_Pgmin':
                    if value.lower() == 'true':
                        self.handle_CostCurveSegment_Pgmin = True
                    else:
                        self.handle_CostCurveSegment_Pgmin = False
                elif key == 'solverName':
                    self.solverName = value.lower()
                elif key == 'solverTimLimit':
                    self.solverTimLimit = value
                elif key == 'solverOptGap':
                    self.solverOptGap = value
                elif key == 'pathRealCase':
                    if value.endswith("/") == False:
                        if value.endswith("\\") == False:
                            value = value + "/"
                    self.pathRealCase = value
                elif key == 'bidFileNameRC':
                    self.bidFileNameRC = value
                elif key == 'costCurveRampFileNameRC':
                    self.costCurveRampFileNameRC = value
                elif key == 'hourlyDataFileNameRC':
                    self.hourlyDataFileNameRC = value
                elif key == 'interfaceFileNameRC':
                    self.interfaceFileNameRC = value
                elif key == 'reserveReqFileNameRC':
                    self.reserveReqFileNameRC = value
                elif key == 'aolFileNameRC':
                    self.aolFileNameRC = value
                elif key == 'rawFileNameRC':
                    self.rawFileNameRC = value
                elif key == 'rtUnitStatusFileNameRC':
                    self.rtUnitStatusFileNameRC = value
                elif key == 'unitFileNameRC':
                    self.unitFileNameRC = value
                elif key == 'pathGenericCase':
                    if value.endswith("/") == False:
                        if value.endswith("\\") == False:
                            value = value + "/"
                    self.pathGenericCase = value
                elif key == 'rawFileNameGC':
                    self.rawFileNameGC = value
                elif key == 'costCurveOutputFileNameGC':
                    self.costCurveOutputFileNameGC = value
                elif key == 'costCurveMultiRampFileNameGC':
                    self.costCurveMultiRampFileNameGC = value
                elif key == 'costCurveSpinRampFileNameGC':
                    self.costCurveSpinRampFileNameGC = value
                elif key == 'Year':
                    self.year = int(value)
                elif key == 'Month':
                    self.month = int(value)
                elif key == 'Day':
                    self.day = int(value)
                elif key == 'Hour':
                    self.hour = int(value)
                elif key == 'Minute':
                    self.minute = int(value)
                elif key == 'Second':
                    self.second = int(value)
                elif key == 'runSCEDTimeFrame':
                    self.runSCEDTimeFrame = float(value)
                elif key == 'blockPrice':
                    self.blockPrice = float(value)
                elif key == 'pyomoDataFormatInputFileRC':
                    self.pyomoDataFormatInputFileRC = value
                elif key == 'pyomoDataFormatInputFileGC':
                    self.pyomoDataFormatInputFileGC = value
                else:
                    myDiary.hotlineWithLogType(1, "key: "+key+" cannot be parsed")
        import GeneralClasses
        self.date = GeneralClasses.Date(self.month, self.day, self.year)
        self.time = GeneralClasses.Time(self.hour, self.minute, self.second)
        myDiary.hotlineWithLogType(5, "Configure file has been parsed")
        
    def isCommentLine(self, line):
        if line[0] == '#':
            return True
        elif line[:2] == "//":
            return True
        else:
            return False
        
    def removeCommentString(self, line):
        idx = line.find('#')
        if idx != -1:
            line = line[:idx]
        idx = line.find('#')
        if idx != -1:
            line = line[:idx]
        return line

    def getTwoTokens(self, line):
        idx = line.find('=')
        key = line[:idx].strip()
        value = line[(idx+1):].strip()
        return [key, value]

    def getIsRunSCED(self):
        return self.isRunSCED
    def getIsPyomoDataFilesAvailable(self):
        return self.isPyomoDataFilesAvailable
    def getGeneratePyomoDataFiles(self):
        return self.generatePyomoDataFiles
    def getNeedHeading(self):
        return self.needHeading
    def getIsPositivePgPmaxPminNeeded(self):
        return self.isPositivePgPmaxPminNeeded
    def getHandle_CostCurveSegment_Pgmin(self):
        return self.handle_CostCurveSegment_Pgmin
        
    def getBlockPrice(self):
        return self.blockPrice
    def getPyomoDataFormatInputFileRC(self):
        return self.pyomoDataFormatInputFileRC
    def getPyomoDataFormatInputFileGC(self):
        return self.pyomoDataFormatInputFileGC

    def getSolverName(self):
        return self.solverName
    def getSolverTimLimit(self):
        return self.solverTimLimit
    def getSolverOptGap(self):
        return self.solverOptGap
    
    #------ date and time
    def getDate(self):
        return self.date
    def getTime(self):
        return self.time
    # e.g. for a 5-minute interval, then 00:00:00 - 00:04:59 is the 0th period, for a day, it starts from 0 to 287.
    def getIdxPeriod(self):
        return self.time.getIdxPeriod(self.runSCEDTimeFrame)
    
    #------ for real-case model
    def setPathRealCase(self, pathRealCase):  # the last character should be a single forward slash '/'
        self.pathRealCase = pathRealCase

    def setBidFileNameRC(self, bidFileNameRC):
        self.bidFileNameRC = bidFileNameRC

    def setCostCurveRampFileNameRC(self, costCurveRampFileNameRC):
        self.costCurveRampFileNameRC = costCurveRampFileNameRC

    def setHourlyDataFileNameRC(self, hourlyDataFileNameRC):
        self.hourlyDataFileNameRC = hourlyDataFileNameRC

    def setInterfaceFileNameRC(self, interfaceFileNameRC):
        self.interfaceFileNameRC = interfaceFileNameRC

    def setReserveReqFileNameRC(self, reserveReqFileNameRC):
        self.reserveReqFileNameRC = reserveReqFileNameRC

    def setAolFileNameRC(self, aolFileNameRC):
        self.aolFileNameRC = aolFileNameRC
    
    def setRawFileNameRC(self, rawFileNameRC):
        self.rawFileNameRC = rawFileNameRC
    
    def setRtUnitStatusFileNameRC(self, rtUnitStatusFileNameRC):
        self.rtUnitStatusFileNameRC = rtUnitStatusFileNameRC
    
    def setUnitFileNameRC(self, unitFileNameRC): # match between unit name and unit ID/number
        self.unitFileNameRC = unitFileNameRC
    
    def getPathRealCase(self):
        return self.pathRealCase

    def getPathToBidFileNameRC(self):
        return self.pathRealCase + self.bidFileNameRC

    def getPathToCostCurveRampFileNameRC(self):
        return self.pathRealCase + self.costCurveRampFileNameRC

    def getPathToHourlyDataFileNameRC(self):
        return self.pathRealCase + self.hourlyDataFileNameRC

    def getPathToInterfaceFileNameRC(self):
        return self.pathRealCase + self.interfaceFileNameRC

    def getPathToReserveReqFileNameRC(self):
        return self.pathRealCase + self.reserveReqFileNameRC

    def getPathToAolFileNameRC(self):
        return self.pathRealCase + self.aolFileNameRC
    
    def getPathToRawFileNameRC(self):
        return self.pathRealCase + self.rawFileNameRC
    
    def getPathToRtUnitStatusFileNameRC(self):
        return self.pathRealCase + self.rtUnitStatusFileNameRC
    
    def getPathToUnitFileNameRC(self): # match between unit name and unit ID/number
        return self.pathRealCase + self.unitFileNameRC
    
    #------ for generic-case model
    def setPathGenericCase(self, pathGenericCase):  # the last character should be a single forward slash '/'
        self.pathGenericCase = pathGenericCase

    def setRawFileNameGC(self, rawFileNameGC):
        self.rawFileNameGC = rawFileNameGC

    def setCostCurveOutputFileNameGC(self, costCurveOutputFileNameGC):
        self.costCurveOutputFileNameGC = costCurveOutputFileNameGC

    def setCostCurveMultiRampFileNameGC(self, costCurveMultiRampFileNameGC):
        self.costCurveMultiRampFileNameGC = costCurveMultiRampFileNameGC

    def setCostCurveSpinRampFileNameGC(self, costCurveSpinRampFileNameGC):
        self.costCurveSpinRampFileNameGC = costCurveSpinRampFileNameGC

    def getPathGenericCase(self):  # the last character should be a single forward slash '/'
        return self.pathGenericCase

    def getPathToRawFileNameGC(self):
        return self.pathGenericCase + self.rawFileNameGC

    def getPathToCostCurveOutputFileNameGC(self):
        return self.pathGenericCase + self.costCurveOutputFileNameGC

    def getPathToCostCurveMultiRampFileNameGC(self):
        return self.pathGenericCase + self.costCurveMultiRampFileNameGC

    def getPathToCostCurveSpinRampFileNameGC(self):
        return self.pathGenericCase + self.costCurveSpinRampFileNameGC

