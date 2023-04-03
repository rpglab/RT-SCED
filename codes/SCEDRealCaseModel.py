"""
Created in 2016

@author: Xingpeng Li (xplipower@gmail.com)

Website: https://rpglab.github.io/resources/RT-SCED_Python/
"""

from __future__ import division
from pyomo.environ import *

model = AbstractModel()


## ****************************************************************************
##						  Set
## ****************************************************************************
model.BUS = Set()
model.LOAD = Set()
model.GEN = Set()
model.GENCOST = Set()
model.BRANCH = Set()

model.RESERVEArea = Set()
model.CONTINGENCY = Set()
model.CONSTRAINT = Set()
model.SCENARIO = Set()
#model.NC = Param()
#model.CONSTRAINT = RangeSet(model.NC)


## ****************************************************************************
##						  Parameters
## ****************************************************************************

## -------------------------------- Bus Data ----------------------------------
model.Bus_number = Param (model.BUS) # orig bus number
model.Bus_kv = Param (model.BUS) # bus voltage level
model.Bus_va = Param (model.BUS) # bus initial angle in radian
model.Bus_area = Param (model.BUS) # bus area

## -------------------------------- Load Data ---------------------------------
model.Load_busNumber = Param (model.LOAD) # load bus number
model.Load_id = Param (model.LOAD) # load ID
model.Load_isInSvc = Param (model.LOAD) # is this load in service, 1 is YES
model.Load_pd = Param (model.LOAD, mutable=True)  # active load

## -------------------------------- Gen Data ----------------------------------
model.Gen_busNumber = Param (model.GEN) # Gen bus number
model.Gen_id = Param (model.GEN) # Gen ID
model.Gen_isInSvc = Param (model.GEN) # is this unit in service
model.Gen_pgInit = Param (model.GEN, mutable=True)  # the initial generator output
model.Gen_pgMax = Param (model.GEN, mutable=True)  # the generator Economic Max
model.Gen_pgMin = Param (model.GEN, mutable=True)  # the generator Economic Min
model.Gen_hasMarketData = Param (model.GEN)  # does this unit have market data available, 1 is YES
model.Gen_useBidSlope = Param (model.GEN)  # is the bid curve (MW, $) submitted flat or linear
model.Gen_costCurveSegmentNum = Param (model.GEN)  # Number of Segments of Gen Cost Curve before linearization
model.Gen_energyRamp = Param (model.GEN, mutable=True)  #  energy ramping rate between multiple periods
model.Gen_spinRamp = Param (model.GEN, mutable=True)  # spin ramping rate for contingency
model.Gen_regUnitStatus = Param (model.GEN)  # regulation reserve, 1 means the unit is qualified to provide regulation reserve
model.Gen_regOfferPrice = Param (model.GEN)  # spin ramping rate for contingency
model.Gen_regOfferMW = Param (model.GEN, mutable=True)  # spin ramping rate for contingency
model.Gen_spinUnitStatus = Param (model.GEN)  # spin ramping rate for contingency
model.Gen_spinOfferPrice = Param (model.GEN)  # spin ramping rate for contingency
model.Gen_spinOfferMW = Param (model.GEN, mutable=True)  # spin ramping rate for contingency
model.Gen_fastStartUnitFlag = Param (model.GEN)  # flag for fast start unit, 1 is YES
model.Gen_coldNotificationTime = Param (model.GEN)  # in hour 
model.Gen_coldStartupTime = Param (model.GEN)  # in hour
model.Gen_area = Param (model.GEN)  # area for generation reserve requirement

## -------------------------------- Gen Cost Data -----------------------------
model.GenCost_genIdx = Param (model.GENCOST) # Gen index
model.GenCost_segmentIdx = Param (model.GENCOST) # Gen segment index
model.GenCost_segmentBreadth = Param (model.GENCOST, mutable=True) # Gen one segment breadth
model.GenCost_segmentPrice = Param (model.GENCOST) # Gen one segment price

