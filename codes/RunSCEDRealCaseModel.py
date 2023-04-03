"""
Created in 2016

@author: Xingpeng Li (xplipower@gmail.com)
"""

# -----------------------------------------------------------------------------
# Run Script for security-constrained economic dispatch (SCED)
# Author: Xingpeng Li
# Email: xplipower@gmail.com 
# How to run: go to the program directory, and type down the below command
# Simple command: python RunSCED_RealCaseModel.py
# Command with redirect: python RunSCED_RealCaseModel.py > fileName.txt
# -----------------------------------------------------------------------------
# Command (Abandoned): pyomo solve –-solver=glpk RunSCED_RealCaseModel.py (solver specified here does not matter)
# it is quite interesting that it would work if you type the commands while
# it refuse to work if copy and paste...
# -----------------------------------------------------------------------------

import Diary
import ParamManager
import GeneralFunctions
import LoadInitFiles

from pyomo.environ import *
from pyomo.opt import SolverFactory
from SCEDRealCaseModel import model as SCEDModel

myDiary = Diary.Diary()
paramManager = ParamManager.ParamManager('configure.txt', myDiary)
isRunSCED = paramManager.getIsRunSCED()
isPyomoDataFilesAvailable = paramManager.getIsPyomoDataFilesAvailable()
generatePyomoDataFiles = paramManager.getGeneratePyomoDataFiles()
myDiary.hotlineWithLogType(7, "The real-case data file directory is: " + paramManager.getPathRealCase())

## Input pyomo file name
DatafileED = paramManager.getPyomoDataFormatInputFileRC()

isCodeWriteFiles = False
isCodeGeneratePyomoFiles = False
if isRunSCED == True:
    myDiary.hotline("The program will run the SCED simulation")
    if isPyomoDataFilesAvailable == True:
        myDiary.hotline("The program will first load the available pyomo-format based data files")
    else:
        isCodeWriteFiles = True
        isCodeGeneratePyomoFiles = True
        myDiary.hotline("The program will first generate the needed pyomo-format based data files")
else:
    myDiary.hotline("The program will NOT run the SCED simulation")
    isCodeWriteFiles = True
    if generatePyomoDataFiles == True:
        isCodeGeneratePyomoFiles = True
        myDiary.hotline("The program will only generate the needed pyomo-format based data files")
    else:
        myDiary.hotline("The program will only generate the regular-format based data files")

