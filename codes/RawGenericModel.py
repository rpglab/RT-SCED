"""
Created in 2016

@author: Xingpeng Li (xplipower@gmail.com)

Website: https://rpglab.github.io/resources/RT-SCED_Python/
"""

class GenericModel:
    ' Store all generic model data'
    def __init__(self, buses, loads, gens, branches, gensCostCurveOutput, gensMultiRamp, gensSpinRamp):
        self.buses = buses
        self.loads = loads
        self.gens = gens
        self.branches = branches
        self.gensCostCurveOutput = gensCostCurveOutput
        self.gensMultiRamp = gensMultiRamp  
        self.gensSpinRamp = gensSpinRamp


class Bus:
    'Store bus data for power flow case'
    def __init__(self, busNumber, busKV, busType, busArea, busVa):
        self.busNumber = busNumber
        #self.busName = busName
        self.busKV = busKV
        self.busType = busType 
        self.busArea = busArea 
        self.busVa = busVa   # store the angle in radian
    def setVm(self, busVm):
        self.busVm = busVm


class Load:
    def __init__(self, busNumber, loadID, isInSvc, Pload):
        self.busNumber = busNumber
        self.loadID = loadID
        self.isInSvc = isInSvc
        self.Pload = Pload     # MW
        #self.Qload = Qload     # Mvar
    def setComment(self, comment):
        self.comment = comment
    

class Gen:
    def __init__(self, busNumber, genID, isInSvc, PGen, PMax, PMin):
        self.busNumber = busNumber
        self.genID = genID
        self.isInSvc = isInSvc     # binary, 1-In service, 0-out of service
        self.PGen = PGen    # in MW
        self.PMax = PMax    # in MW 
        self.PMin = PMin    # in MW 
    def setComment(self, comment):
        self.comment = comment    # name after symbol '/*'
    def setUnitID(self, unitID):
        self.unitID = unitID        # unitID is an integer number, if -1, then, not in the market-EMS data
    def setUnitScheduleID(self, unitScheduleID):
        self.unitScheduleID = unitScheduleID        # unitScheduleID is an integer number, 
                    # unitScheduleID: -1, the unitID is -1
                    # unitScheduleID: -2, the unitID cannot be found in the bid_data
                    # unitScheduleID: -3, the unitID is found in the bid_data, however, the schedule is not available per rt_unit_status_fix_20160409


class Branch:
    def __init__(self, frmBusNumber, toBusNumber, brcID, isInSvc, X, rateA, rateB, rateC):
        self.frmBusNumber = frmBusNumber   # a positve number
        self.toBusNumber = toBusNumber     # a negative number
        self.brcID = brcID     
        self.isInSvc = isInSvc    # binary, 1-In service, 0-out of service  
        self.X = X     
        self.rateA = rateA     
        self.rateB = rateB     
        self.rateC = rateC     
        self.isXfm = 0  # may not needed
        self.tap = 1    # may not needed
        self.isPS = 0
        self.alpha = 0
    def setXfm(self, tap):
        self.isXfm = 1
        self.tap = tap
    def setPS(self, alpha):
        self.isPS = 1
        self.alpha = alpha
    def setPSXfm(self, tap, alpha):
        self.isXfm = 1
        self.tap = tap
        self.isPS = 1
        self.alpha = alpha
    def setComment(self, comment):
        self.comment = comment
    def setXfmComment(self, xfmcomment):
        self.xfmcomment = xfmcomment
    def setR(self, R):
        self.R = R
    def setAngle(self, angle):
        self.angle = angle
    def setPkInitMW(self, pkInitMW):  
        self.pkInitMW = pkInitMW
    def setPkInitMVar(self, pkInitMVar):  
        self.pkInitMVar = pkInitMVar
    def setPkInitMVA(self, pkInitMVA):  
        self.pkInitMVA = pkInitMVA
    

class GenRamp:
    'Store data for generator multiple ramping'
    def __init__(self, busNumber, genID, rampMWs, rampRates):
        self.busNumber = busNumber
        self.genID = genID
        self.rampMWs = rampMWs
        self.rampRates = rampRates
    

class CostCurveOutputList:
    'Store data for cost-curve output'
    def __init__(self, output):
        self.output = output
    
class CostCurveOutput:
    'Store data for cost-curve output'
    def __init__(self, busNumber, genID, SID, segmentnumber, MW, price):
        self.busNumber = busNumber
        self.genID = genID
        self.SID = SID
        self.segmentnumber = segmentnumber
        self.MW = MW
        self.price = price
    