## -------------------------------- Branch Data -------------------------------
model.Branch_frmBusNumber = Param (model.BRANCH) # Branch from bus number
model.Branch_toBusNumber = Param (model.BRANCH) # Branch to bus number
model.Branch_id = Param (model.BRANCH) # Branch id
model.Branch_isInSvc = Param (model.BRANCH) # Branch status, 1 is in service
model.Branch_r = Param (model.BRANCH) # Branch resistance
model.Branch_x = Param (model.BRANCH) # Branch reactance
model.Branch_angle = Param (model.BRANCH) #  phase shifter angle, it is 0 if it is a normal branch
model.Branch_pkInit = Param (model.BRANCH, mutable=True) # Branch initial power flow in MW
model.Branch_rateA = Param (model.BRANCH, mutable=True) # Branch thermal limit - rate A in MVA
model.Branch_rateB = Param (model.BRANCH, mutable=True) # Branch thermal limit - rate B in MVA
model.Branch_rateC = Param (model.BRANCH, mutable=True) # Branch thermal limit - rate C in MVA

## -------------------------------- Reserve Requirements ----------------------
model.ReserveArea_genArea = Param (model.RESERVEArea) # Areas for reserve requirements
model.ReserveArea_regulationReq = Param (model.RESERVEArea, mutable=True) # Regulation reserve requirement per area in MW
model.ReserveArea_reqPenaltyPrice = Param (model.RESERVEArea) # Penalty price ($/MW) for not meeting Regulation reserve requirement
model.ReserveArea_spinReq = Param (model.RESERVEArea, mutable=True) # Spin reserve requirement per area in MW
model.ReserveArea_spinPenaltyPrice = Param (model.RESERVEArea) # 
model.ReserveArea_primaryReq = Param (model.RESERVEArea, mutable=True) # Primary reserve requirement per area in MW
model.ReserveArea_primaryPenaltyPrice = Param (model.RESERVEArea) # 

## -------------------------------- Scenario Data --------------------------
model.isBaseCase = Param (model.SCENARIO) # 1 is YES. 0 is contingency case. No duplicate case can be found in set of SCENARIO

## -------------------------------- Contingency Data --------------------------
model.Contingency_idx = Param (model.CONTINGENCY) # Contingency index
model.Contingency_branchIdx = Param (model.CONTINGENCY) # Contingency index

## -------------------------------- Constraint Data ---------------------------
model.Constraint_contingencyIdx = Param (model.CONSTRAINT) # Contingency index, -> if remove all duplicate numbers, this index list should be the same with Scenario Index.
model.Constraint_monitorBranchIdx = Param (model.CONSTRAINT) # Monitored Branch index
model.Constraint_monitorBranchLimit = Param (model.CONSTRAINT, mutable=True) # Monitored Branch thermal limit

## -------------------------------- DFAX Data ---------------------------------
model.dFax = Param (model.GEN, model.CONSTRAINT) # Monitored Branch thermal limit

## -------------------------------- Auxiliary Data ----------------------------
model.BaseMVA = Param (default=100)  # look-ahead time for single period RT SCED
model.T_ED = Param (default=15)  # look-ahead time for single period RT SCED
model.T_RR = Param (default=5)  # time for regulation reserve, typically, 5 minutes
model.T_SR = Param (default=10)  # time for spinning reserve, typically, 10 minutes
model.T_PR = Param (default=10)  # time for primary reserve, typically, is the same with model.T_SR, 10 minutes

## -------------------------------- Interface Data ----------------------------
model.INTERFACE = Set()
model.Interface_isEnabled = Param (model.INTERFACE)  # total active power limit
model.Interface_totalLimit = Param (model.INTERFACE, mutable=True)  # total active power limit

model.INTERFACELINE = Set()
model.Interfaceline_interfaceIdx = Param (model.INTERFACELINE)
model.Interfaceline_branchIdx = Param (model.INTERFACELINE)

model.dFaxForInterface = Param (model.GEN, model.INTERFACELINE) # Monitored Branch thermal limit


## ****************************************************************************
##						  Variables
## ****************************************************************************

## -------------------------------- Generator Base Case Output ----------------
model.pg = Var(model.GEN)
model.rr = Var(model.GEN, within=NonNegativeReals)  # Generator Regulation Reserve Output
model.sr = Var(model.GEN, within=NonNegativeReals)  # Generator Spinning Reserve Output
model.pr = Var(model.GEN, within=NonNegativeReals)  # Generator Primary Reserve Output

def bounds_Pgi (model, i):
    return (0, model.GenCost_segmentBreadth[i])
model.pgi = Var(model.GENCOST, within=NonNegativeReals, bounds = bounds_Pgi)

