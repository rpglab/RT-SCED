"""
Created in 2016

@author: Xingpeng Li (xplipower@gmail.com)

Website: https://rpglab.github.io/resources/RT-SCED_Python/
"""

class EMSMarketModel:
    ' Store all EMS-Market data'
    def __init__(self, buses, loads, gens, branches, flowgates, aolDFAX, \
                     reserveReq, bidData, hourlyData, scheduleStatus, costCurve):
        self.buses = buses
        self.loads = loads
        self.gens = gens
        self.branches = branches
        self.flowgates = flowgates
        self.aolDFAX = aolDFAX
        self.reserveReq = reserveReq
        self.bidData = bidData
        self.hourlyData = hourlyData
        self.scheduleStatus = scheduleStatus
        self.costCurve = costCurve  # contains [energyOffers, multiRampRates, spinRampRate]
    def setUnits(self, units):
        self.units = units
    def setDate(self, date):   # date = GeneralClasses.Date(MM, DD, YY)
        self.date = date
    def setTime(self, time):   # time = GeneralClasses.Time(HR, MN, SD)
        self.time = time
    def setIdxPeriod(self, idxPeriod):
        self.idxPeriod = idxPeriod   # index of period, from 0 to 287,  (period of 5 minute interval)


class FlowgateList:
    'Store data for each flowgate; \
     buses should be a list of objects of Bus-type class'
    def __init__(self, flowgates):
        self.flowgates = flowgates

class Flowgate:
    def __init__(self, fgNumber, fgName, fgType, constraintType, \
                     constraintNames, contingencyNames, contingencyTypes):
        self.fgNumber = fgNumber
        self.fgName = fgName
        self.fgType = fgType 
        self.constraintType = constraintType       # a string indicates: either "Actual" or "Contingency" 
        self.constraintNames = constraintNames     # a list
        self.contingencyNames = contingencyNames   # a list
        self.contingencyTypes = contingencyTypes   # a list
    def setLimitData(self, limitData):
        self.limitData = limitData
    def setLimitCtlData(self, limitCtlData):
        self.limitCtlData = limitCtlData
    def setUDSFlowData(self, UDSFlowData):
        self.UDSFlowData = UDSFlowData
    def setSEFlowData(self, SEFlowData):
        self.SEFlowData = SEFlowData
    def setUDSShadowPriceData(self, UDSShadowPriceData):
        self.UDSShadowPriceData = UDSShadowPriceData
    def setUDSShadowPriceLimitData(self, UDSShadowPriceLimitData):
        self.UDSShadowPriceLimitData = UDSShadowPriceLimitData
    def setLPAFlowData(self, LPAFlowData):
        self.LPAFlowData = LPAFlowData
    def setLPAShadowPriceData(self, LPAShadowPriceData):
        self.LPAShadowPriceData = LPAShadowPriceData


class DFAXList:
    def __init__(self, data, time):
        self.data = data
        self.time = time
        
    def setDFAXs(self, constDFaxAOL):
        self.constDFaxAOL = constDFaxAOL

class DFAX:
    def __init__(self, constraintName):
        self.constraintName = constraintName

    def setLimit(self, limit):
        self.limit = limit
    def setPflow(self, pflow):
        self.pflow = pflow
    def setQflow(self, qflow):
        self.qflow = qflow
    def setViolationPenalty(self, violationPenalty):
        self.violationPenalty = violationPenalty
    def setCntgyDescription(self, cntgyDescription):
        self.cntgyDescription = cntgyDescription
    def setPenaltyExpansionLimit(self, penaltyExpansionLimit):
        self.penaltyExpansionLimit = penaltyExpansionLimit
    def setDFAXes(self, dFaxes):
        self.dFaxes = dFaxes
    def setPnodeNames(self, PnodeNames):
        self.PnodeNames = PnodeNames


# local_as_service_20160409.csv
class ReserveReq:
    def __init__(self, PJMRTO_Reg, PJMRTO_SR, PJMRTO_PR, MAD_SR, MAD_PR):
        self.PJMRTO_Reg = PJMRTO_Reg    # Contain three numbers: 0 is Locale_ID, 1 is MW requirement, 2 is penalty price.
        self.PJMRTO_SR = PJMRTO_SR
        self.PJMRTO_PR = PJMRTO_PR
        self.MAD_SR = MAD_SR
        self.MAD_PR = MAD_PR
        