if isCodeWriteFiles == True:
    myDiary.hotline("Start to read needed data from raw file")
    pf = open(paramManager.getPathToRawFileNameRC(), "r")
    GeneralFunctions.skipNLines(pf, 3)
    buses = LoadInitFiles.loadBuses(pf, myDiary)
    loads = LoadInitFiles.loadLoads(pf, myDiary)
    gens = LoadInitFiles.loadGens(pf, myDiary)
    branches = LoadInitFiles.loadBranches(pf, myDiary)
    pf.close()
    myDiary.hotline("Finish reading needed data from raw file")

    fileFlowgate = open(paramManager.getPathToInterfaceFileNameRC(), "r")
    GeneralFunctions.skipNLines(fileFlowgate, 3)
    flowgates = LoadInitFiles.readPD_Interface(fileFlowgate, myDiary)
    fileFlowgate.close()

    fileAOL = open(paramManager.getPathToAolFileNameRC(), "r")
    aolDFAX = LoadInitFiles.readAOL(fileAOL, myDiary)
    fileAOL.close()

    import csv
    fileReserveReq = open(paramManager.getPathToReserveReqFileNameRC(), "r")
    csvReserveReq = csv.reader(fileReserveReq)
    reserveReq = LoadInitFiles.readReserveReq(csvReserveReq, myDiary)
    fileReserveReq.close()

    fileBidData = open(paramManager.getPathToBidFileNameRC(), "r")
    csvBidData = csv.reader(fileBidData)
    bidData = LoadInitFiles.readBidData(csvBidData, myDiary)
    fileReserveReq.close()

    fileHourlyData = open(paramManager.getPathToHourlyDataFileNameRC(), "r")
    csvHourlyData = csv.reader(fileHourlyData)
    hourlyData = LoadInitFiles.readHourlyData(csvHourlyData, myDiary)
    fileHourlyData.close()

    fileScheduleStatus = open(paramManager.getPathToRtUnitStatusFileNameRC(), "r")
    csvScheduleStatus = csv.reader(fileScheduleStatus)
    scheduleStatus = LoadInitFiles.readScheduleStatus(csvScheduleStatus, myDiary)
    fileScheduleStatus.close()

    fileCostCurve = open(paramManager.getPathToCostCurveRampFileNameRC(), "r")
    csvCostCurve = csv.reader(fileCostCurve)
    costCurve = LoadInitFiles.readCostCurve(csvCostCurve, myDiary)
    fileCostCurve.close()

    fileUnits = open(paramManager.getPathToUnitFileNameRC(), "r")
    csvUnits = csv.reader(fileUnits)
    units = LoadInitFiles.readUnits(csvUnits, myDiary)
    fileUnits.close()
    myDiary.hotlineWithLogType(5, "All EMS-Market model data have been loaded")

    import RawEMSMarketModel
    emsMarketModel = RawEMSMarketModel.EMSMarketModel(buses, loads, gens, branches, flowgates, aolDFAX, \
                            reserveReq, bidData, hourlyData, scheduleStatus, costCurve)
    emsMarketModel.setUnits(units)
    emsMarketModel.setDate(paramManager.getDate())
    emsMarketModel.setTime(paramManager.getTime())
    emsMarketModel.setIdxPeriod(paramManager.getIdxPeriod())

    import GeneratePyomoDataFiles
    dataWriter = GeneratePyomoDataFiles.generatePyomoFiles(isCodeGeneratePyomoFiles, myDiary)
    dataWriter.setRealCaseModel(emsMarketModel)
    dataWriter.setFileNamePyomoRC(paramManager.getPyomoDataFormatInputFileRC())
    dataWriter.setNeedHeading(paramManager.getNeedHeading())
    dataWriter.setIsPositivePgPmaxPminNeeded(paramManager.getIsPositivePgPmaxPminNeeded())
    dataWriter.setBlockPrice(paramManager.getBlockPrice())
    dataWriter.writeAllDataRC()
    if isCodeGeneratePyomoFiles == True:
        DatafileED = dataWriter.getFileNamePyomoRC()