model.pgc = Var(model.GEN, model.SCENARIO)


## ------------------------------ Slack variable for constraints --------------
model.pgmaxSlackVar = Var(model.GEN, within=NonNegativeReals, initialize = 0) # for both base case and contingency case
model.pgminSlackVar = Var(model.GEN, within=NonNegativeReals, initialize = 0)

model.rrSlackVar = Var(model.GEN, within=NonNegativeReals)
model.srSlackVar = Var(model.GEN, within=NonNegativeReals)
model.prSlackVar = Var(model.GEN, within=NonNegativeReals)

model.rrReqSlackVar = Var(model.RESERVEArea, within=NonNegativeReals, initialize = 0)
model.srReqSlackVar = Var(model.RESERVEArea, within=NonNegativeReals, initialize = 0)
model.prReqSlackVar = Var(model.RESERVEArea, within=NonNegativeReals, initialize = 0)

model.Gen_regOfferMWSlackVar = Var(model.GEN, within=NonNegativeReals)
model.Gen_spinOfferMWSlackVar = Var(model.GEN, within=NonNegativeReals)

model.energyRampUpSlackVar = Var(model.GEN, within=NonNegativeReals, initialize = 0)
model.energyRampDownSlackVar = Var(model.GEN, within=NonNegativeReals, initialize = 0)

model.spinRampUpSlackVar = Var(model.GEN, model.SCENARIO, within=NonNegativeReals, initialize = 0)
model.spinRampDownSlackVar = Var(model.GEN, model.SCENARIO, within=NonNegativeReals, initialize = 0)

model.brcFlowLimitSlackVar = Var(model.CONSTRAINT, within=NonNegativeReals, initialize = 0)

model.interfaceLimiteSlackVar = Var(model.INTERFACE, within=NonNegativeReals, initialize = 0)

## -------------------------------- Monitor Branch Limit ----------------------
model.pk = Var(model.CONSTRAINT)
model.totalFlowForInterface = Var(model.INTERFACE, initialize = 0)
model.pkForInterfaceLine = Var(model.INTERFACELINE, initialize = 0)


## ****************************************************************************
##						  Constraints
## ****************************************************************************

## -------------------------------- System power balance equation -------------
def const_systemBal(model):
    expr = sum(model.pg[g] for g in model.GEN if model.Gen_isInSvc[g] == 1)
    expr = expr - sum(model.Load_pd[d] for d in model.LOAD if model.Load_isInSvc[d] == 1)
    return expr == 0
model.systemBalConst = Constraint(rule = const_systemBal)

def const_systemBalCntgy(model, s):
    expr = sum(model.pgc[g, s] for g in model.GEN if model.Gen_isInSvc[g] == 1)
    expr = expr - sum(model.Load_pd[d] for d in model.LOAD if model.Load_isInSvc[d] == 1)
    return expr == 0
model.systemBalCntgyConst = Constraint(model.SCENARIO, rule = const_systemBalCntgy)

## -------------------------------- branch flow limit -------------------------
def const_flowLimit(model, k):
    return model.pk[k] <= model.Constraint_monitorBranchLimit[k] + model.brcFlowLimitSlackVar[k]
model.brcFlowLimitConst = Constraint(model.CONSTRAINT, rule = const_flowLimit)

def const_flowLimit_2(model, k):
    return model.pk[k] >= -model.Constraint_monitorBranchLimit[k] - model.brcFlowLimitSlackVar[k]
model.brcFlowLimitConst_2 = Constraint(model.CONSTRAINT, rule = const_flowLimit_2)

## -------------------------------- Branch flow calculation -------------------
def const_CalcFlow(model, k):
    idxBrc = model.Constraint_monitorBranchIdx[k]
    idxCntcy = model.Constraint_contingencyIdx[k]  # should be an index that is also contained with Scenario IndexSet
    expr = model.Branch_pkInit[idxBrc]
    if model.Contingency_branchIdx[idxCntcy] == -2:
        for g in model.GEN:
            if model.Gen_isInSvc[g] == 1:
                expr = expr + model.dFax[g, k]*(model.pg[g] - model.Gen_pgInit[g])
        expr = expr - model.pk[k]
        return expr == 0
    else:
        for g in model.GEN:
            if model.Gen_isInSvc[g] == 1:
                expr = expr + model.dFax[g, k]*(model.pgc[g, idxCntcy] - model.Gen_pgInit[g])
        expr = expr - model.pk[k]
        return expr == 0
