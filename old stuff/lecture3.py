import gurobipy as grb


"""
Custom Molder problem
Suppose that a custom molder has one injection-molding machine with two different dies to fit the machine.
Due to differences in number of cavities and cycle times, with the first die he can produce 100 cases
of six-ounce juice glasses in six hours, while with the second die he can produce
100 cases of ten-ounce fancy cocktail glasses in five hours. He
prefers to operate only on a schedule of 60 hours of production per week. He stores
the week's production in his own stockroom where he has an effective capacity of 15,000
cubic feet. A case of six-ounce juice glasses requires 10 cubic feet of
storage space, while a case of ten-ounce cocktail glasses requires 20 cubic
feet due to special packaging. The contribution of the six-ounce glasses is $5.00 per
case; however, the only customer available will not accept more than 800 cases per week.
The contribution of ten-ounce cocktail glasses is $4.50 per case and there is
no limit on the amount that can be sold.


        6ounce 5 ounce
ProfitM 500, 450       c1    x2
Time    6 ,5       a11 a12   b1  60
Space   1000, 2000 a21 a22   b2  15000
Demand  800                 b3  800

"""


def main():
    # model = grb.Model("Linear P example")
    # x1 = model.addVar(vtype=grb.GRB.INTEGER, name="x1")
    # x2 = model.addVar(vtype=grb.GRB.INTEGER, name="x2")
    # x3 = model.addVar(vtype=grb.GRB.INTEGER, name="x3")
    #
    # model.setObjective(60 * x1 + 30 * x2 + 20 * x3, sense=grb.GRB.MAXIMIZE)
    # model.addConstr(8 * x1 + 6 * x2 + x3 <= 48, name="Wood Available")
    # model.addConstr(4 * x1 + 2 * x2 + 1.5 * x3 <= 20, name="Finishing Labour")
    # model.addConstr(2 * x1 + 1.5 * x2 + 0.5 * x3 <= 8, name="Carpentry")
    #
    # model.optimize()
    # for variable in model.getVars():
    #     print(f"{variable.varName} = {variable.x}")
    #
    # print(f"Objective {model.objVal}")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