if isRunSCED == True:
    myDiary.hotlineWithLogType(7, "The name of the case data file loaded is: " + DatafileED)
    myDiary.hotlineWithLogType(5, "Start to load input data for pyomo simulation")
    print "Start to load original input data for pyomo simulation"
    instanceSCED = SCEDModel.create_instance(DatafileED)
    myDiary.hotlineWithLogType(5, "Finish loading input data for pyomo simulation - an instance has been created")
    print "Finished loading original input data for pyomo simulation"
    
    # Data check and auto fix preprocess
    autoFixData = True
    if autoFixData == True:
        for idx in instanceSCED.GenCost_segmentBreadth.index_set():
            if value(instanceSCED.GenCost_segmentBreadth[idx]) < 0:
                instanceSCED.GenCost_segmentBreadth[idx] = 0
                myDiary.hotlineWithLogType(1, "For GenCost segment input data item with index of "+str(idx)+ ", the segment breadth is negative, so it is set to 0")

    handle_CostCurveSegment_Pgmin = paramManager.getHandle_CostCurveSegment_Pgmin()
    if handle_CostCurveSegment_Pgmin == True:
        PgmaxTemp_fromCostCurve = {}
        for idx in instanceSCED.GenCost_genIdx.index_set():
            idxGen = value(instanceSCED.GenCost_genIdx[idx])
            if PgmaxTemp_fromCostCurve.has_key(idxGen) == True:
                PgmaxTemp_fromCostCurve[idxGen] = PgmaxTemp_fromCostCurve[idxGen] + value(instanceSCED.GenCost_segmentBreadth[idx])
            else:
                PgmaxTemp_fromCostCurve[idxGen] = value(instanceSCED.GenCost_segmentBreadth[idx])
        for idxGen, Pgmax_fromCostCurve in PgmaxTemp_fromCostCurve.items():
            if value(instanceSCED.Gen_pgMin[idxGen]) > Pgmax_fromCostCurve:
                instanceSCED.Gen_pgMin[idxGen] = Pgmax_fromCostCurve
                myDiary.hotlineWithLogType(1, "The Pgmin of generator with index "+str(idxGen)+ " is inconsistent with the cost curve, so it is set to " + str(Pgmax_fromCostCurve))

    if autoFixData == True:
        isPositivePgPmaxPminNeeded = paramManager.getIsPositivePgPmaxPminNeeded()
        for idx in instanceSCED.Gen_pgInit.index_set():
            if value(instanceSCED.Gen_isInSvc[idx]) == 0:
                instanceSCED.Gen_pgInit[idx] = 0
            elif value(instanceSCED.Gen_pgMax[idx]) < value(instanceSCED.Gen_pgMin[idx]):
                instanceSCED.Gen_pgInit[idx] = (value(instanceSCED.Gen_pgMin[idx]) + value(instanceSCED.Gen_pgMax[idx]))/2
                instanceSCED.Gen_pgMin[idx] = value(instanceSCED.Gen_pgInit[idx])
                instanceSCED.Gen_pgMax[idx] = value(instanceSCED.Gen_pgInit[idx])
                myDiary.hotlineWithLogType(1, "For online generator "+str(idx)+" Pgmax < Pgmin, thus, they are set to (Pgmax+Pgmin)/2, as well as Pginit")
            elif value(instanceSCED.Gen_pgInit[idx]) < value(instanceSCED.Gen_pgMin[idx]):
                instanceSCED.Gen_pgInit[idx] = value(instanceSCED.Gen_pgMin[idx])
                myDiary.hotlineWithLogType(1, "For online generator "+str(idx)+" Gen_pgInit < Pgmin, thus, Gen_pgInit = Pgmin")
            elif value(instanceSCED.Gen_pgInit[idx]) > value(instanceSCED.Gen_pgMax[idx]):
                instanceSCED.Gen_pgInit[idx] = value(instanceSCED.Gen_pgMax[idx])
                myDiary.hotlineWithLogType(1, "For online generator "+str(idx)+" Gen_pgInit > Pgmax, thus, Gen_pgInit = Pgmax")
            if value(instanceSCED.Gen_energyRamp[idx]) < 0:
                instanceSCED.Gen_energyRamp[idx] = 0
                myDiary.hotlineWithLogType(1, "For generator "+str(idx)+" Gen_energyRamp is negative, thus, Gen_energyRamp = 0")
            if value(instanceSCED.Gen_spinRamp[idx]) < 0:
                instanceSCED.Gen_spinRamp[idx] = 0
                myDiary.hotlineWithLogType(1, "For generator "+str(idx)+" Gen_spinRamp is negative, thus, Gen_spinRamp = 0")
            if value(instanceSCED.Gen_regOfferMW[idx]) < 0:
                instanceSCED.Gen_regOfferMW[idx] = 0
                myDiary.hotlineWithLogType(1, "For generator "+str(idx)+" Gen_regOfferMW is negative, thus, Gen_regOfferMW = 0")
            if value(instanceSCED.Gen_spinOfferMW[idx]) < 0:
                instanceSCED.Gen_spinOfferMW[idx] = 0
                myDiary.hotlineWithLogType(1, "For generator "+str(idx)+" Gen_spinOfferMW is negative, thus, Gen_spinOfferMW = 0")
            if value(instanceSCED.Gen_coldNotificationTime[idx]) < 0:
                instanceSCED.Gen_coldNotificationTime[idx] = 0
                myDiary.hotlineWithLogType(1, "For generator "+str(idx)+" Gen_coldNotificationTime is negative, thus, Gen_coldNotificationTime = 0")
            if value(instanceSCED.Gen_coldStartupTime[idx]) < 0:
                instanceSCED.Gen_coldStartupTime[idx] = 0
                myDiary.hotlineWithLogType(1, "For generator "+str(idx)+" Gen_coldStartupTime is negative, thus, Gen_coldStartupTime = 0")
            if isPositivePgPmaxPminNeeded == True:
                if value(instanceSCED.Gen_pgMax[idx]) < 0:
                    instanceSCED.Gen_pgMax[idx] = 0
                    myDiary.hotlineWithLogType(1, "For generator "+str(idx)+" Gen_pgMax is negative, thus, Gen_pgMax = 0")
                if value(instanceSCED.Gen_pgMin[idx]) < 0:
                    instanceSCED.Gen_pgMin[idx] = 0
                    myDiary.hotlineWithLogType(1, "For generator "+str(idx)+" Gen_pgMin is negative, thus, Gen_pgMin = 0")
                if value(instanceSCED.Gen_pgInit[idx]) < 0:
                    instanceSCED.Gen_pgInit[idx] = 0
                    myDiary.hotlineWithLogType(1, "For generator "+str(idx)+" Gen_pgInit is negative, thus, Gen_pgMin = 0")

