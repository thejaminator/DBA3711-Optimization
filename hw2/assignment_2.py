from typing import Set, List, Dict
from gurobipy import *


def qn1():
    # Create a new model
    m: Model = Model("loans")

    # Six month loan
    six_month_loan = m.addVar(name="six_month_loan_value")

    n_months = 6

    month_names = ["jul", "aug", "sep", "oct", "nov", "dec"]
    liab_per_month = [50000, 60000, 50000, 60000, 50000, 30000]
    rev_per_month = [20000, 30000, 40000, 50000, 80000, 100000]
    loans_per_month = []
    # Create variables that indicate loan for each month
    for month in month_names:
        loans_per_month.append(m.addVar(name="loan_value for month " + month))

    # Set objective
    m.setObjective(0.04 * sum(loans_per_month) + 0.12 * six_month_loan, GRB.MINIMIZE)

    n1 = six_month_loan + loans_per_month[0] + rev_per_month[0] - liab_per_month[0]
    n2 = n1 + loans_per_month[1] + rev_per_month[1] - liab_per_month[1] - 1.04*loans_per_month[0]
    n3 = n2 + loans_per_month[2] + rev_per_month[2] - liab_per_month[2] - 1.04 * loans_per_month[1]
    n4 = n3 + loans_per_month[3] + rev_per_month[3] - liab_per_month[3] - 1.04 * loans_per_month[2]
    n5 = n4 + loans_per_month[4] + rev_per_month[4] - liab_per_month[4] - 1.04 * loans_per_month[3]
    n6 = n5 + loans_per_month[5] + rev_per_month[5] - liab_per_month[5] - 1.04 * loans_per_month[4]



    m.addConstr(six_month_loan >= 0, name="Non negativity")
    for single_month_loan in loans_per_month:
        m.addConstr(single_month_loan >= 0, name="Non negativity")

    m.addConstr(n1 >= 0, name="Cashflow")
    m.addConstr(n2 >= 0, name="Cashflow")
    m.addConstr(n3 >= 0, name="Cashflow")
    m.addConstr(n4 >= 0, name="Cashflow")
    m.addConstr(n5 >= 0, name="Cashflow")
    m.addConstr(n6 >= 0, name="Cashflow")


    m.optimize()

    # # print optimal solutions
    for v in m.getVars():
        print('%s = %f' % (v.varName, v.x))

    # print optimal value
    print('Obj: %g' % m.objVal)

    # print dual values to all constraints
    print(m.getAttr("Pi", m.getConstrs()))


qn1()

def qn2():
    # Create a new model
    m: Model = Model("advertising")

    # Sets
    types_of_ads = set(["tv", "newspaper", "radio"])
    genders = set(["male", "female"])
    age_brackets = set(["senior", "young"])

    # Variables
    number_ads = m.addVars(types_of_ads,  name="number_ads")

    # if we wanted to do integer programming
    # number_ads = m.addVars(types_of_ads, vtype = GRB.INTEGER, name="number_ads")

    # Parameters constants
    audience_reached = {
        ("tv", "male", "senior"): 5000,
        ("tv", "male", "young"): 5000,
        ("tv", "female", "senior"): 5000,
        ("tv", "female", "young"): 10000,

        ("newspaper", "male", "senior"): 4000,
        ("newspaper", "male", "young"): 2000,
        ("newspaper", "female", "senior"): 3000,
        ("newspaper", "female", "young"): 1000,

        ("radio", "male", "senior"): 1500,
        ("radio", "male", "young"): 4500,
        ("radio", "female", "senior"): 1500,
        ("radio", "female", "young"): 7500
    }

    costs = {"tv": 15000, "newspaper": 4000, "radio": 6000}

    # Objective
    m.setObjective(quicksum(costs[ad_type] * number_ads[ad_type] for ad_type in types_of_ads), GRB.MINIMIZE)

    # Subject to constraints
    # a
    m.addConstr(
        quicksum([number_ads["radio"] * audience_reached["radio", j, k]
                  for j in genders
                  for k in age_brackets]) >=
        2 * quicksum([number_ads["newspaper"] * audience_reached["newspaper", j, k]
                      for j in genders
                      for k in age_brackets]))

    # b
    total_audience = quicksum([number_ads[i] * audience_reached[i, j, k]
                               for i in types_of_ads
                               for j in genders
                               for k in age_brackets])
    m.addConstr(total_audience >= 100000)

    # c
    m.addConstr(
        quicksum([number_ads[i] * audience_reached[i, j, "young"]
                  for i in types_of_ads
                  for j in genders]) >=
        2 * quicksum([number_ads[i] * audience_reached[i, j, "senior"]
                      for i in types_of_ads
                      for j in genders]))

    # d
    m.addConstr(
        quicksum([number_ads[i] * audience_reached[i, "female", k]
                  for i in types_of_ads
                  for k in age_brackets]) >= 0.6 * total_audience)

    # e
    m.addConstr(number_ads["newspaper"] <= 7)

    m.optimize()

    # # print optimal solutions
    for v in m.getVars():
        print(f"{v.varName} = {v.x}")

    # # print optimal value
    # print('Obj: %g' % m.objVal)
    #
    # # print dual values to all constraints
    # print(m.getAttr("Pi", m.getConstrs()))


# qn2()
