"""
Created in 2016

@author: Xingpeng Li (xplipower@gmail.com)
"""

import GeneralFunctions
import GeneralClasses
import RawGenericModel
import RawEMSMarketModel

import math

#/////////////////////////// --- Read Generic Model Data --- ////////////////////////////
def endOfRawItem(line):
#    print line
    if not line:
        return True
    if (line.startswith("0")):
        if line.upper().find("END") == -1:  # these two lines aare for double-check purpose
            raise SystemExit   # or use: sys.exit()
        return True
    else:
        return False

def getStrings(line):
    strs = GeneralFunctions.split(line, ',', '\'')
    strs = GeneralFunctions.strip(strs)
    return strs

# /--- Code to read bus data ---/
def readBusData(line):
    strs = getStrings(line)
    busNumber = int(strs[0])
    busKV = float(strs[2])
    busType = int(strs[3])
    busArea = int(strs[6])
    busVa = math.radians(float(strs[9]))
    bus = RawGenericModel.Bus(busNumber, busKV, busType, busArea, busVa)
    busVm = float(strs[8])
    bus.setVm(busVm)
    return bus

def loadBuses(pf, myDiary):
    buses = []
    myDiary.hotline("Start to read raw file - bus data")
    line = pf.readline()
    while not endOfRawItem(line):
        bus = readBusData(line)
        #tempdict = bus.__dict__
        #print tempdict
        buses.append(bus)
        line = pf.readline()
    myDiary.hotline("Finish reading raw file - bus data")
    myDiary.hotlineWithLogType(6, "   there are " + str(len(buses)) + " buses")
    return buses


# /--- Code to read load data ---/
def readLoadData(line):
    strs = getStrings(line)
    busNumber = int(strs[0])
    loadID = strs[1]
    isInSvc = int(strs[2])
    Pload = float(strs[5])
    load = RawGenericModel.Load(busNumber, loadID, isInSvc, Pload)
    return load

def loadLoads(pf, myDiary):
    myDiary.hotline("Start to read raw file - load data")
    numInSvc = 0
    mwInSvc = 0
    loads = []
    line = pf.readline()
    while not endOfRawItem(line):
        load = readLoadData(line)
        comment = GeneralFunctions.returnSpecialComments(line, '/*')
        load.setComment(comment)
        if load.isInSvc == 1:
            numInSvc = numInSvc + 1
            mwInSvc = mwInSvc + load.Pload
        loads.append(load)
        line = pf.readline()
    myDiary.hotline("Finish reading raw file - load data")
    myDiary.hotlineWithLogType(6, "   there are " + str(len(loads)) + " loads")
    myDiary.hotlineWithLogType(6, "   there are " + str(numInSvc) + " in-service loads" )
    myDiary.hotlineWithLogType(6, "   the total in-service load in MW is: " + str(mwInSvc))
    return loads


# /--- Code to read Gen data ---/
def readGenData(line):
    strs = getStrings(line)
    busNumber = int(strs[0])
    genID = strs[1]
    isInSvc = int(strs[14])
    PGen = float(strs[2])
    PMax = float(strs[16])
    PMin = float(strs[17])
    gen = RawGenericModel.Gen(busNumber, genID, isInSvc, PGen, PMax, PMin)
    return gen

def loadGens(pf, myDiary):
    myDiary.hotline("Start to read raw file - generator data")
    numInSvc = 0
    mwInSvc = 0 # capacity
    gens = []
    line = pf.readline()
    while not endOfRawItem(line):
        gen = readGenData(line)
        comment = GeneralFunctions.returnSpecialComments(line, '/*')
        comment = removeY(comment)
        gen.setComment(comment)
        if gen.isInSvc == 1:
            numInSvc = numInSvc + 1
            mwInSvc = mwInSvc + gen.PMax
        gens.append(gen)
        line = pf.readline()
    myDiary.hotline("Finish reading raw file - generator data")
    myDiary.hotlineWithLogType(6, "   there are " + str(len(gens)) + " generators")
    myDiary.hotlineWithLogType(6, "   there are " + str(numInSvc) + " in-service generators" )
    myDiary.hotlineWithLogType(6, "   the total in-service generation capacity in MW is: " + str(mwInSvc))
    return gens

