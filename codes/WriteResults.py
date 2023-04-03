"""
Created in 2016

@author: Xingpeng Li (xplipower@gmail.com)
"""

from pyomo.environ import *
import os

def Write_GenInfo(instance, fileName, isDataForRC, myDiary):
    fileNameSummary = fileName + "_summary.txt"
    deleteOldFiles(fileNameSummary, myDiary)
    with open(fileNameSummary, 'a') as fileSummary:
        myDiary.hotline("A new file " + fileNameSummary + " has been created")        
        fileSummary.write("****************** Summary ******************\n")
        fileSummary.write("Objective value is:  %s\n" % (value(instance.minimizeCost)))
        fileSummary.write("\n################## The following info is mainly for violations ##############\n")
        if isDataForRC == True:
            fileSummary.write("\n**************** Constraint ***********\n")
            countNum = 0
            for k in instance.CONSTRAINT:
                if instance.brcFlowLimitSlackVar[k].value > 0:
                    countNum = countNum + 1
                    fileSummary.write("The flow on branch "+str(instance.Constraint_monitorBranchIdx[k])+" under contingency " \
                                        + str(instance.Constraint_contingencyIdx[k]) + " is overloaded by " + str(instance.brcFlowLimitSlackVar[k].value*instance.BaseMVA) \
                                        + " MW; its limit is: "+ str(value(instance.Constraint_monitorBranchLimit[k]*instance.BaseMVA))+" MW\n")
            fileSummary.write("In total, there are "+str(countNum)+ " branches that are overloaded\n")
            
            fileSummary.write("\n**************** Interface ***********\n")
            countNum = 0
            for k in instance.INTERFACE:
                if instance.interfaceLimiteSlackVar[k].value > 0:
                    countNum = countNum + 1
                    fileSummary.write("The total flow of interface "+str(k) + " is violated by " \
                                        + str(instance.interfaceLimiteSlackVar[k].value*instance.BaseMVA) + " MW, and the limit is: " \
                                        + str(value(instance.Interface_totalLimit[k]*instance.BaseMVA))+" MW\n")
            fileSummary.write("In total, there are "+str(countNum)+ " interfaces that are violated\n")
            
            fileSummary.write("\n**************** Generator ***********\n")
            totalRegulationReserveShortage = 0.0
            totalSpinReserveShortage = 0.0
            totalPrimaryReserveShortage = 0.0
            for g in instance.GEN:
                if instance.rrSlackVar[g].value > 0:
                    totalRegulationReserveShortage = totalRegulationReserveShortage + instance.rrSlackVar[g].value
                    fileSummary.write("Regulation reserve shortage of generator "+str(g)+" is " + str(instance.rrSlackVar[g].value*instance.BaseMVA) + " MW\n")
                if instance.srSlackVar[g].value > 0:
                    totalSpinReserveShortage = totalSpinReserveShortage + instance.srSlackVar[g].value
                    fileSummary.write("Spinning reserve shortage of generator "+str(g)+" is " + str(instance.srSlackVar[g].value*instance.BaseMVA) + " MW\n")
                if instance.prSlackVar[g].value > 0:
                    totalPrimaryReserveShortage = totalPrimaryReserveShortage + instance.prSlackVar[g].value
                    fileSummary.write("Primary reserve shortage of generator "+str(g)+" is " + str(instance.prSlackVar[g].value*instance.BaseMVA) + " MW\n")
                if instance.pgmaxSlackVar[g].value > 0:
                    fileSummary.write("Pg Max limit of generator "+str(g)+" is violated by " + str(instance.pgmaxSlackVar[g].value*instance.BaseMVA) + " MW\n")
                if instance.pgminSlackVar[g].value > 0:
                    fileSummary.write("Pg Min limit of generator "+str(g)+" is violated by " + str(instance.pgminSlackVar[g].value*instance.BaseMVA) + " MW\n")
                if instance.energyRampUpSlackVar[g].value > 0:
                    fileSummary.write("Energy ramp-up limit of generator "+str(g)+" is violated by " + str(instance.energyRampUpSlackVar[g].value*instance.BaseMVA) + " MW\n")
                if instance.energyRampDownSlackVar[g].value > 0:
                    fileSummary.write("Energy ramp-down limit of generator "+str(g)+" is violated by " + str(instance.energyRampDownSlackVar[g].value*instance.BaseMVA) + " MW\n")
                if instance.Gen_regOfferMWSlackVar[g].value > 0:
                    fileSummary.write("Regulation reserve offer MW limit of generator "+str(g)+" is violated by " + str(instance.Gen_regOfferMWSlackVar[g].value*instance.BaseMVA) + " MW\n")
                if instance.Gen_spinOfferMWSlackVar[g].value > 0:
                    fileSummary.write("Spinning reserve offer MW limit of generator "+str(g)+" is violated by " + str(instance.Gen_spinOfferMWSlackVar[g].value*instance.BaseMVA) + " MW\n")
            fileSummary.write("\nThe total regulation reserve shortage is "+str(totalRegulationReserveShortage*instance.BaseMVA)+" MW\n")
            fileSummary.write("The total spinning reserve shortage is "+str(totalSpinReserveShortage*instance.BaseMVA)+" MW\n")
            fileSummary.write("The total primary reserve shortage is "+str(totalPrimaryReserveShortage*instance.BaseMVA)+" MW\n\n")
            for g in instance.GEN:
                for c in instance.SCENARIO:
                    if instance.spinRampUpSlackVar[g, c].value > 0:
                        fileSummary.write("For scenario "+str(c)+" Spin ramp up limit of generator "+str(g)+" is violated by " + str(instance.spinRampUpSlackVar[g, c].value*instance.BaseMVA) + " MW\n")
                    if instance.spinRampDownSlackVar[g, c].value > 0:
                        fileSummary.write("For scenario "+str(c)+" Spin ramp down limit of generator "+str(g)+" is violated by " + str(instance.spinRampDownSlackVar[g, c].value*instance.BaseMVA) + " MW\n")
                        
            fileSummary.write("\n**************** Reserve Area ***********\n")
            for idxArea in instance.RESERVEArea:
                if instance.rrReqSlackVar[idxArea].value > 0:
                    fileSummary.write("Regulation reserve requirement of area "+str(instance.ReserveArea_genArea[idxArea])+" is violated by " + str(instance.rrReqSlackVar[idxArea].value*instance.BaseMVA) + " MW\n")
                if instance.srReqSlackVar[idxArea].value > 0:
                    fileSummary.write("Spinning reserve requirement of area "+str(instance.ReserveArea_genArea[idxArea])+" is violated by " + str(instance.srReqSlackVar[idxArea].value*instance.BaseMVA) + " MW\n")
                if instance.prReqSlackVar[idxArea].value > 0:
                    fileSummary.write("Primary reserve requirement of area "+str(instance.ReserveArea_genArea[idxArea])+" is violated by " + str(instance.prReqSlackVar[idxArea].value*instance.BaseMVA) + " MW\n")
        else:
            fileSummary.write("\n**************** Branch ***********\n")
            countNum = 0
            for k in instance.BRANCH:
                if instance.brcFlowLimitSlackVar[k].value > 0:
                    countNum = countNum + 1
                    fileSummary.write("The flow on branch "+str(k)+" is overloaded by " + str(instance.brcFlowLimitSlackVar[k].value*instance.BaseMVA) + " MW; its rateA is: "+ str(value(instance.Branch_rateA[k]*instance.BaseMVA))+" MW\n")
            fileSummary.write("There are total "+str(countNum)+ " branches that are overloaded\n\n")

            countNum = 0
            for k in instance.INTERFACE:
                if instance.interfaceLimiteSlackVar[k].value > 0:
                    countNum = countNum + 1
                    fileSummary.write("The total flow of interface "+str(k)+" is overloaded by " + str(instance.interfaceLimiteSlackVar[k].value*instance.BaseMVA) + " MW; its limit is: "+ str(value(instance.Interface_totalLimit[k]*instance.BaseMVA))+" MW\n")
            fileSummary.write("In total, there are "+str(countNum)+ " interface that are overloaded\n")

            fileSummary.write("\n**************** Generator ***********\n")
            totalReserveShortage = 0.0
            for g in instance.GEN:
                if instance.srReqSlackVar[g].value > 0:
                    totalReserveShortage = totalReserveShortage + instance.srReqSlackVar[g].value
                    fileSummary.write("Reserve shortage of generator "+str(g)+" is " + str(instance.srReqSlackVar[g].value*instance.BaseMVA) + " MW\n")
                if instance.pgmaxSlackVar[g].value > 0:
                    fileSummary.write("Pg Max limit of generator "+str(g)+" is violated by " + str(instance.pgmaxSlackVar[g].value*instance.BaseMVA) + " MW\n")
                if instance.pgminSlackVar[g].value > 0:
                    fileSummary.write("Pg Min limit of generator "+str(g)+" is violated by " + str(instance.pgminSlackVar[g].value*instance.BaseMVA) + " MW\n")
                if instance.energyRampUpSlackVar[g].value > 0:
                    fileSummary.write("Energy ramp-up limit of generator "+str(g)+" is violated by " + str(instance.energyRampUpSlackVar[g].value*instance.BaseMVA) + " MW\n")
                if instance.energyRampDownSlackVar[g].value > 0:
                    fileSummary.write("Energy ramp-down limit of generator "+str(g)+" is violated by " + str(instance.energyRampDownSlackVar[g].value*instance.BaseMVA) + " MW\n")
                if instance.spinRampSlackVar[g].value > 0:
                    fileSummary.write("Spin ramp limit of generator "+str(g)+" is violated by " + str(instance.spinRampSlackVar[g].value*instance.BaseMVA) + " MW\n")
            fileSummary.write("The total spinning reserve shortage is "+str(totalReserveShortage*instance.BaseMVA)+" MW\n")
            
            fileSummary.write("\n*************** Load ************\n")
            totalLoadShed = 0.0
            for d in instance.LOAD:
                if instance.loadShed[d].value > 0:
                    totalLoadShed = totalLoadShed + instance.loadShed[d].value
                    fileSummary.write("The load amount shedded from load "+str(d)+" is " + str(instance.loadShed[d].value*instance.BaseMVA) + " MW\n")
            fileSummary.write("The total shedded load is "+str(totalLoadShed*instance.BaseMVA)+" MW\n")

            fileSummary.write("\n*************** Contingency ************\n")
            for c in instance.CONTINGENCY:
                if instance.Contingency_isEnabled[c] == 0:
                    continue
                
                totalLoadShed_c = 0.0
                for d in instance.LOAD:
                    if instance.loadShed_c[c, d].value > 0:
                        totalLoadShed_c = totalLoadShed_c + instance.loadShed_c[c, d].value
                        fileSummary.write("Contingency " + str(c) + ", the load amount shedded from load "+str(d)+" is " + str(instance.loadShed_c[c, d].value*instance.BaseMVA) + " MW\n")
                fileSummary.write("Contingency " + str(c) + ", the total shedded load is "+str(totalLoadShed_c*instance.BaseMVA)+" MW\n")
                
                countNum = 0
                for k in instance.INTERFACE:
                    if instance.interfaceLimiteSlackVar[k].value > 0:
                        countNum = countNum + 1
                        fileSummary.write("Contingency " + str(c) + ", the total flow of interface "+str(k)+" is overloaded by " + str(instance.interfaceLimiteSlackVar[k].value*instance.BaseMVA) + " MW; its limit is: "+ str(value(instance.Interface_totalLimit[k]*instance.BaseMVA))+" MW\n")
                fileSummary.write("Contingency " + str(c) + ", in total, there are "+str(countNum)+ " interface that are overloaded\n\n")

    fileNameGen = fileName + "_gen.txt"
    deleteOldFiles(fileNameGen, myDiary)
    with open(fileNameGen, 'a') as fileGen:
        myDiary.hotline("A new file " + fileNameGen + " has been created")
        fileGen.write("****************** Generator ******************\n")
        heading = " Index PgInSvc Pg_init Pgmax Pgmin Pg sr"
        if isDataForRC == True:
            heading = heading + " rr pr hasMarketData pgmax_slack pgmin_slack rrSlackVar srSlackVar prSlackVar"
            heading = heading + " energyRampUp_Slack energyRampDown_Slack regOfferMWSlackVar spinOfferMWSlackVar"
        else:
            heading = heading + " hasCostCurvData srReq_slack pgmax_slack pgmin_slack energyRampUp_Slack energyRampDown_Slack spinRampSlack"
        heading = heading + "\n"
        fileGen.write(heading)
        for g in instance.GEN:
            fileGen.write("%s %d" % (" ", g))
            fileGen.write("%s %d" % (" ", instance.Gen_isInSvc[g]))
            fileGen.write("%s %s" % (" ", value(instance.Gen_pgInit[g]*instance.BaseMVA)))
            fileGen.write("%s %s" % (" ", value(instance.Gen_pgMax[g]*instance.BaseMVA)))
            fileGen.write("%s %s" % (" ", value(instance.Gen_pgMin[g]*instance.BaseMVA)))
            fileGen.write("%s %f" % (" ", instance.pg[g].value*instance.BaseMVA))
            fileGen.write("%s %f" % (" ", instance.sr[g].value*instance.BaseMVA))
            if isDataForRC == True:
                fileGen.write("%s %f" % (" ", instance.rr[g].value*instance.BaseMVA))
                fileGen.write("%s %f" % (" ", instance.pr[g].value*instance.BaseMVA))
                fileGen.write("%s %d" % (" ", instance.Gen_hasMarketData[g]))
                fileGen.write("%s %f" % (" ", instance.pgmaxSlackVar[g].value*instance.BaseMVA))
                fileGen.write("%s %f" % (" ", instance.pgminSlackVar[g].value*instance.BaseMVA))
                fileGen.write("%s %f" % (" ", instance.rrSlackVar[g].value*instance.BaseMVA))
                fileGen.write("%s %f" % (" ", instance.srSlackVar[g].value*instance.BaseMVA))
                fileGen.write("%s %f" % (" ", instance.prSlackVar[g].value*instance.BaseMVA))
                fileGen.write("%s %f" % (" ", instance.energyRampUpSlackVar[g].value*instance.BaseMVA))
                fileGen.write("%s %f" % (" ", instance.energyRampDownSlackVar[g].value*instance.BaseMVA))
                fileGen.write("%s %f" % (" ", instance.Gen_regOfferMWSlackVar[g].value*instance.BaseMVA))
                fileGen.write("%s %f" % (" ", instance.Gen_spinOfferMWSlackVar[g].value*instance.BaseMVA))
            else:
                fileGen.write("%s %d" % (" ", instance.Gen_costCurveFlag[g]))
                fileGen.write("%s %f" % (" ", instance.srReqSlackVar[g].value*instance.BaseMVA))
                fileGen.write("%s %f" % (" ", instance.pgmaxSlackVar[g].value*instance.BaseMVA))
                fileGen.write("%s %f" % (" ", instance.pgminSlackVar[g].value*instance.BaseMVA))
                fileGen.write("%s %f" % (" ", instance.energyRampUpSlackVar[g].value*instance.BaseMVA))
                fileGen.write("%s %f" % (" ", instance.energyRampDownSlackVar[g].value*instance.BaseMVA))
                fileGen.write("%s %f" % (" ", instance.spinRampSlackVar[g].value*instance.BaseMVA))
            fileGen.write("%s" % ("\n"))
    
    if isDataForRC == True:
        fileNameBranch = fileName + "_constraint.txt"
        deleteOldFiles(fileNameBranch, myDiary)
        with open(fileNameBranch, 'a') as fileBranch:
            myDiary.hotline("A new file " + fileNameBranch + " has been created")        
            fileBranch.write("****************** Constraint ******************\n")
            fileBranch.write(" index lineflow limit slackVar\n")
            for k in instance.CONSTRAINT:
                fileBranch.write("%s %d" % (" ", k))
                fileBranch.write("%s %f" % (" ", instance.pk[k].value*instance.BaseMVA))
                fileBranch.write("%s %f" % (" ", instance.Constraint_monitorBranchLimit[k].value*instance.BaseMVA))
                fileBranch.write("%s %f" % (" ", instance.brcFlowLimitSlackVar[k].value*instance.BaseMVA))
                fileBranch.write("%s" % ("\n"))

    fileNameInterface = fileName + "_interface.txt"
    deleteOldFiles(fileNameInterface, myDiary)
    with open(fileNameInterface, 'a') as fileInterface:
        myDiary.hotline("A new file " + fileNameInterface + " has been created")
        fileInterface.write("****************** Interface ******************\n")
        fileInterface.write(" index interfaceEnabled totalFlow interfacelimit slackVar\n")
        for i in instance.INTERFACE:
            fileInterface.write("%s %d" % (" ", i))
            fileInterface.write("%s %d" % (" ", instance.Interface_isEnabled[i]))
            fileInterface.write("%s %f" % (" ", instance.totalFlowForInterface[i].value*instance.BaseMVA))
            fileInterface.write("%s %f" % (" ", instance.Interface_totalLimit[i].value*instance.BaseMVA))
            fileInterface.write("%s %f" % (" ", instance.interfaceLimiteSlackVar[i].value*instance.BaseMVA))
            fileInterface.write("%s" % ("\n"))
        
    if isDataForRC == True:
        fileNameInterfaceLine = fileName + "_interfaceline.txt"
        deleteOldFiles(fileNameInterfaceLine, myDiary)
        with open(fileNameInterfaceLine, 'a') as fileInterfaceLine:
            myDiary.hotline("A new file " + fileNameInterfaceLine + " has been created")
            fileInterfaceLine.write("****************** InterfaceLine ******************\n")
            fileInterfaceLine.write(" index lineflow branchIndex interfaceIndex\n")
            for k in instance.INTERFACELINE:
                fileInterfaceLine.write("%s %d" % (" ", k))
                fileInterfaceLine.write("%s %f" % (" ", instance.pkForInterfaceLine[k].value*instance.BaseMVA))
                fileInterfaceLine.write("%s %d" % (" ", instance.Interfaceline_branchIdx[k]))
                fileInterfaceLine.write("%s %d" % (" ", instance.Interfaceline_interfaceIdx[k]))
                fileInterfaceLine.write("%s" % ("\n"))

    if isDataForRC == True:
        fileNamePgc = fileName + "_pgc.txt"
        deleteOldFiles(fileNamePgc, myDiary)
        with open(fileNamePgc, 'a') as filePgc:
            myDiary.hotline("A new file " + fileNamePgc + " has been created")        
            filePgc.write("****************** Pgc ******************\n")
            filePgc.write(" indexScenario indexGen pgc spinUpSlackVar spinDownSlackVar\n")
            for s in instance.SCENARIO:
                for g in instance.GEN:
                    filePgc.write("%s %d" % (" ", s))
                    filePgc.write("%s %d" % (" ", g))
                    filePgc.write("%s %f" % (" ", instance.pgc[g, s].value*instance.BaseMVA))
                    filePgc.write("%s %f" % (" ", instance.spinRampUpSlackVar[g, s].value*instance.BaseMVA))
                    filePgc.write("%s %f" % (" ", instance.spinRampDownSlackVar[g, s].value*instance.BaseMVA))
                    filePgc.write("%s" % ("\n"))

    if isDataForRC == False:
        fileNameBranch = fileName + "_branch.txt"
        deleteOldFiles(fileNameBranch, myDiary)
        with open(fileNameBranch, 'a') as fileBranch:
            myDiary.hotline("A new file " + fileNameBranch + " has been created")        
            fileBranch.write("****************** Branch ******************\n")
            fileBranch.write(" index lineflow rateA slackVar\n")
            for k in instance.BRANCH:
                fileBranch.write("%s %d" % (" ", k))
                fileBranch.write("%s %f" % (" ", instance.pk[k].value*instance.BaseMVA))
                fileBranch.write("%s %f" % (" ", instance.Branch_rateA[k].value*instance.BaseMVA))
                fileBranch.write("%s %f" % (" ", instance.brcFlowLimitSlackVar[k].value*instance.BaseMVA))
                fileBranch.write("%s" % ("\n"))
    
    if isDataForRC == False:
        fileNameBus = fileName + "_bus.txt"
        deleteOldFiles(fileNameBus, myDiary)
        with open(fileNameBus, 'a') as fileBus:
            myDiary.hotline("A new file " + fileNameBus + " has been created")
            fileBus.write("****************** Bus ******************\n")
            fileBus.write(" index busNumber busAngle\n")
            for n in instance.BUS:
                fileBus.write("%s %d" % (" ", n))
                fileBus.write("%s %d" % (" ", instance.Bus_number[n]))
                fileBus.write("%s %f" % (" ", instance.theta[n].value))
                fileBus.write("%s" % ("\n"))

    if isDataForRC == False:
        fileNameLoad = fileName + "_load.txt"
        deleteOldFiles(fileNameLoad, myDiary)
        with open(fileNameLoad, 'a') as fileLoad:
            myDiary.hotline("A new file " + fileNameLoad + " has been created")
            fileLoad.write("****************** Load ******************\n")
            fileLoad.write(" index loadBusNumber loadID load_IsInSvc Pload Pd_served Pd_shedded\n")
            for n in instance.LOAD:
                fileLoad.write("%s %d" % (" ", n))
                fileLoad.write("%s %d" % (" ", instance.Load_busNumber[n]))
                fileLoad.write("%s %s" % (" ", str(instance.Load_id[n])))
                fileLoad.write("%s %d" % (" ", instance.Load_isInSvc[n]))
                fileLoad.write("%s %f" % (" ", value(instance.Load_pd[n]*instance.BaseMVA)))
                fileLoad.write("%s %f" % (" ", instance.loadServed[n].value*instance.BaseMVA))
                fileLoad.write("%s %f" % (" ", instance.loadShed[n].value*instance.BaseMVA))
                fileLoad.write("%s" % ("\n"))

    if isDataForRC == False:
        fileNamePgc = fileName + "_contingencyPgc.txt"
        deleteOldFiles(fileNamePgc, myDiary)
        with open(fileNamePgc, 'a') as filePgc:
            myDiary.hotline("A new file " + fileNamePgc + " has been created")
            filePgc.write("****************** Generator ******************\n")
            filePgc.write(" indexCtgcy ctgcyValid genIdx gen_IsInSvc pgc \n")
            for c in instance.CONTINGENCY:
                if instance.Contingency_isEnabled[c] == 0:
                    continue
                #fileContingency.write("%s %d\n" % (" continegency scenario index ", c))
                for g in instance.GEN:
                    filePgc.write("%s %d" % (" ", c))
                    filePgc.write("%s %d" % (" ", instance.Contingency_isEnabled[c]))
                    filePgc.write("%s %d" % (" ", g))
                    filePgc.write("%s %d" % (" ", instance.Gen_isInSvc[g]))
                    filePgc.write("%s %f" % (" ", instance.pgc[g, c].value*instance.BaseMVA))
                    filePgc.write("%s" % ("\n"))

        fileNamePkc = fileName + "_contingencyPkc.txt"
        deleteOldFiles(fileNamePkc, myDiary)
        with open(fileNamePkc, 'a') as filePkc:
            myDiary.hotline("A new file " + fileNamePkc + " has been created")
            filePkc.write("****************** Branch ******************\n")
            filePkc.write(" indexCtgcy ctgcyValid brcIdx brc_IsInSvcOrig pkc rateC \n")
            for c in instance.CONTINGENCY:
                if instance.Contingency_isEnabled[c] == 0:
                    continue
                for k in instance.BRANCH:
                    filePkc.write("%s %d" % (" ", c))
                    filePkc.write("%s %d" % (" ", instance.Contingency_isEnabled[c]))
                    filePkc.write("%s %d" % (" ", k))
                    filePkc.write("%s %d" % (" ", instance.Branch_isInSvc[k]))
                    filePkc.write("%s %f" % (" ", instance.pkc[c, k].value*instance.BaseMVA))
                    filePkc.write("%s %f" % (" ", instance.Branch_rateC[k].value*instance.BaseMVA))
                    filePkc.write("%s" % ("\n"))

    fileNameGenCost = fileName + "_genCost.txt"
    deleteOldFiles(fileNameGenCost, myDiary)
    with open(fileNameGenCost, 'a') as fileGenCost:
        myDiary.hotline("A new file " + fileNameGenCost + " has been created")
        fileGenCost.write("****************** Generator Cost ******************\n")
        heading = " Index genIdx segmentIdx segmentBreadth segmentPrice Pgi\n"
        fileGenCost.write(heading)
        for i in instance.GENCOST:
            fileGenCost.write("%s %d" % (" ", i))
            fileGenCost.write("%s %s" % (" ", value(instance.GenCost_genIdx[i])))
            fileGenCost.write("%s %s" % (" ", value(instance.GenCost_segmentIdx[i])))
            fileGenCost.write("%s %s" % (" ", value(instance.GenCost_segmentBreadth[i]*instance.BaseMVA)))
            fileGenCost.write("%s %s" % (" ", value(instance.GenCost_segmentPrice[i])))
            fileGenCost.write("%s %f" % (" ", instance.pgi[i].value*instance.BaseMVA))
            fileGenCost.write("%s" % ("\n"))

    myDiary.hotlineWithLogType(5, "SECD simulation results have been written into files")


def deleteOldFiles(fileName, myDiary):
    if os.path.isfile(fileName):
        os.remove(fileName)
        myDiary.hotline("original file " + fileName + " has been deleted")        


