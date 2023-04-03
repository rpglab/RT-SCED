"""
Created in 2016

@author: Xingpeng Li (xplipower@gmail.com)

Website: https://rpglab.github.io/resources/RT-SCED_Python/
"""

import os
import math

class generatePyomoFiles():
    'Store data for each flowgate; \
    buses should be a list of objects of Bus-type class'
    def __init__(self, isCodeGeneratePyomoFiles, myDiary):
        self.isCodeGeneratePyomoFiles = isCodeGeneratePyomoFiles
        self.myDiary = myDiary
        self.fileNamePyomoRC = 'pyomoDataForRealCaseModel.dat'     # default name
        self.fileNamePyomoGC = 'pyomoDataForGenericCaseModel.dat'  # default name
        self.isPositivePgPmaxPminNeeded = False

    def setRealCaseModel(self, emsMarketModel):
        self.emsMarketModel = emsMarketModel
    def setGenericCaseModel(self, genericModel):
        self.genericModel = genericModel
        
    def setNeedHeading(self, needHeading):
        self.needHeading = needHeading
    def setIsPositivePgPmaxPminNeeded(self, isPositivePgPmaxPminNeeded):
        self.isPositivePgPmaxPminNeeded = isPositivePgPmaxPminNeeded
    def setBlockPrice(self, blockPrice):
        self.blockPrice = blockPrice
    
    def setFileNamePyomoRC(self, fileNamePyomoRC):
        self.fileNamePyomoRC = fileNamePyomoRC
    def setFileNamePyomoGC(self, fileNamePyomoGC):
        self.fileNamePyomoGC = fileNamePyomoGC
    
    def getFileNamePyomoRC(self):
        return self.fileNamePyomoRC
    def getFileNamePyomoGC(self):
        return self.fileNamePyomoGC
    
    
    #----------- This section (below) is for generic case only ------------#
    def busNumMatchGC(self):
        self.busNumToIdxGC = {}
        idx = 0
        for bus in self.genericModel.buses:
            self.busNumToIdxGC[bus.busNumber] = idx
            idx = idx + 1
    
    def busNumToCostCurveIdx(self):
        self.busNumToCostCurveMultiRampIdxGC = {}
        for idx, genMultiRamp in enumerate(self.genericModel.gensMultiRamp):
            busNumber = genMultiRamp.busNumber
            if self.busNumToCostCurveMultiRampIdxGC.has_key(busNumber) == True:
                array = self.busNumToCostCurveMultiRampIdxGC.get(busNumber)
                array.append(idx)
                self.busNumToCostCurveMultiRampIdxGC[busNumber] = array
            else:
                array = [idx]
                self.busNumToCostCurveMultiRampIdxGC[busNumber] = array
    
        self.busNumToCostCurveSpinRampIdxGC = {}
        for idx, genSpinRamp in enumerate(self.genericModel.gensSpinRamp):
            busNumber = genSpinRamp.busNumber
            if self.busNumToCostCurveSpinRampIdxGC.has_key(busNumber) == True:
                array = self.busNumToCostCurveSpinRampIdxGC.get(busNumber)
                array.append(idx)
                self.busNumToCostCurveSpinRampIdxGC[busNumber] = array
            else:
                array = [idx]
                self.busNumToCostCurveSpinRampIdxGC[busNumber] = array
    
        self.busNumToGenIdxGC = {}
        for idx, gen in enumerate(self.genericModel.gens):
            busNumber = gen.busNumber
            if self.busNumToGenIdxGC.has_key(busNumber) == True:
                array = self.busNumToGenIdxGC.get(busNumber)
                array.append(idx)
                self.busNumToGenIdxGC[busNumber] = array
            else:
                array = [idx]
                self.busNumToGenIdxGC[busNumber] = array
    
    #----------- This section (above) is for generic case only ------------#
    
    # in case that the bus number in raw file is not consecutive from 1 to ... numBuses
    # may not be needed just for Pyomo-based SCED simulation, let's see
    def busNumMatchRC(self):
        self.busNumToIdxRC = {}
        idx = 0
        for bus in self.emsMarketModel.buses:
            self.busNumToIdxRC[bus.busNumber] = idx
            idx = idx + 1
    
    # given a schedule ID, return index of the corresponding unit status data entry
    def unitStatusMatch(self):
        self.statusScheduleIDToIdx = {}
        idx = 0
        for item in self.emsMarketModel.scheduleStatus:
            self.statusScheduleIDToIdx[item.unitScheduleID] = idx
            idx = idx + 1
        
    # given a schedule ID, return index of the corresponding bid data entry
    def unitBidMatch(self):
        self.bidScheduleIDToIdx = {}
        idx = 0
        for item in self.emsMarketModel.bidData:
            self.bidScheduleIDToIdx[item.unitScheduleID] = idx
            idx = idx + 1        
        
    # given a schedule ID, return index of the corresponding energy offer of costcurve_ramprate data entry
    def unitCostCurveMatch(self):
        self.energyCostCurveScheduleIDToIdx = {}
        idx = 0
        for item in self.emsMarketModel.costCurve[0]:
            self.energyCostCurveScheduleIDToIdx[item.unitScheduleID] = idx
            idx = idx + 1

    # given a schedule ID, return index of the corresponding multi/energy ramp of costcurve_ramprate data entry
    def multiRampCostCurveMatch(self):
        self.multiRampCostCurveUnitIDToIdx = {}
        idx = 0
        for item in self.emsMarketModel.costCurve[1]:
            self.multiRampCostCurveUnitIDToIdx[item.unitID] = idx
            idx = idx + 1

    # given a unit ID, return index of the corresponding spin ramp of costcurve_ramprate data entry
    def spinRampCostCurveMatch(self):
        self.spinRampCostCurveUnitIDToIdx = {}
        idx = 0
        for item in self.emsMarketModel.costCurve[2]:
            self.spinRampCostCurveUnitIDToIdx[item.unitID] = idx
            idx = idx + 1

    # given a schedule ID, return index of the corresponding hourly_economic_min_max data entry
    def unitHourlyMatch(self):
        self.hourScheduleIDToIdx = {}
        idx = 0
        for item in self.emsMarketModel.hourlyData:
            if item.unitScheduleID in self.hourScheduleIDToIdx:
                self.hourScheduleIDToIdx[item.unitScheduleID].append(idx)
            else:
                self.hourScheduleIDToIdx[item.unitScheduleID] = [idx]
            idx = idx + 1

    # given a schedule ID, return index of generator in the raw file
    def unitRawMatch(self):
        self.genRawScheduleIDToIdx = {}
        idx = 0
        for gen in self.gens:
            if gen.unitScheduleID > 0:
                self.genRawScheduleIDToIdx[gen.unitScheduleID] = idx
            idx = idx + 1

    # Form the real-case pyomo data file
    def writeAllDataRC(self):
        if self.isCodeGeneratePyomoFiles == True:
            if os.path.isfile(self.fileNamePyomoRC):
                os.remove(self.fileNamePyomoRC)
                self.myDiary.hotline("The original file " + self.fileNamePyomoRC + " has been deleted")
        isDataForRC = True
        generatePyomoFiles.writeBusData(self, self.emsMarketModel.buses, isDataForRC)
        generatePyomoFiles.writeLoadData(self, self.emsMarketModel.loads, isDataForRC)
        generatePyomoFiles.writeGenRCData(self)
        generatePyomoFiles.writeBranchData(self, isDataForRC)
        generatePyomoFiles.writeReserveReqData(self)
        generatePyomoFiles.writeConstraintsData(self)
        if self.isCodeGeneratePyomoFiles == True:
            self.myDiary.hotlineWithLogType(5, "A new file " + self.fileNamePyomoRC + " has been created and filled with needed data")
        else:
            self.myDiary.hotlineWithLogType(5, "All real-case files with regular data-format have been created and filled with needed data")

    # Form the generic-case pyomo data file
    def writeAllDataGC(self):
        if self.isCodeGeneratePyomoFiles == True:
            if os.path.isfile(self.fileNamePyomoGC):
                os.remove(self.fileNamePyomoGC)
                self.myDiary.hotline("The original file " + self.fileNamePyomoGC + " has been deleted")
        isDataForRC = False
        generatePyomoFiles.writeBusData(self, self.genericModel.buses, isDataForRC)
        generatePyomoFiles.writeLoadData(self, self.genericModel.loads, isDataForRC)
        generatePyomoFiles.writeGenGCData(self)
        generatePyomoFiles.writeBranchData(self, isDataForRC)
        if self.isCodeGeneratePyomoFiles == True:
            self.myDiary.hotlineWithLogType(5, "A new file " + self.fileNamePyomoGC + " has been created and filled with needed data")
        else:
            self.myDiary.hotlineWithLogType(5, "All generic-case files with regular data-format have been created and filled with needed data")
        

    # write bus data to a file
    def writeBusData(self, buses, isDataForRC):
        fileNameInit = "busGC.dat"
        if isDataForRC == True:
            fileNameInit = "busRC.dat"
        fileName = generatePyomoFiles.checkIsCodeGeneratePyomoFiles(self, fileNameInit, isDataForRC)
        generatePyomoFiles.dumpNewFileCreation(self, fileName, fileNameInit)
        with open(fileName, 'a') as f:
            heading = "  Bus_number Bus_kv Bus_va Bus_area "
            if self.isCodeGeneratePyomoFiles == True:
                f.write("param: BUS: " + heading + " :=")
            elif self.needHeading == True:
                f.write("  index" + heading)
            f.write("\n")
            
            idx = 0
            for bus in buses:
                idx = idx + 1
                f.write("%s %d" % (" ", idx))
                f.write("%s %d" % (" ", bus.busNumber))
                f.write("%s %f" % (" ", bus.busKV))
                f.write("%s %f" % (" ", bus.busVa))
                f.write("%s %d %s" % (" ", bus.busArea, "\n"))
            if self.isCodeGeneratePyomoFiles == True:
                f.write(";\n\n")

    # write load data to a file
    def writeLoadData(self, loads, isDataForRC):
        fileNameInit = "loadGC.dat"
        if isDataForRC == True:
            fileNameInit = "loadRC.dat"
        fileName = generatePyomoFiles.checkIsCodeGeneratePyomoFiles(self, fileNameInit, isDataForRC)
        generatePyomoFiles.dumpNewFileCreation(self, fileName, fileNameInit)
        with open(fileName, 'a') as f:
            heading = "  Load_busNumber Load_id Load_isInSvc Load_pd "
            if self.isCodeGeneratePyomoFiles == True:
                f.write("param:  LOAD: " + heading + " :=")
            elif self.needHeading == True:
                f.write("  index" + heading)
            f.write("\n")
            
            idx = 0
            for load in loads:
                idx = idx + 1
                f.write("%s %d" % (" ", idx))
                f.write("%s %d" % (" ", load.busNumber))
                f.write("%s %s" % (" ", load.loadID))
                f.write("%s %d" % (" ", load.isInSvc))
                f.write("%s %f" % (" ", load.Pload))
                f.write("%s" % ("\n"))
            if self.isCodeGeneratePyomoFiles == True:
                f.write(";\n\n")

    # write gen and genCost data to separate files
    def writeGenGCData(self):
        generatePyomoFiles.busNumToCostCurveIdx(self)
        
        fileNameInit = "genCostGC.dat"
        isDataForRC = False
        fileName = generatePyomoFiles.checkIsCodeGeneratePyomoFiles(self, fileNameInit, isDataForRC)
        generatePyomoFiles.dumpNewFileCreation(self, fileName, fileNameInit)
        genIdxHasCostCurve = {}
        with open(fileName, 'a') as f:
            heading = "  GenCost_genIdx GenCost_segmentIdx GenCost_segmentBreadth GenCost_segmentPrice"
            if self.isCodeGeneratePyomoFiles == True:
                f.write("param:  GENCOST: " + heading + " :=")
            elif self.needHeading == True:
                f.write("  index" + heading)
            f.write("\n")

            mwSegmentPreviousData = 0
            busNumberPreviousData = -1
            genIDPreviousData = -1
            genIdxPreviousData = -1
            idxSegment = -1
            for idx, genCostCurveOutput in enumerate(self.genericModel.gensCostCurveOutput):
                busNumber = genCostCurveOutput.busNumber
                genID = genCostCurveOutput.genID
                
                isTheSameGenPrior = False
                if busNumber == busNumberPreviousData:
                    if genID == genIDPreviousData:
                        isTheSameGenPrior = True
                        genIdx = genIdxPreviousData
                        idxSegment = idxSegment + 1
                if isTheSameGenPrior == False:
                    genIdx = generatePyomoFiles.findTheGenIdxGC(self, busNumber, genID)
                    genIdxHasCostCurve[genIdx] = 1
                    if genIdx == -1:
                        self.myDiary.hotlineWithLogType(2, "the "+str(idx+1)+"-th line of cost curve cannot be matched to a valid generator, thus, skipped")
                        continue
                    busNumberPreviousData = busNumber
                    genIDPreviousData = genID
                    genIdxPreviousData = genIdx
                    idxSegment = 1
                    mwSegmentPreviousData = 0
                f.write("%s %d" % (" ", (idx+1)))
                f.write("%s %d" % (" ", (genIdx+1)))
                f.write("%s %d" % (" ", idxSegment))
                segmentBreadth = genCostCurveOutput.MW - mwSegmentPreviousData
                if segmentBreadth < 0:
                    segmentBreadth = 0
                    self.myDiary.hotlineWithLogType(2, "the "+str(idx+1)+"-th line of cost curve has negative segment breadth, thus, it is set to 0")
                f.write("%s %f" % (" ", segmentBreadth))
                f.write("%s %f" % (" ", genCostCurveOutput.price))
                f.write("%s" % ("\n"))
                mwSegmentPreviousData = genCostCurveOutput.MW
            if self.isCodeGeneratePyomoFiles == True:
                f.write(";\n\n")
        self.myDiary.hotlineWithLogType(6, "The number of generators that have cost curve is: "+str(len(genIdxHasCostCurve)))

        fileNameInit = "genGC.dat"
        isDataForRC = False
        fileName = generatePyomoFiles.checkIsCodeGeneratePyomoFiles(self, fileNameInit, isDataForRC)
        generatePyomoFiles.dumpNewFileCreation(self, fileName, fileNameInit)
        with open(fileName, 'a') as f:
            heading = "  Gen_busNumber Gen_id  Gen_isInSvc  Gen_pgInit Gen_pgMax Gen_pgMin Gen_energyRamp Gen_spinRamp Gen_costCurveFlag"
            if self.isCodeGeneratePyomoFiles == True:
                f.write("param:  GEN: " + heading + " :=")
            elif self.needHeading == True:
                f.write("  index" + heading)
            f.write("\n")

            for idx, gen in enumerate(self.genericModel.gens):
                f.write("%s %d" % (" ", (idx+1)))
                f.write("%s %d" % (" ", gen.busNumber))
                f.write("%s %s" % (" ", gen.genID))
                f.write("%s %d" % (" ", gen.isInSvc))
                
                pgen = gen.PGen
                if self.isPositivePgPmaxPminNeeded == True:
                    if pgen < 0:
                        self.myDiary.hotlineWithLogType(1, "When generate generic case, unit " + str(idx+1) + " pgen is negative, " + str(pgen) + ", is set to 0")
                        pgen = 0
                f.write("%s %f" % (" ", pgen))
                
                pgmax = gen.PMax
                if self.isPositivePgPmaxPminNeeded == True:
                    if pgmax < 0:
                        self.myDiary.hotlineWithLogType(1, "When generate generic case, unit " + str(idx+1) + " pgmax is negative, " + str(pgmax) + ", is set to 0")
                        pgmax = 0
                f.write("%s %f" % (" ", pgmax))
                
                pgmin = gen.PMin
                if self.isPositivePgPmaxPminNeeded == True:
                    if pgmin < 0:
                        self.myDiary.hotlineWithLogType(1, "When generate generic case, unit " + str(idx+1) + " pgmin is negative, " + str(pgmin) + ", is set to 0")
                        pgmin = 0
                f.write("%s %f" % (" ", pgmin))
                
                multiRamprate = generatePyomoFiles.findTheRampRate(self, gen.busNumber, gen.genID, gen.PGen, \
                                self.busNumToCostCurveMultiRampIdxGC, self.genericModel.gensMultiRamp)
                spinRamprate = generatePyomoFiles.findTheRampRate(self, gen.busNumber, gen.genID, gen.PGen, \
                                self.busNumToCostCurveSpinRampIdxGC, self.genericModel.gensSpinRamp)
                f.write("%s %f" % (" ", multiRamprate))
                f.write("%s %f" % (" ", spinRamprate))

                hasCostCurveFlag = 0
                if genIdxHasCostCurve.has_key(idx):
                    hasCostCurveFlag = 1
                f.write("%s %d" % (" ", hasCostCurveFlag))
                f.write("%s" % ("\n"))
            if self.isCodeGeneratePyomoFiles == True:
                f.write(";\n\n")
            
                
    def findTheGenIdxGC(self, busNumber, genID):
        indices = self.busNumToGenIdxGC[busNumber]
        for idx in indices:
            gen = self.genericModel.gens[idx]
            if gen.genID == genID:
                return idx
        return -1
            
    def findTheRampRate(self, busNumber, genID, pg, busNumToCostCurveRampIdx, costcurveRampIdx):
        ramprate = 0
        if busNumToCostCurveRampIdx.has_key(busNumber) == False:
            return ramprate
        indicesRamp = busNumToCostCurveRampIdx[busNumber]
        for idxRamp in indicesRamp:
            genRamp = costcurveRampIdx[idxRamp]
            if genRamp.genID != genID:
                continue
            for idxMW, mw in enumerate(genRamp.rampMWs):
                if pg < mw:
                    return genRamp.rampRates[idxMW]
        return ramprate

    # write gen and genCost data to separate files
    def writeGenRCData(self):
        matchUnitID(self.emsMarketModel.gens, self.emsMarketModel.units)
        generatePyomoFiles.unitBidMatch(self)
        generatePyomoFiles.unitCostCurveMatch(self)
        generatePyomoFiles.multiRampCostCurveMatch(self)
        generatePyomoFiles.spinRampCostCurveMatch(self)
        generatePyomoFiles.unitHourlyMatch(self)
        generatePyomoFiles.unitStatusMatch(self)
        findUnitScheduleID(self.emsMarketModel, self.statusScheduleIDToIdx)

        gens = self.emsMarketModel.gens
        bids = self.emsMarketModel.bidData
        hourlyData = self.emsMarketModel.hourlyData
        costCurve = self.emsMarketModel.costCurve
        energyOffers = costCurve[0]
        multiRampRates = costCurve[1]
        spinRampRate = costCurve[2]

        RegUnitStatus = []
        Reg_Offer_Mw = []
        SpinUnitStatus = []
        Spin_Offer_Mw = []
        EconMax = []
        EconMin = []
        for gen in gens:
            scheduleID = gen.unitScheduleID
            flagUsingDummyValues = False
            if scheduleID in self.hourScheduleIDToIdx:
                idxItems = self.hourScheduleIDToIdx[scheduleID]
            else:
                flagUsingDummyValues = True
            idxTarget = -1
            if flagUsingDummyValues == False:
                idxTarget = findHourlyDataIdx(hourlyData, idxItems, self.emsMarketModel.date, self.emsMarketModel.time.hour)
                if (idxTarget < 0):
                    flagUsingDummyValues = True
            if flagUsingDummyValues == True:
                RegUnitStatus.append(-1)
                Reg_Offer_Mw.append(-1)
                SpinUnitStatus.append(-1)
                Spin_Offer_Mw.append(-1)
                EconMax.append(-1)
                EconMin.append(-1)
            else:
                RegUnitStatus.append(hourlyData[idxTarget].regUnitStatus)
                Reg_Offer_Mw.append(hourlyData[idxTarget].regOfferMW)
                SpinUnitStatus.append(hourlyData[idxTarget].spinStatus)
                Spin_Offer_Mw.append(hourlyData[idxTarget].spinOfferMW)
                EconMax.append(hourlyData[idxTarget].econMax)
                EconMin.append(hourlyData[idxTarget].econMin)
                
        CostCurveSegmentNum = []
        genIdxCostCurve = []
        segmentIdxCostCurve = []
        segmentBreadthCostCurve = []
        segmentPriceCostCurve = []
        
        idx = 0
        idxGen = 0
        for gen in gens:
            idxGen = idxGen + 1
            unitScheduleID = gen.unitScheduleID
            idxOffer = -1
            if unitScheduleID in self.energyCostCurveScheduleIDToIdx:
                idxOffer = self.energyCostCurveScheduleIDToIdx[unitScheduleID]
            if idxOffer == -1:
                CostCurveSegmentNum.append(0)
                continue
            MWs = energyOffers[idxOffer].MWs
            prices = energyOffers[idxOffer].prices
            CostCurveSegmentNum.append(len(MWs))
            for idxTmp in range(0, len(prices)):
                idx = idx + 1
                genIdxCostCurve.append(idxGen)
                segmentIdxCostCurve.append(idxTmp+1)
                if idxTmp == 0:
                    segmentBreadthCostCurve.append(MWs[idxTmp])
                else:
                    segmentBreadthCostCurve.append(MWs[idxTmp] - MWs[idxTmp-1])
                segmentPriceCostCurve.append(prices[idxTmp])

        EnergyRamp = getGensRamp(gens, multiRampRates, self.multiRampCostCurveUnitIDToIdx, bids, self.bidScheduleIDToIdx)
        SpinRamp = getGensRamp(gens, spinRampRate, self.spinRampCostCurveUnitIDToIdx, bids, self.bidScheduleIDToIdx)
        
        gensUseBidSlope = []
        fileNameInit = "genRC.dat"
        isDataForRC = True
        fileName = generatePyomoFiles.checkIsCodeGeneratePyomoFiles(self, fileNameInit, isDataForRC)
        generatePyomoFiles.dumpNewFileCreation(self, fileName, fileNameInit)
        with open(fileName, 'a') as f:
            heading = "  Gen_busNumber Gen_id  Gen_isInSvc  Gen_pgInit Gen_pgMax Gen_pgMin Gen_hasMarketData"
            heading = heading + " Gen_useBidSlope  Gen_costCurveSegmentNum  Gen_energyRamp Gen_spinRamp Gen_regUnitStatus"
            heading = heading + " Gen_regOfferPrice Gen_regOfferMW Gen_spinUnitStatus Gen_spinOfferPrice Gen_spinOfferMW"
            heading = heading + " Gen_fastStartUnitFlag Gen_coldNotificationTime Gen_coldStartupTime Gen_area "
            if self.isCodeGeneratePyomoFiles == True:
                f.write("param:  GEN: " + heading + " :=")
            elif self.needHeading == True:
                f.write("  unitID unitScheduleID index" + heading + " genName")
            f.write("\n")

            idx = 0
            for gen in self.emsMarketModel.gens:
                if self.isCodeGeneratePyomoFiles == False:
                    f.write("%s %d" % (" ", gen.unitID))   
                    f.write("%s %d" % (" ", gen.unitScheduleID))

                f.write("%s %d" % (" ", (idx+1)))
                f.write("%s %d" % (" ", gen.busNumber))
                f.write("%s %s" % (" ", gen.genID))
                f.write("%s %d" % (" ", gen.isInSvc))
                
                pgen = gen.PGen
                if self.isPositivePgPmaxPminNeeded == True:
                    if pgen < 0:
                        self.myDiary.hotlineWithLogType(1, "When generate real EMS-Market case, unit " + str(idx+1) + " pgen is negative, " + str(pgen) + ", is set to 0")
                        pgen = 0
                f.write("%s %f" % (" ", pgen))
                
                scheduleID = gen.unitScheduleID
                if scheduleID < 0:
                    pgmax = gen.PMax
                    pgmin = gen.PMin
                    #make sure pgmax and pgmin is postive
                    if self.isPositivePgPmaxPminNeeded == True:
                        if pgmax < 0:
                            self.myDiary.hotlineWithLogType(1, "When generate real EMS-Market case, unit " + str(idx+1) + " pgmax is negative, " + str(pgmax) + ", is set to 0")
                            pgmax = 0
                        if pgmin < 0:
                            self.myDiary.hotlineWithLogType(1, "When generate real EMS-Market case, unit " + str(idx+1) + " pgmin is negative, " + str(pgmin) + ", is set to 0")
                            pgmin = 0
                    f.write("%s %f" % (" ", pgmax))
                    f.write("%s %f" % (" ", pgmin))
                    for i in range(0, 15):
                        f.write(" 0")
                    gensUseBidSlope.append(0)
                else:
                    idxBid = self.bidScheduleIDToIdx[scheduleID]
                    bid = bids[idxBid]
                    pgmax = bid.econMax
                    pgmin = bid.econMin
                    if EconMax[idx] != -1:
                        pgmax = EconMax[idx]
                        pgmin = EconMin[idx]
                    #make sure pgmax and pgmin is postive
                    if self.isPositivePgPmaxPminNeeded == True:
                        if pgmax < 0:
                            self.myDiary.hotlineWithLogType(1, "When generate real EMS-Market case, unit " + str(idx+1) + " pgmax is negative, " + str(pgmax) + ", is set to 0")
                            pgmax = 0
                        if pgmin < 0:
                            self.myDiary.hotlineWithLogType(1, "When generate real EMS-Market case, unit " + str(idx+1) + " pgmin is negative, " + str(pgmin) + ", is set to 0")
                            pgmin = 0
                    f.write("%s %f" % (" ", pgmax))
                    f.write("%s %f" % (" ", pgmin))
                    f.write("%s %d" % (" ", 1))
                    f.write("%s %d" % (" ", bid.useBidSlope))
                    gensUseBidSlope.append(bid.useBidSlope)
                    
                    f.write("%s %d" % (" ", CostCurveSegmentNum[idx]))
                    f.write("%s %f" % (" ", EnergyRamp[idx]))
                    f.write("%s %f" % (" ", SpinRamp[idx]))

                    notANaN = True
                    if math.isnan(RegUnitStatus[idx]):
                        notANaN = False
                    if math.isnan(bid.regOfferPrice):
                        notANaN = False
                    if math.isnan(Reg_Offer_Mw[idx]):
                        notANaN = False
                    if notANaN:
                        f.write("%s %d" % (" ", RegUnitStatus[idx]))
                        f.write("%s %f" % (" ", bid.regOfferPrice))
                        f.write("%s %f" % (" ", Reg_Offer_Mw[idx]))
                    else:
                        f.write("%s %d" % (" ", 0))
                        f.write("%s %d" % (" ", 0))
                        f.write("%s %d" % (" ", 0))
                        
                    notANaN = True
                    if math.isnan(SpinUnitStatus[idx]):
                        notANaN = False
                    if math.isnan(bid.spinOfferPrice):
                        notANaN = False
                    if math.isnan(Spin_Offer_Mw[idx]):
                        notANaN = False
                    if notANaN:
                        f.write("%s %d" % (" ", SpinUnitStatus[idx]))
                        f.write("%s %f" % (" ", bid.spinOfferPrice))
                        f.write("%s %f" % (" ", Spin_Offer_Mw[idx]))
                    else:
                        f.write("%s %d" % (" ", 0))
                        f.write("%s %d" % (" ", 0))
                        f.write("%s %d" % (" ", 0))
                    
                    fastStartTol = 1.0/6  # 10 minutes
                    coldnotificationtime = bid.coldNotificationTime
                    coldstartuptime = bid.coldStartupTime
                    FastStartUnitFlag = 0
                    if (coldnotificationtime + coldstartuptime) < fastStartTol:
                        FastStartUnitFlag = 1
                    f.write("%s %d" % (" ", FastStartUnitFlag))
                    f.write("%s %f" % (" ", coldnotificationtime)) # in hour
                    f.write("%s %f" % (" ", coldstartuptime))  # in hour
                    
                    f.write("%s %d" % (" ", bid.localeID))
                if self.isCodeGeneratePyomoFiles == False:
                    f.write(" %s" % (gen.comment))
                f.write("%s" % ("\n"))
                idx = idx + 1
            if self.isCodeGeneratePyomoFiles == True:
                f.write(";\n\n")
        
        fileNameInit = "genCostRC.dat"
        isDataForRC = True
        fileName = generatePyomoFiles.checkIsCodeGeneratePyomoFiles(self, fileNameInit, isDataForRC)
        generatePyomoFiles.dumpNewFileCreation(self, fileName, fileNameInit)
        with open(fileName, 'a') as f:
            heading = "  GenCost_genIdx GenCost_segmentIdx  GenCost_segmentBreadth  GenCost_segmentPrice "
            if self.isCodeGeneratePyomoFiles == True:
                f.write("param:  GENCOST: " + heading + " :=")
            elif self.needHeading == True:
                f.write("  index" + heading)
            f.write("\n")

            idxPyomo = 0
            idxSegment = 1
            doLinearization = False
            idxPriorGen = -1
            for idx in range(0, len(genIdxCostCurve)):
                idxGen = genIdxCostCurve[idx] - 1
                if idxPriorGen != idxGen:
                    doLinearization = False
                    idxPriorGen = idxGen
                
                if gensUseBidSlope[idxGen] == 1 and segmentIdxCostCurve[idx] != 1:
                    doLinearization = True
                
                if doLinearization == False:
                    idxSegment = 1
                    idxPyomo = idxPyomo + 1
                    f.write("%s %d" % (" ", idxPyomo))
                    #f.write("%s %d" % (" ", idxGenCostCurve[idx]))
                    f.write("%s %d" % (" ", genIdxCostCurve[idx]))
                    f.write("%s %d" % (" ", segmentIdxCostCurve[idx]))
                    f.write("%s %f" % (" ", segmentBreadthCostCurve[idx]))
                    f.write("%s %f" % (" ", segmentPriceCostCurve[idx]))
                    f.write("%s" % ("\n"))
                else:
                    p1 = segmentPriceCostCurve[idx-1]
                    p2 = segmentPriceCostCurve[idx]
                    m1 = 0
                    m2 = segmentBreadthCostCurve[idx]
                    pm = linearInterpolate(p1, m1, p2, m2, self.blockPrice)
                    ps = pm[0]
                    ms = pm[1]
                    for k in range(1, len(ps)):
                        idxPyomo = idxPyomo + 1
                        idxSegment = idxSegment + 1
                        f.write("%s %d" % (" ", idxPyomo))
                        f.write("%s %d" % (" ", genIdxCostCurve[idx]))
                        f.write("%s %d" % (" ", idxSegment))
                        f.write("%s %f" % (" ", ms[k]))
                        f.write("%s %f" % (" ", ps[k]))
                        f.write("%s" % ("\n"))
            if self.isCodeGeneratePyomoFiles == True:
                f.write(";\n\n")
            

    # write reserve requirements to a file
    def writeReserveReqData(self):
        fileNameInit = "reserveReqRC.dat"
        isDataForRC = True
        fileName = generatePyomoFiles.checkIsCodeGeneratePyomoFiles(self, fileNameInit, isDataForRC)
        generatePyomoFiles.dumpNewFileCreation(self, fileName, fileNameInit)
        with open(fileName, 'a') as f:
            heading = "  ReserveArea_genArea ReserveArea_regulationReq  ReserveArea_reqPenaltyPrice  ReserveArea_spinReq"
            heading = heading + " ReserveArea_spinPenaltyPrice ReserveArea_primaryReq ReserveArea_primaryPenaltyPrice "
            if self.isCodeGeneratePyomoFiles == True:
                f.write("param:  RESERVEArea: " + heading + " :=")
            elif self.needHeading == True:
                f.write("  index" + heading)
            f.write("\n")

            reserveReq = self.emsMarketModel.reserveReq
            PJMRTO_Reg = reserveReq.PJMRTO_Reg
            PJMRTO_SR = reserveReq.PJMRTO_SR
            PJMRTO_PR = reserveReq.PJMRTO_PR
            MAD_SR = reserveReq.MAD_SR
            MAD_PR = reserveReq.MAD_PR
            
            f.write("%s %d %f %f %f %f %f %f" % (" 1 ", PJMRTO_Reg[0], PJMRTO_Reg[1], PJMRTO_Reg[2], \
                          PJMRTO_SR[1], PJMRTO_SR[2], PJMRTO_PR[1], PJMRTO_PR[2]))
            f.write("%s" % ("\n"))
            f.write("%s %d %f %f %f %f %f %f" % (" 2 ", MAD_SR[0], 0, 0, \
                          MAD_SR[1], MAD_SR[2], MAD_PR[1], MAD_PR[2],))
            f.write("%s" % ("\n"))
            if self.isCodeGeneratePyomoFiles == True:
                f.write(";\n\n")

    # write branch data to a file
    def writeBranchData(self, isDataForRC):
        fileNameInit = "branchRC.dat"
        branches = ''
        if isDataForRC == True:
            branches = self.emsMarketModel.branches
            generatePyomoFiles.busNumMatchRC(self)
            calcLineFlow(branches, self.emsMarketModel.buses, self.busNumToIdxRC)
        else:
            fileNameInit = "branchGC.dat"
            generatePyomoFiles.busNumMatchGC(self)
            branches = self.genericModel.branches
            calcLineFlow(branches, self.genericModel.buses, self.busNumToIdxGC)
        fileName = generatePyomoFiles.checkIsCodeGeneratePyomoFiles(self, fileNameInit, isDataForRC)
        generatePyomoFiles.dumpNewFileCreation(self, fileName, fileNameInit)
        with open(fileName, 'a') as f:
            heading = "  Branch_frmBusNumber Branch_toBusNumber  Branch_id  Branch_isInSvc Branch_r Branch_x Branch_angle "
            heading = heading + " Branch_pkInit Branch_rateA Branch_rateB Branch_rateC "
            if self.isCodeGeneratePyomoFiles == True:
                f.write("param:  BRANCH: " + heading + " :=")
            elif self.needHeading == True:
                f.write("  index" + heading)
            f.write("\n")

            idx = 0
            for branch in branches:
                idx = idx + 1
                f.write("%s %d" % (" ", idx))
                f.write("%s %d" % (" ", branch.frmBusNumber))
                f.write("%s %d" % (" ", branch.toBusNumber))
                f.write("%s %s" % (" ", branch.brcID))
                f.write("%s %d" % (" ", branch.isInSvc))
                f.write("%s %f" % (" ", branch.R))
                f.write("%s %f" % (" ", branch.X))
                angleInRadian = branch.angle * math.pi / 180
                f.write("%s %f" % (" ", angleInRadian))
                f.write("%s %f" % (" ", branch.pkInitMW))
                f.write("%s %f" % (" ", branch.rateA))
                f.write("%s %f" % (" ", branch.rateB))
                f.write("%s %f" % (" ", branch.rateC))
                f.write("%s" % ("\n"))
            if self.isCodeGeneratePyomoFiles == True:
                f.write(";\n\n")

    # write contingency data to a file
    def writeConstraintsData(self):
        flowgates = self.emsMarketModel.flowgates
        gens = self.emsMarketModel.gens
        branches = self.emsMarketModel.branches
        idxPeriod = self.emsMarketModel.idxPeriod
        
        allContingency = []
        allConstraint = []
        allDFax = []
        flowgateNumbers = []
        
        idxCtcgy = 0
        aolDFAX = self.emsMarketModel.aolDFAX
        constDFaxAOL = aolDFAX.constDFaxAOL
        for dfaxConst in constDFaxAOL:
            idx = findFlowgate(dfaxConst, flowgates)
            if idx == -1:
                continue
            
            flowgate = flowgates[idx]
            constraintNames = flowgate.constraintNames
            idxConstraint = -1
            for constraintName in constraintNames:
                idx = findBranch(branches, constraintName)
                if idx != -1:
                    idxConstraint = idx + 1
                    break
            if idxConstraint == -1:
                self.myDiary.hotlineWithLogType(1, "All constraints associaed with flowgate number "+ str(flowgate.fgNumber) + " cannot be found in the raw file; and hence ingored")
                continue
            
            flowgateNumbers.append(flowgate.fgNumber)
            idxCtcgy = idxCtcgy + 1
            limit = flowgate.limitData[idxPeriod]
            allConstraint.append([idxCtcgy, idxConstraint, limit])
            
            if flowgate.constraintType == "Actual":
                allContingency.append([idxCtcgy, -2])
            else:
                contingencyNames = flowgate.contingencyNames
                for contingencyName in contingencyNames:
                    idx = findBranch(branches, contingencyName)
                    if idx != -1:
                        idx = idx + 1
                    allContingency.append([idxCtcgy, idx])
            
            pnodeNames = dfaxConst.PnodeNames
            dFaxValues = dfaxConst.dFaxes
            genDFax = []
            for gen in gens:
                genName = gen.comment
                idx = findIdxSameName(pnodeNames, genName)
                if idx == -1:
                    genDFax.append(0)
                else:
                    genDFax.append(dFaxValues[idx])
            allDFax.append(genDFax)
            
        fileNameInit = "contingencyRC.dat"
        isDataForRC = True
        fileName = generatePyomoFiles.checkIsCodeGeneratePyomoFiles(self, fileNameInit, isDataForRC)
        generatePyomoFiles.dumpNewFileCreation(self, fileName, fileNameInit)
        with open(fileName, 'a') as f:
            heading = "  Contingency_idx Contingency_branchIdx "
            if self.isCodeGeneratePyomoFiles == True:
                f.write("param:  CONTINGENCY: " + heading + " :=")
            elif self.needHeading == True:
                f.write("  index" + heading)
            f.write("\n")

            for idx in range(0, len(allContingency)):
                f.write("%s %d" % (" ", (idx+1)))
                f.write("%s %d" % (" ", allContingency[idx][0]))
                f.write("%s %d" % (" ", allContingency[idx][1]))
                f.write("%s" % ("\n"))
            if self.isCodeGeneratePyomoFiles == True:
                f.write(";\n\n")
                
        fileNameInit = "constraintRC.dat"
        isDataForRC = True
        fileName = generatePyomoFiles.checkIsCodeGeneratePyomoFiles(self, fileNameInit, isDataForRC)
        generatePyomoFiles.dumpNewFileCreation(self, fileName, fileNameInit)
        with open(fileName, 'a') as f:
            heading = "  Constraint_contingencyIdx Constraint_monitorBranchIdx Constraint_monitorBranchLimit "
            if self.isCodeGeneratePyomoFiles == True:
                f.write("param:  CONSTRAINT: " + heading + " :=")
            elif self.needHeading == True:
                f.write("  index" + heading)
            f.write("\n")

            for idx in range(0, len(allConstraint)):
                f.write("%s %d" % (" ", (idx+1)))
                f.write("%s %d" % (" ", allConstraint[idx][0]))
                f.write("%s %d" % (" ", allConstraint[idx][1]))
                f.write("%s %f" % (" ", allConstraint[idx][2]))
                f.write("%s" % ("\n"))
            if self.isCodeGeneratePyomoFiles == True:
                f.write(";\n\n")

        fileNameInit = "scenarioRC.dat"   # including both base case and contingency case
        isDataForRC = True
        fileName = generatePyomoFiles.checkIsCodeGeneratePyomoFiles(self, fileNameInit, isDataForRC)
        generatePyomoFiles.dumpNewFileCreation(self, fileName, fileNameInit)
        with open(fileName, 'a') as f:
            heading = "  isBaseCase "
            if self.isCodeGeneratePyomoFiles == True:
                f.write("param:  SCENARIO: " + heading + " :=")
            elif self.needHeading == True:
                f.write("  index" + heading)
            f.write("\n")

            scenario = []
            for idx in range(0, len(allContingency)):
                idxCntgy = allContingency[idx][0]
                if idxCntgy in scenario:
                    continue
                else:
                    scenario.append(idxCntgy)
                    f.write("%s %d" % (" ", len(scenario)))
                    if idxCntgy == -2:
                        f.write("%s %d" % (" ", 1))
                    else:
                        f.write("%s %d" % (" ", 0))
                    f.write("%s" % ("\n"))
            if self.isCodeGeneratePyomoFiles == True:
                f.write(";\n\n")
                
        fileNameInit = "DFaxRC.dat"
        isDataForRC = True
        fileName = generatePyomoFiles.checkIsCodeGeneratePyomoFiles(self, fileNameInit, isDataForRC)
        generatePyomoFiles.dumpNewFileCreation(self, fileName, fileNameInit)
        with open(fileName, 'a') as f:
            rowIdxStr = " "
            for idx in range(1, len(allConstraint)+1):
                rowIdxStr = rowIdxStr + str(idx) + " "
            heading = " dFax "
            if self.isCodeGeneratePyomoFiles == True:
                f.write("param  " + heading + ":   " + rowIdxStr + " := ")
            elif self.needHeading == True:
                f.write("  twoDimIdx " + rowIdxStr)
            f.write("\n")

            for idx in range(0, len(gens)):
                f.write("%s %d" % (" ", (idx+1)))
                for jdx in range(0, len(allConstraint)):
                    f.write("%s %f" % (" ", allDFax[jdx][idx]))
                f.write("%s" % ("\n"))
            if self.isCodeGeneratePyomoFiles == True:
                f.write(";\n\n")
                
    def checkIsCodeGeneratePyomoFiles(self, fileName, isDataForRC):
        if self.isCodeGeneratePyomoFiles == False:
            if os.path.isfile(fileName):
                os.remove(fileName)
                self.myDiary.hotline("original file " + fileName + " has been deleted")        
        else:
            if isDataForRC == True:
                fileName = self.fileNamePyomoRC
            else:
                fileName = self.fileNamePyomoGC
        return fileName

    def dumpNewFileCreation(self, fileName, fileNameInit):
        if fileName == fileNameInit:
            self.myDiary.hotline("A new file " + fileName + " will be created very soon")