# the name may end with " Y", which should be removed
def removeY(comment):
    if comment.endswith(" Y"):
        comment = comment[:len(comment)-2].rstrip()
    return comment

# /--- Code to read Branch data ---/
def readBranchData(line):
    strs = getStrings(line)
    frmBusNumber = int(strs[0])
    toBusNumber = int(strs[1])
    brcID = strs[2]
    isInSvc = int(strs[15])
    X = float(strs[4])
    rateA = float(strs[6])
    rateB = float(strs[7])
    rateC = float(strs[8])
    branch = RawGenericModel.Branch(abs(frmBusNumber), abs(toBusNumber), brcID, isInSvc, X, rateA, rateB, rateC)
    branch.setR(float(strs[3]))
    if float(strs[9]) != 0:
        branch.setAngle(float(strs[10]))
    else:
        branch.setAngle(0.0)
    branch.setXfmComment("")
    return branch

def loadBranches(pf, myDiary):
    myDiary.hotline("Start to read raw file - branch data")
    numInSvc = 0
    branches = []
    line = pf.readline()
    while not endOfRawItem(line):
        branch = readBranchData(line)
        comment = GeneralFunctions.returnSpecialComments(line, '/*')
        branch.setComment(comment)
        if branch.isInSvc == 1:
            numInSvc = numInSvc + 1
        branches.append(branch)
        line = pf.readline()
    
    # get Xfm extra comment/name
    line = pf.readline()
    while not endOfRawItem(line):
        strs = getStrings(line)
        frmBusNumber = int(strs[0])
        toBusNumber = int(strs[1])
        brcID = strs[2]
        idxBrc = findIdxBranch(branches, frmBusNumber, toBusNumber, brcID)
        if idxBrc != -1:
            xfmComment = GeneralFunctions.returnSpecialComments(line, '/*')
            xfmComment = removeXfmYinfo(xfmComment)
            branches[idxBrc].setXfmComment(xfmComment)
        line = pf.readline()
        
    myDiary.hotline("Finish reading raw file - branch data")
    myDiary.hotlineWithLogType(6, "   there are " + str(len(branches)) + " branches")
    myDiary.hotlineWithLogType(6, "   there are " + str(numInSvc) + " in-service branches" )
    return branches

# anything after " Y" will be removed
def removeXfmYinfo(xfmComment):
    idx = xfmComment.find(" Y")
    if idx != -1:
        xfmComment = xfmComment[:idx].rstrip()
    return xfmComment

def findIdxBranch(branches, frmBusNumber, toBusNumber, brcID):
    idxBrc = -1
    for idx, branch in enumerate(branches):
        if frmBusNumber != branch.frmBusNumber:
            continue
        if toBusNumber != branch.toBusNumber:
            continue
        if brcID != branch.brcID:
            continue
        idxBrc = idx
        break
    return idxBrc

def splitStrings(strs, num):
    strings = []
    for i in range(num):
        temp = []
        strings.append(temp)
    size = len(strs)/num
    for i in range(size):
        for j in range(num):
            strings[j].append(strs[i*num+j])
    return strings


# /--- Code to read Cost Curve Ramp data ---/
def readCostCurveRamp(fileRamp, myDiary):
    myDiary.hotline("Start to read cost curve ramp data")
    gensRamp = []
    line = fileRamp.readline()
    while 1 :
        if not line:
            break
        strs = line.split(",")
        strs = GeneralFunctions.strip(strs)
        busNumber = int(strs[0])
        genID = strs[1]
        strings = splitStrings(strs[2:], 2)
        MWs = GeneralFunctions.getFloatNumbers(strings[0])
        ramprates = GeneralFunctions.getFloatNumbers(strings[1])
        ramp = RawGenericModel.GenRamp(busNumber, genID, MWs, ramprates)
        gensRamp.append(ramp)
        line = fileRamp.readline()
    myDiary.hotline("Finish reading cost curve ramp data")
    return gensRamp
    

