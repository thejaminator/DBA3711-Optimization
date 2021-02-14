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

    # Set constraints
    for single_month_loan, liab, rev in zip(loans_per_month, liab_per_month, rev_per_month):
        m.addConstr(six_month_loan + single_month_loan >= liab - rev, name="Requirements per month")

    m.addConstr(six_month_loan >= 0, name="Non negativity")
    for single_month_loan in loans_per_month:
        m.addConstr(single_month_loan >= 0, name="Non negativity")

    m.optimize()

    # # print optimal solutions
    for v in m.getVars():
        print('%s = %d' % (v.varName, v.x))

    # print optimal value
    print('Obj: %g' % m.objVal)

    # print dual values to all constraints
    print(m.getAttr("Pi", m.getConstrs()))


qn1()