# bid_data_20160409.csv
class BidList:
    def __init__(self, bids):
        self.bids = bids

class Bid:
    def __init__(self, pnodeID, unitID, unitScheduleID):
        self.pnodeID = pnodeID
        self.unitID = unitID
        self.unitScheduleID = unitScheduleID

    def setOperatingRate(self, operatingRate):
        self.operatingRate = operatingRate
    def setColdNotificationTime(self, coldNotificationTime):
        self.coldNotificationTime = coldNotificationTime
    def setColdStartupTime(self, coldStartupTime):
        self.coldStartupTime = coldStartupTime
    def setEconMax(self, econMax):
        self.econMax = econMax
    def setEconMin(self, econMin):
        self.econMin = econMin
    def setDefaultRampRate(self, defaultRampRate):
        self.defaultRampRate = defaultRampRate
    def setUseBidSlope(self, useBidSlope):
        self.useBidSlope = useBidSlope
    def setPricedBasedSchedule(self, pricedBasedSchedule):
        self.pricedBasedSchedule = pricedBasedSchedule
    def setSpinOfferPrice(self, spinOfferPrice):
        self.spinOfferPrice = spinOfferPrice
    def setRegOfferPrice(self, regOfferPrice):
        self.regOfferPrice = regOfferPrice
    def setLocaleID(self, localeID):
        self.localeID = localeID


# hourly_economic_min_max_20160409.csv
class HrEconMinMaxList:
    def __init__(self, hrEcons):
        self.hrEcons = hrEcons

class HrEconMinMax:
    def __init__(self, pnodeID, unitID, unitScheduleID):
        self.pnodeID = pnodeID
        self.unitID = unitID
        self.unitScheduleID = unitScheduleID

    def setEconMin(self, econMin):
        self.econMin = econMin
    def setEconMax(self, econMax):
        self.econMax = econMax
    def setRegUnitStatus(self, regUnitStatus):
        self.regUnitStatus = regUnitStatus
    def setSpinStatus(self, spinStatus):
        self.spinStatus = spinStatus
    def setRegOfferMW(self, regOfferMW):
        self.regOfferMW = regOfferMW
    def setSpinOfferMW(self, spinOfferMW):
        self.spinOfferMW = spinOfferMW
    def setEffectiveHour(self, effectiveHour):  # effectiveHour = [Date, Time] -- two user-defined classes
        self.effectiveHour = effectiveHour      # 
        self.date = effectiveHour[0]
        self.hour = effectiveHour[1].hour
        self.minute = effectiveHour[1].minute
        self.second = effectiveHour[1].second


# rt_unit_status_fix_20160409.csv
class RtUnitStatusFixList:
    def __init__(self, rtUnitStFix):
        self.rtUnitStFix = rtUnitStFix

class RtUnitStatusFix:
    def __init__(self, pnodeID, unitID, unitScheduleID):
        self.pnodeID = pnodeID
        self.unitID = unitID
        self.unitScheduleID = unitScheduleID

    def setScheduleSt(self, scheduleSt):
        self.scheduleSt = scheduleSt  # a string with 299 characters
        
    def isScheduleAvailable(self, idxPeriod):  # idxPeriod is from 0 to 287.
        if self.scheduleSt[idxPeriod] == 'U':
            return False
        else:
            return True


# costcurve_ramprate_20160409.csv
class CostcurveEnergy:
    def __init__(self, pnodeID, unitID, unitScheduleID):
        self.pnodeID = pnodeID
        self.unitID = unitID
        self.unitScheduleID = unitScheduleID

    def setOffers(self, MWs, prices):
        self.MWs = MWs
        self.prices = prices

class CostcurveMultiRamp:
    def __init__(self, unitID):
        self.unitID = unitID

    def setOffers(self, MWs, ramprates):
        self.MWs = MWs
        self.ramprates = ramprates

class CostcurveSpinRamp:
    def __init__(self, unitID):
        self.unitID = unitID

    def setOffers(self, MWs, ramprates):
        self.MWs = MWs
        self.ramprates = ramprates


# Units.csv
class UnitIdentification:
    def __init__(self, unitID):
        self.unitID = unitID

    def setInfo(self, pool, station, voltage, unitName):
        self.pool = pool
        self.station = station
        self.voltage = voltage
        self.unitName = unitName