# /--- Code to read Cost Curve Output data ---/
def readCostCurveOutput(fileOutput, myDiary):
    myDiary.hotline("Start to read cost curve output (MW/Price) data")
    outputs = []
    line = fileOutput.readline()
    while 1 :
        if not line:
            break
        strs = line.split(",")
        strs = GeneralFunctions.strip(strs)
        busNumber = int(strs[0])
        genID = strs[1]
        SID = strs[2]
        segmentnumber = int(strs[3])
        MW = float(strs[4])
        price = float(strs[5])
        output = RawGenericModel.CostCurveOutput(busNumber, genID, SID, segmentnumber, MW, price)
        outputs.append(output)
        line = fileOutput.readline()
    myDiary.hotline("Finish reading cost curve output (MW/Price) data")
    return outputs
        

#/////////////////////////// --- Read EMS-Market Data --- ////////////////////////////
# Read EMS-Market Interface file
def readPD_Interface(filePD, myDiary):
    myDiary.hotline("Start to read EMS-Market Interface/flowgate data")
    flowgates = []
    line = filePD.readline()
    line = line.strip()
    while 1 :
        if line.startswith("flowgate"):
            line = line[8:]
            line = line.lstrip()
            idx = line.find('"')
            fgNumber = line[:idx]
            fgNumber = fgNumber.rstrip()
            fgNumber = int(fgNumber)
            line = line[(idx+1):]
            idx = line.find('"')
            fgName = line[:idx].strip()
            fgType = line[(idx+1):]
            fgType = fgType.strip()
            
            constraintNames = []
            line = filePD.readline()
            line = line.strip()
            line = nextUncommentedLine(filePD, line)
            while line != 'contingency':
                constraintNames.append(line[1:len(line)-1])
                line = filePD.readline()
                line = line.strip()
                line = nextUncommentedLine(filePD, line)
            
            line = filePD.readline()
            line = line.strip()
            line = nextUncommentedLine(filePD, line)
            contingencyNames = []
            contingencyTypes = []
            while not line.startswith('end'):
                idx = line.find('"')
                line = line[(idx+1):]
                idx = line.find('"')
                contingencyNames.append(line[:idx])
                line = line[(idx+1):]
                idx = line.find('"')
                constraintType = 'contingency'
                if idx == -1:
                    contingencyTypes.append('')
                    constraintType = 'Actual'
                else:
                    line = line[(idx+1):]
                    idx = line.find('"')
                    contingencyTypes.append(line[:idx])
                line = filePD.readline()
                line = line.strip()
                line = nextUncommentedLine(filePD, line)
            flowgate = RawEMSMarketModel.Flowgate(fgNumber, fgName, fgType, constraintType, constraintNames, contingencyNames, contingencyTypes)
            flowgates.append(flowgate)
        if line.startswith("[Limit Data]"):
            flowgates = saveInterfaceData(flowgates, filePD, "Limit Data")
        if line.startswith("[LimitControl Data]"):
            flowgates = saveInterfaceData(flowgates, filePD, "LimitControl Data")
        if line.startswith("[UDSFlow Data]"):
            flowgates = saveInterfaceData(flowgates, filePD, "UDSFlow Data")
        if line.startswith("[SEFlow Data]"):
            flowgates = saveInterfaceData(flowgates, filePD, "SEFlow Data")
        if line.startswith("[UDSShadowPrice Data]"):
            flowgates = saveInterfaceData(flowgates, filePD, "UDSShadowPrice Data")
        if line.startswith("[UDSShadowPriceLimit Data]"):
            flowgates = saveInterfaceData(flowgates, filePD, "UDSShadowPriceLimit Data")
        if line.startswith("[LPAFlow Data]"):
            flowgates = saveInterfaceData(flowgates, filePD, "LPAFlow Data")
        if line.startswith("[LPAShadowPrice Data]"):
            flowgates = saveInterfaceData(flowgates, filePD, "LPAShadowPrice Data")
        
        line = isMultiEmptyLines(filePD, 3)
        if not line:
            break
    myDiary.hotline("Finish reading EMS-Market Interface/flowgate data")
    return flowgates