model.brcFlowCalcConst = Constraint(model.CONSTRAINT, rule = const_CalcFlow)

## -------------------------------- Gen segment output sum --------------------
# Consider to use Dictionary to speed up the process of adding const_GenSegmentSum
def const_GenSegmentSum(model, g):
    if model.Gen_isInSvc[g] == 0:
        return model.pg[g] == 0
    elif model.Gen_hasMarketData[g] == 0:
        return model.pg[g] == model.Gen_pgInit[g]
    elif value(model.Gen_pgInit[g]) <= 0:
        return Constraint.Skip
    else:
        expr = 0
        idx = 0
        for i in model.GENCOST:
            unit = model.GenCost_genIdx[i]
            if g == unit:
                idx = idx + 1
                expr = expr + model.pgi[i]
        if idx == 0:
            print "Something wrong: no cost segment found for generator ", str(g)
            return Constraint.Skip
        else:
            expr = expr - model.pg[g]
            return expr == 0
model.genSegmentSumConst = Constraint(model.GEN, rule = const_GenSegmentSum)

def const_GenCostFixed(model, i):
    genIdx = model.GenCost_genIdx[i]
    if model.Gen_isInSvc[genIdx] == 0:
        return model.pgi[i] == 0
    elif model.Gen_hasMarketData[genIdx] == 0:
        return model.pgi[i] == 0
    elif value(model.Gen_pgInit[genIdx]) <= 0:
        return model.pgi[i] == 0
    else:
        return Constraint.Skip
model.genCostFixed = Constraint(model.GENCOST, rule = const_GenCostFixed)

## -------------------------------- Gen ramping limit -------------------------
def const_GenEnergyRampUpLimit(model, g):
    if model.Gen_isInSvc[g] == 0:
        return model.energyRampUpSlackVar[g] == 0
    else:
        expr = model.pg[g] - model.Gen_pgInit[g]
        return expr <= model.Gen_energyRamp[g]*model.T_ED + model.energyRampUpSlackVar[g]
model.genEnergyRampUpConst = Constraint(model.GEN, rule = const_GenEnergyRampUpLimit)

def const_GenEnergyRampDownLimit(model, g):
    if model.Gen_isInSvc[g] == 0:
        return model.energyRampDownSlackVar[g] == 0
    else:
        expr = model.pg[g] - model.Gen_pgInit[g]
        return expr >= -model.Gen_energyRamp[g]*model.T_ED - model.energyRampDownSlackVar[g]
model.genEnergyRampDownConst = Constraint(model.GEN, rule = const_GenEnergyRampDownLimit)

def const_GenCntgyRampUpLimit(model, s, g):
    if model.Gen_isInSvc[g] == 0:
        return model.spinRampUpSlackVar[g, s] == 0
    else:
        expr = model.pgc[g, s] - model.pg[g]
        return expr <= model.Gen_spinRamp[g]*model.T_SR + model.spinRampUpSlackVar[g, s]
model.genSpinRampUpConst = Constraint(model.SCENARIO, model.GEN, rule = const_GenCntgyRampUpLimit)

def const_GenCntgyRampDownLimit(model, s, g):
    if model.Gen_isInSvc[g] == 0:
        return model.spinRampDownSlackVar[g, s] == 0
    else:
        expr = model.pgc[g, s] - model.pg[g]
        return expr >= -model.Gen_spinRamp[g]*model.T_SR - model.spinRampDownSlackVar[g, s]
model.genSpinRampDownConst = Constraint(model.SCENARIO, model.GEN, rule = const_GenCntgyRampDownLimit)

## -------------------------------- Reserve limit -----------------------------
def const_RegReserveRampLimit(model, g):
    if model.Gen_isInSvc[g] == 0:
        return model.rrSlackVar[g] == 0
    else:
        return model.rr[g] <= model.Gen_spinRamp[g]*model.T_RR + model.rrSlackVar[g]
model.regReserveRampConst = Constraint(model.GEN, rule = const_RegReserveRampLimit)

def const_RegReserveQua(model, g):
    if model.Gen_isInSvc[g] == 0:
        return model.rr[g] == 0
    elif model.Gen_regUnitStatus[g] == 0:
        return model.rr[g] == 0
    elif model.Gen_hasMarketData[g] == 0:
        return model.rr[g] == 0
    else:
#        return model.pr[g] == 0  # need to find out whether regulation reserve would be also counted as primary reserve
        return Constraint.Skip
model.regReserveQua = Constraint(model.GEN, rule = const_RegReserveQua)

def const_SpinReserveRampLimit(model, g):
    if model.Gen_isInSvc[g] == 0:
        return model.srSlackVar[g] == 0
    else:
        return model.sr[g] <= model.Gen_spinRamp[g]*model.T_SR + model.srSlackVar[g]
model.spinReserveRampConst = Constraint(model.GEN, rule = const_SpinReserveRampLimit)

def const_SpinReserveQua(model, g):
    if model.Gen_isInSvc[g] == 0:
        return model.sr[g] == 0
    elif model.Gen_regUnitStatus[g] == 1 or model.Gen_spinUnitStatus[g] == 0:
        return model.sr[g] == 0
    elif model.Gen_hasMarketData[g] == 0:
        return model.sr[g] == 0
    else:
        return Constraint.Skip
model.spinReserveQua = Constraint(model.GEN, rule = const_SpinReserveQua)

def const_PrimaryReserveRampLimit(model, g):
    if model.Gen_isInSvc[g] == 1:
        return model.pr[g] <= model.Gen_spinRamp[g]*model.T_PR + model.prSlackVar[g]
    elif model.Gen_fastStartUnitFlag[g] == 1:
        availableRampMinutes = model.T_PR - model.Gen_coldNotificationTime[g]*60 - model.Gen_coldStartupTime[g]*60
        if availableRampMinutes < 0:
            availableRampMinutes = 0
        return model.pr[g] <= model.Gen_spinRamp[g]*availableRampMinutes + model.prSlackVar[g]
    else:
        return model.pr[g] + model.prSlackVar[g] == 0
model.primaryReserveRampConst = Constraint(model.GEN, rule = const_PrimaryReserveRampLimit)

def const_PrimaryReserveQua(model, g):
    return model.pr[g] >= model.sr[g]
model.primaryReserveQua = Constraint(model.GEN, rule = const_PrimaryReserveQua)

## -------------------------------- Unit generation limit ---------------------
def const_GenMaxLimit(model, g):
    if model.Gen_isInSvc[g] == 0:
        return model.pgmaxSlackVar[g] == 0
    else:
        return model.pg[g] <= model.Gen_pgMax[g] + model.pgmaxSlackVar[g]
model.genMaxLimitConst = Constraint(model.GEN, rule = const_GenMaxLimit)

def const_GenMinLimit(model, g):
    if model.Gen_isInSvc[g] == 0:
        return model.pgminSlackVar[g] == 0
    else:
        return model.pg[g] >= model.Gen_pgMin[g] - model.pgminSlackVar[g]
model.genMinLimitConst = Constraint(model.GEN, rule = const_GenMinLimit)

def const_GenMaxLimitCntgy(model, g, c):
    if model.Gen_isInSvc[g] == 0:
        return model.pgc[g, c] == 0
    else:
        return model.pgc[g, c] <= model.Gen_pgMax[g] + model.pgmaxSlackVar[g]
model.genMaxLimitCntgyConst = Constraint(model.GEN, model.SCENARIO, rule = const_GenMaxLimitCntgy)

def const_GenMinLimitCntgy(model, g, c):
    if model.Gen_isInSvc[g] == 0:
        return Constraint.Skip
    else:
        return model.pgc[g, c] >= model.Gen_pgMin[g] - model.pgminSlackVar[g]
model.genMinLimitCntgyConst = Constraint(model.GEN, model.SCENARIO, rule = const_GenMinLimitCntgy)

def const_GenRegLimit(model, g):
    if model.Gen_isInSvc[g] == 0:
        return Constraint.Skip
    else:
        expr = model.pg[g] + model.rr[g]
        return expr <= model.Gen_pgMax[g] + model.pgmaxSlackVar[g]
model.genRegLimitConst = Constraint(model.GEN, rule = const_GenRegLimit)

def const_GenSpinLimit(model, g):
    if model.Gen_isInSvc[g] == 0:
        return Constraint.Skip
    else:
        expr = model.pg[g] + model.sr[g]
        return expr <= model.Gen_pgMax[g] + model.pgmaxSlackVar[g]
