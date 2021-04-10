
from typing import List

import pandas as pd
from gurobipy import *


def run_model(data: pd.DataFrame, x: pd.DataFrame,
              t: pd.DataFrame,
              opponents: List[int]) -> List[int]:
    no_pokemons = len(data)
    no_opponents = len(opponents)
    # preparing an optimization model
    mod = Model("pokemon")

    # declaring variables
    c = mod.addVars(no_pokemons, no_opponents, name='c')

    # setting the objective such that it helps us end the game as fast as possible
    # but if want to make it safer, we should maximise the turn difference:
    # mod.setObjective(sum(c[i,j]*t.iloc[i,j] for i in range(no_pokemons) for j in range(no_opponents)), GRB.MAXIMIZE)
    mod.setObjective(
        sum(c[i, j] * x.iloc[i, opponents[j] - 1] for i in range(no_pokemons) for j in range(no_opponents)),
        GRB.MINIMIZE)

    # adding constraints
    # comment next line out if want to remove constraint of only one of each pokemon in pokedex
    mod.addConstrs(sum(c[i, j] for j in range(no_opponents)) <= 1 for i in range(no_pokemons))
    mod.addConstrs(sum(c[i, j] for i in range(no_pokemons)) == 1 for j in range(no_opponents))
    # chosen pokemons must be able to defeat opponent (no negative turn difference)
    mod.addConstrs(c[i, j] * t.iloc[i, opponents[j] - 1] >= 0 for i in range(no_pokemons) for j in range(no_opponents))

    # for pokemons who are slower and turn difference < 1, they would be first defeated by opponent
    mod.addConstrs(c[i, j] == 0 for i in range(no_pokemons) for j in range(no_opponents) if
                   (data.calculated_speed[j] >= data.calculated_speed[i]) & (t.iloc[i, opponents[j] - 1] < 1))
    # solving the optimization problem
    mod.optimize()

    # print optimal value
    print('\nOptimal: %g\n' % mod.objVal)

    # print optimal solutions
    print('Optimal Assignment:')
    optimal_pokemons: List[int] = []
    for index, v in c.items(): # index[0] is the best pokemon to fight against the opponent
        if v.getAttr("x") == 1:
            print("Pokemon {i} should battle pokemon {j}".format(i=data.name[index[0]],
                                                                 j=data.name[opponents[index[1]] - 1]))
            print(data.pokedex_number[index[0]])
            optimal_pokemons.append(data.pokedex_number[index[0]])
    return optimal_pokemons