def findBranch(branches, lineName):
    for idx, branch in enumerate(branches):
        if lineName == branch.comment:
            return idx
        elif lineName == branch.xfmcomment:
            return idx
    return -1
    
def findIdxSameName(pnodeNames, genName):
    for idx, pnodeName in enumerate(pnodeNames):
        if pnodeName == genName:
            return idx
    return -1

def findFlowgate(dfaxConst, flowgates):
    nameDFaxConst = dfaxConst.constraintName
    for idx, flowgate in enumerate(flowgates):
        if nameDFaxConst == flowgate.fgName:
            return idx
    return -1

def calcLineFlow(branches, buses, busNumToIdx):
    for branch in branches:
        idxFrmBus = busNumToIdx[branch.frmBusNumber]
        idxToBus = busNumToIdx[branch.toBusNumber]
        
        # TODO: for now, the DC power flow model is used to calculate the Pk_init in MW
        deltaK = buses[idxFrmBus].busVa - buses[idxToBus].busVa
        pkInit = 100*deltaK/branch.X  # by timing 100 is to convert per unit value to MW value
        branch.setPkInitMW(pkInit)

def matchUnitID(gens, units):
    flag = []
    for i in range(0, len(units)):
        flag.append(-1)
    # excluding generators outside PJM territory
    for i in range(0, len(units)):
        unit = units[i]
        if unit.pool != "PJM":
            flag[i] = 0
    numMatched = 0
    for gen in gens:
        longName = gen.comment
        gen.setUnitID(-1)
        idx = 0
        for unit in units:
            foundIt = False
            if flag[idx] == -1:
                if unit.station in longName:
                    if unit.voltage in longName:
                        if unit.unitName in longName:
                            foundIt = True
            if foundIt:
                gen.setUnitID(unit.unitID)
                flag[idx] = 0
                numMatched = numMatched + 1
                break
            idx = idx + 1