model.genSpinLimitConst = Constraint(model.GEN, rule = const_GenSpinLimit)

def const_GenPrimaryLimit(model, g):
    if model.Gen_isInSvc[g] == 0:
        pgmax = value(model.Gen_pgMax[g])
        if pgmax < 0:
            pgmax = 0
        return model.pr[g] <= pgmax + model.prSlackVar[g]
    else:
        expr = model.pg[g] + model.pr[g]
        return expr <= model.Gen_pgMax[g] + model.pgmaxSlackVar[g]
model.genPrimaryLimitConst = Constraint(model.GEN, rule = const_GenPrimaryLimit)

## -------------------------------- Reserve Requirements ----------------------
def const_regReserveReq(model, idxArea):
    expr = 0
    for g in model.GEN:
        if model.Gen_isInSvc[g] == 1:
            if model.Gen_area[g] == model.ReserveArea_genArea[idxArea]:
                expr = expr + model.rr[g]
    expr = expr + model.rrReqSlackVar[idxArea]
    return expr >= model.ReserveArea_regulationReq[idxArea]
model.areaRegReserveReqConst = Constraint(model.RESERVEArea, rule = const_regReserveReq)

def const_spinReserveReq(model, idxArea):
    expr = 0
    for g in model.GEN:
        if model.Gen_isInSvc[g] == 1:
            if model.Gen_area[g] == model.ReserveArea_genArea[idxArea]:
                expr = expr + model.sr[g]
    expr = expr + model.srReqSlackVar[idxArea]
    return expr >= model.ReserveArea_spinReq[idxArea]
model.areaSpinReserveReqConst = Constraint(model.RESERVEArea, rule = const_spinReserveReq)

def const_primaryReserveReq(model, idxArea):
    expr = 0
    for g in model.GEN:
        # an offline unit may be able to provide primary reserve
        if model.Gen_area[g] == model.ReserveArea_genArea[idxArea]:
            expr = expr + model.pr[g]
    expr = expr + model.prReqSlackVar[idxArea]
    return expr >= model.ReserveArea_primaryReq[idxArea]
model.areaPrimaryReserveReqConst = Constraint(model.RESERVEArea, rule = const_primaryReserveReq)

## -------------------------------- Gen reserve offer limit -------------------
def const_RegReserveOfferLimit(model, g):
    if model.Gen_isInSvc[g] == 0:
        return model.Gen_regOfferMWSlackVar[g] == 0
    else:
        return model.rr[g] <= model.Gen_regOfferMW[g] + model.Gen_regOfferMWSlackVar[g]
model.regReserveOfferLimit = Constraint(model.GEN, rule = const_RegReserveOfferLimit)

def const_SpinReserveOfferLimit(model, g):
    if model.Gen_isInSvc[g] == 0:
        return model.Gen_spinOfferMWSlackVar[g] == 0
    else:
        return model.sr[g] <= model.Gen_spinOfferMW[g] + model.Gen_spinOfferMWSlackVar[g]
model.spinReserveOfferLimit = Constraint(model.GEN, rule = const_SpinReserveOfferLimit)

## -------------------------------- Additional Constraints --------------------
def const_NonDispatchableGenCntgyCaseLimit(model, s, g):
    if model.Gen_hasMarketData[g] == 0:
        return model.pgc[g, s] == model.pg[g]
    else:
        return Constraint.Skip
model.nonDispatchableGenCntgyCaseLimit = Constraint(model.SCENARIO, model.GEN, rule = const_NonDispatchableGenCntgyCaseLimit)

def const_BaseCntgySameCaseLimit(model, s, g):
    if model.isBaseCase[s] == 0:
        return Constraint.Skip
    else:
        return model.pgc[g, s] == model.pg[g]
model.baseCntgySameCaseLimit = Constraint(model.SCENARIO, model.GEN, rule = const_BaseCntgySameCaseLimit)

## --------------------------------  Interface limit --------------------------
def const_InterfaceLimit(model, i):
    if model.Interface_isEnabled[i] == 1:
        expr = model.totalFlowForInterface[i]
        return expr <= model.Interface_totalLimit[i] + model.interfaceLimiteSlackVar[i]
    else:
        return Constraint.Skip
model.interfaceLimitConst = Constraint(model.INTERFACE, rule = const_InterfaceLimit)