## ------ The following block of code may fix the data inconsistency between Pgmax and segment
#    if autoFixData == True:
#        PgmaxTemp = []
#        for idx in instanceSCED.Gen_pgMax.index_set():
#            PgmaxTemp.append(value(instanceSCED.Gen_pgMax[idx]))
#        for idx in instanceSCED.GenCost_genIdx.index_set():
#            idxGen = value(instanceSCED.GenCost_genIdx[idx]) - 1
#            if value(instanceSCED.GenCost_segmentBreadth[idx]) <= PgmaxTemp[idxGen]:
#                PgmaxTemp[idxGen] = PgmaxTemp[idxGen] - value(instanceSCED.GenCost_segmentBreadth[idx])
#            else:
#                instanceSCED.GenCost_segmentBreadth[idx] = PgmaxTemp[idxGen]
#                myDiary.hotlineWithLogType(1, "Generator "+str(idxGen+1)+"'s "+str(instanceSCED.GenCost_segmentIdx[idx]) \
#                                        + " breadth is set to "+str(PgmaxTemp[idxGen])+" due to a violation with Pgmax")
#                PgmaxTemp[idxGen] = 0
            
    baseMVA = 100  # in the objective function in the model.py code, manual change is needed if this number is not 100.
    for idx in instanceSCED.Load_pd.index_set():
        instanceSCED.Load_pd[idx] = value(instanceSCED.Load_pd[idx])/baseMVA
    for idx in instanceSCED.Gen_pgInit.index_set():
        instanceSCED.Gen_pgInit[idx] = value(instanceSCED.Gen_pgInit[idx])/baseMVA
        instanceSCED.Gen_pgMax[idx] = value(instanceSCED.Gen_pgMax[idx])/baseMVA
        instanceSCED.Gen_pgMin[idx] = value(instanceSCED.Gen_pgMin[idx])/baseMVA
        instanceSCED.Gen_energyRamp[idx] = value(instanceSCED.Gen_energyRamp[idx])/baseMVA
        instanceSCED.Gen_spinRamp[idx] = value(instanceSCED.Gen_spinRamp[idx])/baseMVA
        instanceSCED.Gen_regOfferMW[idx] = value(instanceSCED.Gen_regOfferMW[idx])/baseMVA
        instanceSCED.Gen_spinOfferMW[idx] = value(instanceSCED.Gen_spinOfferMW[idx])/baseMVA
    for idx in instanceSCED.GenCost_segmentBreadth.index_set():
        instanceSCED.GenCost_segmentBreadth[idx] = value(instanceSCED.GenCost_segmentBreadth[idx])/baseMVA
    for idx in instanceSCED.Branch_pkInit.index_set():
        instanceSCED.Branch_pkInit[idx] = value(instanceSCED.Branch_pkInit[idx])/baseMVA
        instanceSCED.Branch_rateA[idx] = value(instanceSCED.Branch_rateA[idx])/baseMVA
        instanceSCED.Branch_rateB[idx] = value(instanceSCED.Branch_rateB[idx])/baseMVA
        instanceSCED.Branch_rateC[idx] = value(instanceSCED.Branch_rateC[idx])/baseMVA
    for idx in instanceSCED.Constraint_monitorBranchLimit.index_set():
        instanceSCED.Constraint_monitorBranchLimit[idx] = value(instanceSCED.Constraint_monitorBranchLimit[idx])/baseMVA
    for idx in instanceSCED.ReserveArea_regulationReq.index_set():
        instanceSCED.ReserveArea_regulationReq[idx] = value(instanceSCED.ReserveArea_regulationReq[idx])/baseMVA
        instanceSCED.ReserveArea_spinReq[idx] = value(instanceSCED.ReserveArea_spinReq[idx])/baseMVA
        instanceSCED.ReserveArea_primaryReq[idx] = value(instanceSCED.ReserveArea_primaryReq[idx])/baseMVA
    for idx in instanceSCED.Interface_totalLimit.index_set():
        instanceSCED.Interface_totalLimit[idx] = value(instanceSCED.Interface_totalLimit[idx])/baseMVA
   
    # some statistics information
    TotalLoad = 0
    for idx in instanceSCED.Load_pd.index_set():
        if instanceSCED.Load_isInSvc[idx] == 1:
            TotalLoad = TotalLoad + value(instanceSCED.Load_pd[idx])
    myDiary.hotlineWithLogType(6, "The total load for this case is: " + str(TotalLoad*baseMVA) + " MW")
    
    TotalGenInit = 0
    for idx in instanceSCED.Gen_pgInit.index_set():
        if instanceSCED.Gen_isInSvc[idx] == 1:
            TotalGenInit = TotalGenInit + value(instanceSCED.Gen_pgInit[idx])
    myDiary.hotlineWithLogType(6, "The total generation for this case is: " + str(TotalGenInit*baseMVA) + " MW")

    TotalGenMax = 0
    for idx in instanceSCED.Gen_pgMax.index_set():
        if instanceSCED.Gen_isInSvc[idx] == 1:
            TotalGenMax = TotalGenMax + value(instanceSCED.Gen_pgMax[idx])
    myDiary.hotlineWithLogType(6, "The total online generation capacity is: " + str(TotalGenMax*baseMVA) + " MW")
    
    TotalGenMax = 0
    for idx in instanceSCED.Gen_pgMax.index_set():
        if instanceSCED.Gen_isInSvc[idx] == 1:
            if instanceSCED.Gen_hasMarketData[idx] == 1:
                TotalGenMax = TotalGenMax + value(instanceSCED.Gen_pgMax[idx])
    myDiary.hotlineWithLogType(6, "The total capacity of online generators that have cost curve available is: " + str(TotalGenMax*baseMVA) + " MW")
    
    TotalGenMax = 0
    for idx in instanceSCED.Gen_pgMax.index_set():
        if instanceSCED.Gen_isInSvc[idx] == 1:
            if instanceSCED.Gen_hasMarketData[idx] == 1:
                TotalGenMax = TotalGenMax + value(instanceSCED.Gen_pgMax[idx])
            else:
                TotalGenMax = TotalGenMax + value(instanceSCED.Gen_pgInit[idx])
    myDiary.hotlineWithLogType(6, "The total availabe capacity of online generators is: " + str(TotalGenMax*baseMVA) + " MW")
    
    # the following adjustment may be needed for a lossy power flow model
    ratioGenLoad = TotalGenInit/TotalLoad
    for idx in instanceSCED.Load_pd.index_set():
        instanceSCED.Load_pd[idx] = value(instanceSCED.Load_pd[idx])*ratioGenLoad
    myDiary.hotlineWithLogType(6, "To consider loss, each load is increased by : " + str(ratioGenLoad*100-100) + "%")