#    print "number of units matched: ", numMatched
    

# find the scheduleID from bid data
def findUnitScheduleID(emsMarketModel, statusScheduleIDToIdx):
    idx = 0
    bids = emsMarketModel.bidData
    scheduleStatus = emsMarketModel.scheduleStatus
    idxPeriod = emsMarketModel.idxPeriod
    for gen in emsMarketModel.gens:
        unitID = gen.unitID
        if unitID == -1:
            gen.setUnitScheduleID(-1)
        else:
            unitList = findValues(bids, unitID)
            if len(unitList) == 0:
                gen.setUnitScheduleID(-2)
            else:
                unitListValid = []
                for idx in unitList:
                    scheduleID = bids[idx].unitScheduleID
                    idxItem = statusScheduleIDToIdx[scheduleID]
                    if scheduleStatus[idxItem].isScheduleAvailable(idxPeriod):
                        unitListValid.append(idx)
                if len(unitListValid) == 0:
                    gen.setUnitScheduleID(-3)
                else:
                    idxUnitPriceScheduleID = findPriceSchedule(bids, unitListValid)
                    gen.setUnitScheduleID(bids[idxUnitPriceScheduleID].unitScheduleID)


# a heuristic way to achieve it
def findPriceSchedule(bids, unitListValid):
    idxUnitPriceScheduleID = unitListValid[0]
    unitPriceScheduleID = bids[unitListValid[0]].unitScheduleID
    for idx in range(1, len(unitListValid)):
        if bids[unitListValid[idx]].unitScheduleID > unitPriceScheduleID:
            idxUnitPriceScheduleID = unitListValid[idx]
            unitPriceScheduleID = bids[unitListValid[idx]].unitScheduleID
    return idxUnitPriceScheduleID
            
                