def const_CalcInterfaceTotalFlow(model, i):
    expr = 0
    for k in model.INTERFACELINE:
        if model.Interfaceline_interfaceIdx[k] == i:
            expr = expr + model.pkForInterfaceLine[k]
    return expr == model.totalFlowForInterface[i]
model.calcInterfaceTotalFlowConst = Constraint(model.INTERFACE, rule = const_CalcInterfaceTotalFlow)

def const_CalcInterfaceLineFlow(model, k):
    idxBrc = model.Interfaceline_branchIdx[k]
    expr = model.Branch_pkInit[idxBrc]
    for g in model.GEN:
        if model.Gen_isInSvc[g] == 1:
            expr = expr + model.dFaxForInterface[g, k]*(model.pg[g] - model.Gen_pgInit[g])
    expr = expr - model.pkForInterfaceLine[k]
    return expr == 0
model.calcInterfaceLineFlowConst = Constraint(model.INTERFACELINE, rule = const_CalcInterfaceLineFlow)


## ****************************************************************************
##						  Objective function
## ****************************************************************************
model.PgMax_penalty = Param (default=850.0)
model.PgMin_penalty = Param (default=850.0)

model.RR_penalty = Param (default=850.0)
model.SR_penalty = Param (default=850.0)   # $/(MW/min)
model.PR_penalty = Param (default=850.0)

model.RR_OfferLimit_penalty = Param (default=850.0)
model.SR_OfferLimit_penalty = Param (default=850.0)

model.energyRampUp_penalty = Param (default=850.0)
model.energyRampDown_penalty = Param (default=850.0)
model.spinRampUp_penalty = Param (default=850.0)
model.spinRampDown_penalty = Param (default=850.0)

model.BrcFlowLimit_penalty = Param (default=950.0)
model.InterfaceFlowLimit_penalty = Param (default=950.0)

def costObj(model):
    expr = model.BaseMVA*( sum(model.pgi[i]*model.GenCost_segmentPrice[i] for i in model.GENCOST) \
            + sum(model.rr[g]*model.Gen_regOfferPrice[g] for g in model.GEN) \
            + sum(model.sr[g]*model.Gen_spinOfferPrice[g] for g in model.GEN) \
            + model.PgMax_penalty*sum(model.pgmaxSlackVar[g] for g in model.GEN) \
            + model.PgMin_penalty*sum(model.pgminSlackVar[g] for g in model.GEN) \
            + model.RR_penalty*sum(model.rrSlackVar[g] for g in model.GEN) \
            + model.SR_penalty*sum(model.srSlackVar[g] for g in model.GEN) \
            + model.PR_penalty*sum(model.prSlackVar[g] for g in model.GEN) \
            + sum(model.rrReqSlackVar[idxArea]*model.ReserveArea_reqPenaltyPrice[idxArea] for idxArea in model.RESERVEArea) \
            + sum(model.srReqSlackVar[idxArea]*model.ReserveArea_spinPenaltyPrice[idxArea] for idxArea in model.RESERVEArea) \
            + sum(model.prReqSlackVar[idxArea]*model.ReserveArea_primaryPenaltyPrice[idxArea] for idxArea in model.RESERVEArea) \
            + model.RR_OfferLimit_penalty*sum(model.Gen_regOfferMWSlackVar[g] for g in model.GEN) \
            + model.SR_OfferLimit_penalty*sum(model.Gen_spinOfferMWSlackVar[g] for g in model.GEN) \
            + model.energyRampUp_penalty*sum(model.energyRampUpSlackVar[g] for g in model.GEN) \
            + model.energyRampDown_penalty*sum(model.energyRampDownSlackVar[g] for g in model.GEN) \
            + model.spinRampUp_penalty*sum(model.spinRampUpSlackVar[g, s] for g in model.GEN for s in model.SCENARIO) \
            + model.spinRampDown_penalty*sum(model.spinRampDownSlackVar[g, s] for g in model.GEN for s in model.SCENARIO) \
            + model.BrcFlowLimit_penalty*sum(model.brcFlowLimitSlackVar[k] for k in model.CONSTRAINT) \
            + model.InterfaceFlowLimit_penalty*sum(model.interfaceLimiteSlackVar[i] for i in model.INTERFACE) )
    return expr
model.minimizeCost = Objective(rule=costObj)  # by default, sense = minimize