def saveInterfaceData(flowgates, filePD, flag):
    for flowgate in flowgates:
        line = filePD.readline()
        numbers = line.split()
        if flowgate.fgNumber == int(numbers[0]):
            listData = []
            for number in numbers[1:]:
                listData.append(float(number))
            if len(listData) != 288:
                print "ERROR: the flowgate ", flowgate.fgNumber, " does not have exactly 288 ", flag
                raise SystemExit   # or use: sys.exit()
        if flag == "Limit Data":
            flowgate.setLimitData(listData)
        if flag == "LimitControl Data":
            flowgate.setLimitCtlData(listData)
        if flag == "UDSFlow Data":
            flowgate.setUDSFlowData(listData)
        if flag == "SEFlow Data":
            flowgate.setSEFlowData(listData)
        if flag == "UDSShadowPrice Data":
            flowgate.setUDSShadowPriceData(listData)
        if flag == "UDSShadowPriceLimit Data":
            flowgate.setUDSShadowPriceLimitData(listData)
        if flag == "LPAFlow Data":
            flowgate.setLPAFlowData(listData)
        if flag == "LPAShadowPrice Data":
            flowgate.setLPAShadowPriceData(listData)
    line = filePD.readline()   # this line should be: [End Data]
    return flowgates

# Return next uncommented line if this line starts with "//"
def nextUncommentedLine(filePD, line):
    while line.startswith('//'):
        line = filePD.readline()
        line = line.strip()
    return line

# if there are num consecutive empty lines, then return empty string,
# otherwise, return the first non-empty line ever found.
def isMultiEmptyLines(filePD, num):
    for idx in range(num):
        line = filePD.readline()
        line = line.strip()
        if line:
            return line
    return ''


# Read EMS-Market AOL file
def readAOL(fileAOL, myDiary):
    myDiary.hotline("Start to read EMS-Market AOL data")
    line = fileAOL.readline()
    line = fileAOL.readline()
    datetime = line.split(",")[4]
    datetime = datetime.split()
    date = datetime[0]
    time = datetime[1]
    aolDFAX = RawEMSMarketModel.DFAXList(date, time)
    constDFaxAOL = []
    line = fileAOL.readline()
    while not isEndAOL(line):
        if isHeadingLineAOL(line):
            line = fileAOL.readline()
            tokens = splitLineAOL(line)
            constraintName = tokens[4].strip()
            
            dfaxConst = RawEMSMarketModel.DFAX(constraintName)
            dfaxConst.setLimit(float(tokens[6]))
            dfaxConst.setPflow(float(tokens[7]))
            dfaxConst.setQflow(float(tokens[8]))
            dfaxConst.setViolationPenalty(float(tokens[12]))
            dfaxConst.setCntgyDescription(tokens[13])
            dfaxConst.setPenaltyExpansionLimit(float(tokens[15]))

            findNextHeading(fileAOL)
            findNextHeading(fileAOL)
            line = fileAOL.readline()
            pnodeNames = []
            dFaxes = []
            while not isDataEndAOL(line):
                tokens = line.split(",")
                pnodeNames.append(tokens[5].strip())
                dFaxes.append(float(tokens[6].strip()))
                line = fileAOL.readline()
            dfaxConst.setPnodeNames(pnodeNames)
            dfaxConst.setDFAXes(dFaxes)
        constDFaxAOL.append(dfaxConst)
    aolDFAX.setDFAXs(constDFaxAOL)
    myDiary.hotline("Finish reading EMS-Market AOL data")
    return aolDFAX

def isHeadingLineAOL(line):
    if line.startswith("I,"):
        return True
    else:
        return False

def isDataEndAOL(line):
    if line.startswith("D,"):
        return False
    else:
        return True

def isEndAOL(line):
    if line.startswith("C,"):
        return True
    else:
        return False

def splitLineAOL(line):
    tokens = line.split(",")
    tokens = GeneralFunctions.strip(tokens)
    return tokens

def findNextHeading(fileAOL):
    line = fileAOL.readline()
    while not isHeadingLineAOL(line):
        line = fileAOL.readline()
    return line


