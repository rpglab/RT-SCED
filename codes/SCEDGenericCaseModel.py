"""
Created in 2016

# Author: Xingpeng Li
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
model.Gen_energyRamp = Param (model.GEN, within=NonNegativeReals, mutable=True)  #  energy ramping rate between multiple periods
model.Gen_spinRamp = Param (model.GEN, within=NonNegativeReals, mutable=True)  # spin ramping rate for contingency
model.Gen_costCurveFlag = Param (model.GEN) # 1 indicates a cost curve is available

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
model.Branch_rateA = Param (model.BRANCH, mutable=True) # Branch thermal limit - rate A
model.Branch_rateB = Param (model.BRANCH, mutable=True) # Branch thermal limit - rate B
model.Branch_rateC = Param (model.BRANCH, mutable=True) # Branch thermal limit - rate C

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

## -------------------------------- Contingency Data --------------------------
model.CONTINGENCY = Set()
model.Contingency_isEnabled = Param (model.CONTINGENCY)

model.CONTINGENCYLINE = Set()
model.Contingency_index = Param (model.CONTINGENCYLINE)
model.Contingency_branchIdx = Param (model.CONTINGENCYLINE)

## ****************************************************************************
##						  Variables
## ****************************************************************************

## -------------------------------- Generator Base Case Output ----------------
model.pg = Var(model.GEN)
model.sr = Var(model.GEN, within=NonNegativeReals)
model.theta = Var(model.BUS, initialize = 0)
model.loadServed = Var(model.LOAD, initialize = 0)
model.loadShed = Var(model.LOAD, within=NonNegativeReals, initialize = 0)

def bounds_Pgi (model, i):
    return (0, model.GenCost_segmentBreadth[i])
model.pgi = Var(model.GENCOST, within=NonNegativeReals, bounds = bounds_Pgi)

model.pk = Var(model.BRANCH) # branch line flow

model.totalFlowForInterface = Var(model.INTERFACE, initialize = 0) # total line flow for an interface

## --------------- Contingency-related variables ------------------------------
model.pgc = Var(model.GEN, model.CONTINGENCY)   # note the set order 
model.theta_c = Var(model.CONTINGENCY, model.BUS)
model.pkc = Var(model.CONTINGENCY, model.BRANCH)
model.loadServed_c = Var(model.CONTINGENCY, model.LOAD, initialize = 0)
model.loadShed_c = Var(model.CONTINGENCY, model.LOAD, within=NonNegativeReals, initialize = 0)
model.totalFlowForInterface_c = Var(model.CONTINGENCY, model.INTERFACE, initialize = 0)

## ------------------------------ Slack variable for some constraints ---------
model.pgmaxSlackVar = Var(model.GEN, within=NonNegativeReals, initialize = 0)
model.pgminSlackVar = Var(model.GEN, within=NonNegativeReals, initialize = 0)
model.spinRampSlackVar = Var(model.GEN, within=NonNegativeReals, initialize = 0)
model.energyRampUpSlackVar = Var(model.GEN, within=NonNegativeReals, initialize = 0)
model.energyRampDownSlackVar = Var(model.GEN, within=NonNegativeReals, initialize = 0)
model.srReqSlackVar = Var(model.GEN, within=NonNegativeReals, initialize = 0)
model.brcFlowLimitSlackVar = Var(model.BRANCH, within=NonNegativeReals, initialize = 0)
model.interfaceLimiteSlackVar = Var(model.INTERFACE, within=NonNegativeReals, initialize = 0)


## ****************************************************************************
##						  Constraints
## ****************************************************************************

## -------------------------------- System power balance equation -------------
def const_NodeBal(model, n):
    expr = sum(model.pg[g] for g in model.GEN if model.Gen_busNumber[g] == n)
    expr = expr - sum(model.loadServed[d] for d in model.LOAD if model.Load_busNumber[d] == n)
    expr = expr - sum(model.pk[k] for k in model.BRANCH if model.Branch_frmBusNumber[k]==n)
    expr = expr + sum(model.pk[k] for k in model.BRANCH if model.Branch_toBusNumber[k]==n)
    return expr == 0
model.nodeBalConst = Constraint(model.BUS, rule = const_NodeBal)

## -------------------------------- Load shed calculation ---------------------
def const_LoadTotalLimit(model, d):
    expr = model.loadShed[d] + model.loadServed[d]
    expr = expr - model.Load_pd[d]*model.Load_isInSvc[d]
    return expr == 0
model.loadTotalConst = Constraint(model.LOAD, rule = const_LoadTotalLimit)

def const_FixOfflineAndNegativeLoad(model, d):
    if model.Load_isInSvc[d] == 0:
        return model.loadShed[d] == 0
    elif value(model.Load_pd[d]) < 0:
        return model.loadShed[d] == 0
    else:
        return model.loadServed[d] >= 0
model.fixOfflineAndNegativeLoad = Constraint(model.LOAD, rule = const_FixOfflineAndNegativeLoad)

#def const_RemoveLoadShedFeature(model, d):
#    return model.loadShed[d] == 0
#model.removeLoadShedFeatureConst = Constraint(model.LOAD, rule = const_RemoveLoadShedFeature)

## -------------------------------- Branch flow calculation -------------------
def const_CalcFlow(model, k):
    if model.Branch_isInSvc[k] == 0:
        return model.pk[k] == 0
    else:
        expr = model.pk[k] - (model.theta[model.Branch_frmBusNumber[k]] - model.theta[model.Branch_toBusNumber[k]] - model.Branch_angle[k]) / model.Branch_x[k]
        return expr == 0
model.brcFlowCalcConst = Constraint(model.BRANCH, rule = const_CalcFlow)

## -------------------------------- Branch flow limit -------------------------
def const_BrcFlowLimit(model, k):
    if model.Branch_isInSvc[k] == 0:
        return Constraint.Skip
    else:
        expr = model.pk[k] - model.brcFlowLimitSlackVar[k]
        return expr <= model.Branch_rateA[k]
model.brcFlowLimit = Constraint(model.BRANCH, rule = const_BrcFlowLimit)

def const_BrcFlowLimit_2(model, k):
    if model.Branch_isInSvc[k] == 0:
        return Constraint.Skip
    else:
        expr = model.pk[k] + model.brcFlowLimitSlackVar[k]
        return expr >= -model.Branch_rateA[k]
model.brcFlowLimit_2 = Constraint(model.BRANCH, rule = const_BrcFlowLimit_2)

## -------------------------------- Gen cost curve limit ----------------------
# Consider to use Dictionary to speed up the process of adding const_GenSegmentSum
def const_GenSegmentSum(model, g):
    if model.Gen_isInSvc[g] == 0:
        return model.pg[g] == 0
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
            return Constraint.Skip
        else:
            expr = expr - model.pg[g]
            return expr == 0
model.genSegmentSumConst = Constraint(model.GEN, rule = const_GenSegmentSum)

def const_GenCostFixed(model, i):
    genIdx = model.GenCost_genIdx[i]
    if model.Gen_isInSvc[genIdx] == 0:
        return model.pgi[i] == 0
    else:
        if value(model.Gen_pgInit[genIdx]) <= 0:
            return model.pgi[i] == 0
        else:
            return Constraint.Skip
model.genCostFixedConst = Constraint(model.GENCOST, rule = const_GenCostFixed)

def const_GenCostCurveFlag(model, g):
    if model.Gen_costCurveFlag[g] == 0:
        return model.pg[g] == model.Gen_pgInit[g]*model.Gen_isInSvc[g]
    else:
        return Constraint.Skip
model.genCostCurveFlagConst = Constraint(model.GEN, rule = const_GenCostCurveFlag)

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
        return expr >= (-model.Gen_energyRamp[g] - model.energyRampDownSlackVar[g])*model.T_ED
model.genEnergyRampDownConst = Constraint(model.GEN, rule = const_GenEnergyRampDownLimit)

## -------------------------------- Reserve limit -----------------------------
def const_SpinReserveRampLimit(model, g):
    if model.Gen_isInSvc[g] == 0:
        return model.spinRampSlackVar[g] == 0
    else:
        return model.sr[g] <= model.Gen_spinRamp[g]*model.T_SR + model.spinRampSlackVar[g]
model.spinReserveRampConst = Constraint(model.GEN, rule = const_SpinReserveRampLimit)

## -------------------------------- Unit generation limit ---------------------
def const_GenMaxLimit(model, g):
    if model.Gen_isInSvc[g] == 0:
        return model.pgmaxSlackVar[g] == 0
    else:
        return model.pg[g] - model.pgmaxSlackVar[g] <= model.Gen_pgMax[g]
model.genMaxLimitConst = Constraint(model.GEN, rule = const_GenMaxLimit)

def const_GenMinLimit(model, g):
    if model.Gen_isInSvc[g] == 0:
        return model.pgminSlackVar[g] == 0
    else:
        return model.pg[g] + model.pgminSlackVar[g] >= model.Gen_pgMin[g]
model.genMinLimitConst = Constraint(model.GEN, rule = const_GenMinLimit)

def const_GenSpinLimit(model, g):
    if model.Gen_isInSvc[g] == 0:
        return model.sr[g] == 0
    else:
        expr = model.pg[g] + model.sr[g]
        return expr <= model.Gen_pgMax[g] + model.pgmaxSlackVar[g]
model.genSpinLimitConst = Constraint(model.GEN, rule = const_GenSpinLimit)

## --------------------------------  Spinning reserve for Largest gen ctgcy----
def const_SpinReserveForLargestGenCntgy(model, g):
    if model.Gen_isInSvc[g] == 0:
        return model.srReqSlackVar[g] == 0
    else:
        expr = sum(model.sr[u] for u in model.GEN) - model.sr[g] - model.pg[g]
        return expr + model.srReqSlackVar[g] >= 0
model.spinReserveForLargestGenCntgy = Constraint(model.GEN, rule = const_SpinReserveForLargestGenCntgy)

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
            expr = expr + model.pk[model.Interfaceline_branchIdx[k]]
    return expr == model.totalFlowForInterface[i]
model.calcInterfaceTotalFlowConst = Constraint(model.INTERFACE, rule = const_CalcInterfaceTotalFlow)

## --------------------------------  Contingency limit ------------------------
## System power balance equation
def const_NodeBal_Ctgcy(model, c, n):
    if model.Contingency_isEnabled[c] == 0:
        return Constraint.Skip
    else:
        expr = sum(model.pgc[g, c] for g in model.GEN if model.Gen_busNumber[g] == n)
        expr = expr - sum(model.loadServed_c[c, d] for d in model.LOAD if model.Load_busNumber[d] == n)
        expr = expr - sum(model.pkc[c, k] for k in model.BRANCH if model.Branch_frmBusNumber[k]==n)
        expr = expr + sum(model.pkc[c, k] for k in model.BRANCH if model.Branch_toBusNumber[k]==n)
        return expr == 0
model.nodeBalConst_Ctgcy = Constraint(model.CONTINGENCY, model.BUS, rule = const_NodeBal_Ctgcy)

def const_LoadTotalLimit_Ctgcy(model, c, d):
    if model.Contingency_isEnabled[c] == 0:
        return Constraint.Skip
    else:
        expr = model.loadShed_c[c, d] + model.loadServed_c[c, d]
        expr = expr - model.Load_pd[d]*model.Load_isInSvc[d]
        return expr == 0
model.loadTotalConst_Ctgcy = Constraint(model.CONTINGENCY, model.LOAD, rule = const_LoadTotalLimit_Ctgcy)

def const_FixOfflineAndNegativeLoad_Ctgcy(model, c, d):
    if model.Contingency_isEnabled[c] == 0:
        return Constraint.Skip
    elif model.Load_isInSvc[d] == 0:
        return model.loadShed_c[c, d] == 0
    elif value(model.Load_pd[d]) < 0:
        return model.loadShed_c[c, d] == 0
    else:
        return model.loadShed_c[c, d] >= 0
model.fixOfflineAndNegativeLoad_Ctgcy = Constraint(model.CONTINGENCY, model.LOAD, rule = const_FixOfflineAndNegativeLoad_Ctgcy)

## Branch flow calculation
def const_CalcFlow_Ctgcy(model, cL, k):
    c = model.Contingency_index[cL]
    if model.Contingency_isEnabled[c] == 0:
        return model.pkc[c, k] == 0  # then, the associated pkc has no meaning, just assign 0 value to it.
    elif model.Contingency_branchIdx[cL] == k:
        return model.pkc[c, k] == 0
    elif model.Branch_isInSvc[k] == 0:
        return model.pkc[c, k] == 0
    else:
        expr = model.pkc[c, k] - (model.theta_c[c, model.Branch_frmBusNumber[k]] - model.theta_c[c, model.Branch_toBusNumber[k]] - model.Branch_angle[k]) / model.Branch_x[k]
        return expr == 0
model.brcFlowCalcConst_Ctgcy = Constraint(model.CONTINGENCYLINE, model.BRANCH, rule = const_CalcFlow_Ctgcy)

##  Branch flow limit 
def const_BrcFlowLimit_Ctgcy(model, c, k):
    if model.Contingency_isEnabled[c] == 0:
        return Constraint.Skip
    elif model.Contingency_branchIdx[c] == k:
        return Constraint.Skip
    elif model.Branch_isInSvc[k] == 0:
        return Constraint.Skip
    else:
        expr = model.pkc[c, k] - model.brcFlowLimitSlackVar[k]
        return expr <= model.Branch_rateC[k]
model.brcFlowLimit_Ctgcy = Constraint(model.CONTINGENCY, model.BRANCH, rule = const_BrcFlowLimit_Ctgcy)

def const_BrcFlowLimit_2_Ctgcy(model, c, k):
    if model.Contingency_isEnabled[c] == 0:
        return Constraint.Skip
    elif model.Contingency_branchIdx[c] == 0:
        return Constraint.Skip
    elif model.Branch_isInSvc[k] == 0:
        return Constraint.Skip
    else:
        expr = model.pkc[c, k] + model.brcFlowLimitSlackVar[k]
        return expr >= -model.Branch_rateC[k]
model.brcFlowLimit_2_Ctgcy = Constraint(model.CONTINGENCY, model.BRANCH, rule = const_BrcFlowLimit_2_Ctgcy)

##  Unit limit 
def const_GenMaxLimit_Ctgcy(model, c, g):
    if model.Contingency_isEnabled[c] == 0:
        return model.pgc[g, c] == 0
    if model.Gen_isInSvc[g] == 0:
        return model.pgc[g, c] == 0
    else:
        return model.pgc[g, c] - model.pgmaxSlackVar[g] <= model.Gen_pgMax[g]
model.genMaxLimitConst_Ctgcy = Constraint(model.CONTINGENCY, model.GEN, rule = const_GenMaxLimit_Ctgcy)

def const_GenMinLimit_Ctgcy(model, c, g):
    if model.Contingency_isEnabled[c] == 0:
        return Constraint.Skip
    if model.Gen_isInSvc[g] == 0:
        return Constraint.Skip
    else:
        return model.pgc[g, c] + model.pgminSlackVar[g] >= model.Gen_pgMin[g]
model.genMinLimitConst_Ctgcy = Constraint(model.CONTINGENCY, model.GEN, rule = const_GenMinLimit_Ctgcy)

def const_GenCostCurveFlag_Ctgcy(model, c, g):
    if model.Contingency_isEnabled[c] == 0:
        return Constraint.Skip
    elif model.Gen_costCurveFlag[g] == 0:
        return model.pgc[g, c] == model.Gen_pgInit[g]*model.Gen_isInSvc[g]
    else:
        return Constraint.Skip
model.genCostCurveFlagConst_Ctgcy = Constraint(model.CONTINGENCY, model.GEN, rule = const_GenCostCurveFlag_Ctgcy)

## Spin ramp limit
def const_SpinRampLimit_Ctgcy(model, c, g):
    if model.Contingency_isEnabled[c] == 0:
        return Constraint.Skip
    elif model.Gen_isInSvc[g] == 0:
        return Constraint.Skip
    else:
        expr = model.pgc[g, c] - model.pg[g]
        return expr <= model.Gen_spinRamp[g]*model.T_SR + model.spinRampSlackVar[g]
model.spinRampLimit_Ctgcy = Constraint(model.CONTINGENCY, model.GEN, rule = const_SpinRampLimit_Ctgcy)

def const_SpinRampLimit_2_Ctgcy(model, c, g):
    if model.Contingency_isEnabled[c] == 0:
        return Constraint.Skip
    elif model.Gen_isInSvc[g] == 0:
        return Constraint.Skip
    else:
        expr = model.pgc[g, c] - model.pg[g]
        return expr >= -model.Gen_spinRamp[g]*model.T_SR - model.spinRampSlackVar[g]
model.spinRampLimit_2_Ctgcy = Constraint(model.CONTINGENCY, model.GEN, rule = const_SpinRampLimit_2_Ctgcy)

## Interface limit
def const_InterfaceLimit_Ctgcy(model, c, i):
    if model.Contingency_isEnabled[c] == 0:
        return Constraint.Skip
    elif model.Interface_isEnabled[i] == 1:
        expr = model.totalFlowForInterface_c[c, i]
        return expr <= model.Interface_totalLimit[i] + model.interfaceLimiteSlackVar[i]
    else:
        return Constraint.Skip
model.interfaceLimitConst_Ctgcy = Constraint(model.CONTINGENCY, model.INTERFACE, rule = const_InterfaceLimit_Ctgcy)

def const_CalcInterfaceTotalFlow_Ctgcy(model, c, i):
    if model.Contingency_isEnabled[c] == 0:
        return Constraint.Skip
    else:
        expr = 0
        for k in model.INTERFACELINE:
            if model.Interfaceline_interfaceIdx[k] == i:
                expr = expr + model.pkc[c, model.Interfaceline_branchIdx[k]]
        return expr == model.totalFlowForInterface_c[c, i]
model.calcInterfaceTotalFlowConst_Ctgcy = Constraint(model.CONTINGENCY, model.INTERFACE, rule = const_CalcInterfaceTotalFlow_Ctgcy)


## ****************************************************************************
##						  Objective function
## ****************************************************************************
model.SR_price = Param (default=6.99)  # price for spinning reserve

model.PgMax_penalty = Param (default=850.0)
model.PgMin_penalty = Param (default=850.0)
model.SR_penalty = Param (default=850.0)

model.energyRampUp_penalty = Param (default=850.0)
model.energyRampDown_penalty = Param (default=850.0)
model.spinRamp_penalty = Param (default=850.0)

model.BrcFlowLimit_penalty = Param (default=950.0)
model.LoadShed_penalty = Param (default=5000.0)
model.LoadShed_c_penalty = Param (default=5000.0)

model.InterfaceLimit_penalty = Param (default=950.0)

def costObj(model):
    expr = model.BaseMVA* (sum(model.pgi[i]*model.GenCost_segmentPrice[i] for i in model.GENCOST) \
                + model.SR_price*sum(model.sr[g] for g in model.GEN)  \
                + model.SR_penalty*sum(model.srReqSlackVar[g] for g in model.GEN)  \
                + model.BrcFlowLimit_penalty*sum(model.brcFlowLimitSlackVar[k] for k in model.BRANCH) \
                + model.LoadShed_penalty*sum(model.loadShed[d] for d in model.LOAD) \
                + model.PgMax_penalty*sum(model.pgmaxSlackVar[g] for g in model.GEN) \
                + model.PgMin_penalty*sum(model.pgminSlackVar[g] for g in model.GEN) \
                + model.energyRampUp_penalty*sum(model.energyRampUpSlackVar[g] for g in model.GEN) \
                + model.energyRampDown_penalty*sum(model.energyRampDownSlackVar[g] for g in model.GEN) \
                + model.spinRamp_penalty*sum(model.spinRampSlackVar[g] for g in model.GEN) \
                + model.InterfaceLimit_penalty*sum(model.interfaceLimiteSlackVar[k] for k in model.INTERFACE) \
                + model.LoadShed_c_penalty*sum(model.loadShed_c[c, d] for c in model.CONTINGENCY for d in model.LOAD) )
    return expr
model.minimizeCost = Objective(rule=costObj)  # by default, sense = minimize