def findValues(bids, unitID):
    idxList = []
    for i in range(0, len(bids)):
        if bids[i].unitID == unitID:
            idxList.append(i)
    return idxList
    
def findValue(array, number):
    idx = 0
    for item in array:
        if number == item:
            return idx
        idx = idx + 1
    return -1

import GeneralClasses
# find the same hour item, if no same item, then, find the closest time period
def findHourlyDataIdx(hourlyData, idxItems, date, hour):
    idxTarget = -1
    diffHour = float("inf")
    for idx in idxItems:
        diffHour2 = GeneralClasses.calcDiffHours(date, hour, hourlyData[idx].date, hourlyData[idx].hour)
        if diffHour2 < diffHour:
            diffHour = diffHour2
            idxTarget = idx
    return idxTarget


def getGensRamp(gens, rampRates, rampCostCurveUnitIDToIdx, bids, bidScheduleIDToIdx):
    gensRamp = []
    for gen in gens:
        ramp = 0
        idxRamp = -1
        unitID = gen.unitID
        if unitID in rampCostCurveUnitIDToIdx:
            idxRamp = rampCostCurveUnitIDToIdx[unitID]
        if idxRamp == -1:
            unitScheduleID = gen.unitScheduleID
            if unitScheduleID in bidScheduleIDToIdx:
                idxBid = bidScheduleIDToIdx[unitScheduleID]
                ramp = bids[idxBid].defaultRampRate
        else:
            pginit = gen.PGen
            idxSegment = getRampIdx(rampRates[idxRamp].MWs, pginit)
            if idxSegment != -1:
                ramp = rampRates[idxRamp].ramprates[idxSegment]
        gensRamp.append(ramp)
    return gensRamp
    
def getRampIdx(MWs, pginit):
    for idx, MW in enumerate(MWs):
        if MW >= pginit:
            return idx
    return -1


def linearInterpolate(p1, m1, p2, m2, deltaP):
    ps = [p1]
    ms = [m1]

    if m2 != 0 and abs(p2-p1) > deltaP:
        n = int(math.ceil((p2 - p1) / deltaP))
        #print "n: ", n
        bw = (m2 - m1) / n
        slope = (m2 - m1) / (p2 - p1)
        for k in range(1,n+1):
            p = p1 + (k-0.5)*bw/slope
            ps.append(p)
            #m = m1 + slope*(p-p1)
            ms.append(bw)
    else:
        ps.append(p2)
        ms.append(m2)
    return [ps, ms]