# Read EMS-Market Reserve Requirement file
def readReserveReq(csvReserveReq, myDiary):
    myDiary.hotline("Start to read Reserve Requirement data")
    line = csvReserveReq.next()
    line = csvReserveReq.next()

    line = csvReserveReq.next()
    PJMRTO_Reg = [int(line[2])]
    PJMRTO_Reg.append(float(line[10]))
    PJMRTO_Reg.append(float(line[11]))

    line = csvReserveReq.next()
    PJMRTO_SR = [int(line[2])]
    PJMRTO_SR.append(float(line[10]))
    PJMRTO_SR.append(float(line[11]))

    line = csvReserveReq.next()
    PJMRTO_PR = [int(line[2])]
    PJMRTO_PR.append(float(line[10]))
    PJMRTO_PR.append(float(line[11]))

    line = csvReserveReq.next()
    MAD_SR = [int(line[2])]
    MAD_SR.append(float(line[10]))
    MAD_SR.append(float(line[11]))

    line = csvReserveReq.next()
    MAD_PR = [int(line[2])]
    MAD_PR.append(float(line[10]))
    MAD_PR.append(float(line[11]))

    reserveReq = RawEMSMarketModel.ReserveReq(PJMRTO_Reg, PJMRTO_SR, PJMRTO_PR, MAD_SR, MAD_PR)
    myDiary.hotline("Finish reading Reserve Requirement data")
    return reserveReq


# Read EMS-Market bid file
def readBidData(csvBidData, myDiary):
    myDiary.hotline("Start to read Bid data")
    row = csvBidData.next()
    bids = []
    for row in csvBidData:
        pnodeID = int(row[0].strip())
        unitID = int(row[1].strip())
        unitScheduleID = int(row[4].strip())
        bid = RawEMSMarketModel.Bid(pnodeID, unitID, unitScheduleID)
        
        bid.setOperatingRate(stringToFloat(row[6]))
        bid.setColdNotificationTime(stringToFloat(row[10]))
        bid.setColdStartupTime(stringToFloat(row[18]))
        bid.setEconMax(stringToFloat(row[23]))
        bid.setEconMin(stringToFloat(row[24]))
        bid.setDefaultRampRate(stringToFloat(row[32]))
        bid.setUseBidSlope(stringToInt(row[34]))
        bid.setPricedBasedSchedule(stringToFloat(row[36]))
        bid.setSpinOfferPrice(stringToFloat(row[44]))
        bid.setRegOfferPrice(stringToFloat(row[45]))
        bid.setLocaleID(stringToFloat(getStrippedString(row[48])))
        bids.append(bid)
    myDiary.hotline("Finish reading Bid data")
    return bids

# Read EMS-Market hourly data file
def readHourlyData(csvHourlyData, myDiary):
    myDiary.hotline("Start to read EMS-Market hourly updated data")
    row = csvHourlyData.next()
    hrItems = []
    for row in csvHourlyData:
        pnodeID = int(row[0].strip())
        unitID = int(row[1].strip())
        unitScheduleID = int(row[24].strip())
        hrItem = RawEMSMarketModel.HrEconMinMax(pnodeID, unitID, unitScheduleID)
#        print unitScheduleID
        
        hrItem.setEconMin(stringToFloat(row[3]))
        hrItem.setEconMax(stringToFloat(row[4]))
        hrItem.setRegUnitStatus(stringToInt(row[14]))
        hrItem.setSpinOfferMW(stringToFloat(row[16]))
        hrItem.setSpinStatus(stringToInt(row[17]))
        hrItem.setRegOfferMW(stringToFloat(row[20]))
        hrItem.setEffectiveHour(analyzeDateTime(row[23].strip()))
        hrItems.append(hrItem)
    myDiary.hotline("Finish reading EMS-Market hourly updated data")
    return hrItems

