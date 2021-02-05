import gurobipy as grb


def main():
    model = grb.Model("Linear P example")
    x1 = model.addVar(vtype=grb.GRB.INTEGER, name="x1")
    x2 = model.addVar(vtype=grb.GRB.INTEGER, name="x2")
    x3 = model.addVar(vtype=grb.GRB.INTEGER, name="x3")

    model.setObjective(60 * x1 + 30 * x2 + 20 * x3, sense=grb.GRB.MAXIMIZE)
    model.addConstr(8 * x1 + 6 * x2 + x3 <= 48, name="Wood Available")
    model.addConstr(4 * x1 + 2 * x2 + 1.5 * x3 <= 20, name="Finishing Labour")
    model.addConstr(2 * x1 + 1.5 * x2 + 0.5 * x3 <= 8, name="Carpentry")

    grb.quicksum

    model.optimize()
    for variable in model.getVars():
        print(f"{variable.varName} = {variable.x}")

    print(f"Objective {model.objVal}")
    model.getAttr()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