#    for idx in instanceSCED.GEN:
#        instanceSCED.genEnergyRampConst[idx].deactivate()

    print "Finished input data auto-adjustment process for pyomo simulation"
    instanceSCED.preprocess()
    #instanceSCED.pprint()

    # Create a solver
    opt = SolverFactory(paramManager.getSolverName())
    opt.options.tmlim = paramManager.getSolverTimLimit() # tmlim is for glpk
    opt.options.mipgap = paramManager.getSolverOptGap()
    myDiary.hotlineWithLogType(0, "The solver used is: " + paramManager.getSolverName())
    myDiary.hotlineWithLogType(0, "The solver time limit is: " + paramManager.getSolverTimLimit() + " seconds")
    myDiary.hotlineWithLogType(0, "The solver optimization gap is: " + paramManager.getSolverOptGap())

    # Create a model instance and optimize
    myDiary.hotlineWithLogType(5, "Start to solve pyomo case")
    results = opt.solve(instanceSCED, suffixes=['rc','dual'],tee=True)
    #results = opt.solve(instanceSCED, load_solutions=False)
    myDiary.hotlineWithLogType(5, "Finish solving pyomo case")

    myDiary.hotlineWithLogType(6, "results.Solution.Status: " + str(results.Solution.Status))
    myDiary.hotlineWithLogType(6, "results.solver.status: " + str(results.solver.status))
    myDiary.hotlineWithLogType(6, "results.solver.termination_condition: " + str(results.solver.termination_condition))
    myDiary.hotlineWithLogType(6, "results.solver.termination_message: " + str(results.solver.termination_message))
    
    print "\nresults.Solution.Status: ", results.Solution.Status
    print "Solver status:", results.solver.status
    print "Solver Termination Condition:", results.solver.termination_condition
    print "Solver Termination message :", results.solver.termination_message
    #instanceSCED.display()  # all results will be shown, if we need all of them, we'd better redirect them to a file.

    import os
    fileNameTmp = "genDataRC_Actually.txt"
    if os.path.isfile(fileNameTmp):
        os.remove(fileNameTmp)
        myDiary.hotlineWithLogType(0, "The original file "+fileNameTmp + "has been deleted")
    with open(fileNameTmp, 'a') as fileTmp:
        heading = " Index PgInSvc Pg_init Pgmax Pgmin EnergyRamp SpinRamp HasCostCurveData Gen_fastStartUnitFlag"
        heading = heading + "\n"
        fileTmp.write(heading)
        for g in instanceSCED.GEN:
            fileTmp.write("%s %d" % (" ", g))
            fileTmp.write("%s %d" % (" ", instanceSCED.Gen_isInSvc[g]))
            fileTmp.write("%s %f" % (" ", value(instanceSCED.Gen_pgInit[g]*baseMVA)))
            fileTmp.write("%s %f" % (" ", value(instanceSCED.Gen_pgMax[g]*baseMVA)))
            fileTmp.write("%s %f" % (" ", value(instanceSCED.Gen_pgMin[g]*baseMVA)))
            fileTmp.write("%s %f" % (" ", value(instanceSCED.Gen_energyRamp[g]*baseMVA)))
            fileTmp.write("%s %f" % (" ", value(instanceSCED.Gen_spinRamp[g]*baseMVA)))
            fileTmp.write("%s %d" % (" ", instanceSCED.Gen_hasMarketData[g]))
            fileTmp.write("%s %d" % (" ", instanceSCED.Gen_fastStartUnitFlag[g]))
            fileTmp.write("%s" % ("\n"))
    myDiary.hotlineWithLogType(0, "File "+fileNameTmp + "has been created successfully")

    import WriteResults
    fileName = "resultsRC"
    isDataForRC = True
    WriteResults.Write_GenInfo(instanceSCED, fileName, isDataForRC, myDiary)

myDiary.close()