# Read EMS-Market unit schedule status file
def readScheduleStatus(csvScheduleStatus, myDiary):
    myDiary.hotline("Start to read EMS-Market unit schedule status data")
    row = csvScheduleStatus.next()
    row = csvScheduleStatus.next()
    ssItems = []
    for row in csvScheduleStatus:
        pnodeID = int(row[0].strip())
        unitID = int(row[1].strip())
        unitScheduleID = int(row[3].strip())
        ssItem = RawEMSMarketModel.RtUnitStatusFix(pnodeID, unitID, unitScheduleID)
        
        hrValues = ''
        for i in range(4, 28):
            hrValues += row[i].strip()
        ssItem.setScheduleSt(hrValues)
        ssItems.append(ssItem)
    myDiary.hotline("Finish reading EMS-Market unit schedule status data")
    return ssItems


# Read EMS-Market cost curve file
def readCostCurve(csvCostCurve, myDiary):
    myDiary.hotline("Start to read EMS-Market cost curve data")
    row = csvCostCurve.next()
    row = csvCostCurve.next()
    energyOffers = []
    multiRampRates = []
    spinRampRates = []
    typeMark = 0
    for row in csvCostCurve:
        if isHeadingLineCostCurve(row):
            typeMark += 1
            continue
            
        if typeMark == 0:
            pnodeID = int(row[2].strip())
            unitID = int(row[3].strip())
            unitScheduleID = int(row[4].strip())
            energy = RawEMSMarketModel.CostcurveEnergy(pnodeID, unitID, unitScheduleID)
            pairs = giveMeFloatPairs(row, 5)
            energy.setOffers(pairs[0], pairs[1])
            energyOffers.append(energy)
        elif typeMark == 1:
            unitID = int(row[2].strip())
            multiRampRate = RawEMSMarketModel.CostcurveMultiRamp(unitID)
            pairs = giveMeFloatPairs(row, 3)
            multiRampRate.setOffers(pairs[0], pairs[1])
            multiRampRates.append(multiRampRate)
        elif typeMark == 2:
            unitID = int(row[2].strip())
            spinRampRate = RawEMSMarketModel.CostcurveSpinRamp(unitID)
            pairs = giveMeFloatPairs(row, 3)
            spinRampRate.setOffers(pairs[0], pairs[1])
            spinRampRates.append(spinRampRate)
    myDiary.hotline("Finish reading EMS-Market cost curve data")
    return [energyOffers, multiRampRates, spinRampRates]


# Read EMS-Market unit match info file
def readUnits(csvUnits, myDiary):
    myDiary.hotline("Start to read unit match (between ID/Number and name) info data")
    row = csvUnits.next()
    units = []
    for row in csvUnits:
        unitID = int(row[6].strip())
        unit = RawEMSMarketModel.UnitIdentification(unitID)
        unit.setInfo(row[0].strip(), row[3].strip(), row[4].strip(), row[5].strip())
        units.append(unit)
    myDiary.hotline("Finish reading unit match (between ID/Number and name) info data")
    return units


def stringToFloat(str):
    if not str:
        return float('nan')
    else:
        return float(str.strip())

def stringToInt(str):
    if not str:
        return float('nan')
    else:
        return int(str.strip())

def getStrippedString(str):
    if not str:
        return str
    else:
        return str.strip()

# The input string needed to be trimmed.
# and it should have the format of MM/DD/YEAR HR:MN:SD
# or the format of MM/DD/YEAR HR:MN
def analyzeDateTime(str):
    idx = str.find('/')
    MM = int(str[:idx])
    str = str[(idx+1):]
    idx = str.find('/')
    DD = int(str[:idx])
    idxSpace = str.find(' ')
    YY = int(str[(idx+1):idxSpace])
    date = GeneralClasses.Date(MM, DD, YY)
    str = str[(idxSpace+1):].lstrip()
    tokens = str.split(':')
    HR = int(tokens[0])
    MN = int(tokens[1])
    SD = 0
    if len(tokens) == 3:
        SD = int(tokens[2])
    time = GeneralClasses.Time(HR, MN, SD)
    return [date, time]
    
def isHeadingLineCostCurve(row):
    if row[0] == "I":
        return True
    else:
        return False

def giveMeFloatPairs(row, beginIdx):
    left = []
    right = []
    for idx in range(beginIdx, len(row), 2):
        if not row[idx+1]:
            break
        left.append(float(row[idx]))
        right.append(float(row[idx+1]))
    return [left, right]


