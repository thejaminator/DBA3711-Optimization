from typing import List, Dict

import streamlit as st
import numpy as np
import pandas as pd
from gurobipy import *

from project.types import PokedexId


@st.cache
def run_model(data: pd.DataFrame, x: pd.DataFrame,
              t: pd.DataFrame,
              opponents: List[PokedexId],
              enforce_unique_pokemon: bool,
              use_max_turn_diff_obj: bool,
              banned_pokemon: List[PokedexId],
              must_have_pokemon: List[PokedexId],
              min_turn_difference: int = 0,

              ) -> List[PokedexId]:
    """Returns list of optimal pokedex pokemon ids, sorted in same order as the opponents"""

    def to_mat_idx(pokemon_id: PokedexId):
        return pokemon_id - 1  # should do data[data.pokedex_number == pokemon_id].index[0] if order is not assured

    no_pokemons = len(data)
    no_opponents = len(opponents)
    # preparing an optimization model
    mod = Model("pokemon")

    # declaring variables
    c = mod.addVars(no_pokemons, no_opponents, name='c')

    # setting the objective such that it helps us end the game as fast as possible
    # but if want to make it safer, we should maximise the turn difference:
    if use_max_turn_diff_obj:
        mod.setObjective(
            sum(c[i, j] * t.iloc[i, opponents[j] - 1] for i in range(no_pokemons) for j in range(no_opponents)),
            GRB.MAXIMIZE)
    else:
        mod.setObjective(
            sum(c[i, j] * x.iloc[i, opponents[j] - 1] for i in range(no_pokemons) for j in range(no_opponents)),
            GRB.MINIMIZE)

    # adding constraints
    # comment next line out if want to remove constraint of only one of each pokemon in pokedex
    if enforce_unique_pokemon:
        mod.addConstrs(sum(c[i, j] for j in range(no_opponents)) <= 1 for i in range(no_pokemons))
    mod.addConstrs(sum(c[i, j] for i in range(no_pokemons)) == 1 for j in range(no_opponents))
    # chosen pokemons must be able to defeat opponent (no negative turn difference or less than min_turn_difference)
    mod.addConstrs((c[i, j] == 1) >> (c[i, j] * t.iloc[i, opponents[j] - 1] >= min_turn_difference)
                   for i in range(no_pokemons) for j in range(no_opponents))

    # for pokemons who are slower and turn difference < 1, they would be first defeated by opponent
    mod.addConstrs(c[i, j] == 0 for i in range(no_pokemons) for j in range(no_opponents) if
                   (data.calculated_speed[j] >= data.calculated_speed[i]) & (t.iloc[i, opponents[j] - 1] < 1))

    # optional - banned pokemon
    mod.addConstrs(sum(c[to_mat_idx(pokedex_id), j] for pokedex_id in banned_pokemon) == 0 for j in range(no_opponents))

    # optional - must have pokemon
    if len(must_have_pokemon) > 0:
        mod.addConstrs(
            sum(c[to_mat_idx(pokedex_id), j] for j in range(no_opponents)) == 1 for pokedex_id in must_have_pokemon)

    # solving the optimization problem
    mod.optimize()

    # print optimal value
    print('\nOptimal: %g\n' % mod.objVal)

    # print optimal solutions
    print('Optimal Assignment:')
    optimal_pokemons: List[int] = [None] * no_opponents  # hack to make empty list to assign the results in order
    for index, v in c.items():  # index[0] is the best pokemon to fight against the opponent
        if v.getAttr("x") == 1:
            print("Pokemon {i} should battle pokemon {j}".format(i=data.name[index[0]],
                                                                 j=data.name[opponents[index[1]] - 1]))
            optimal_pokemon = data.pokedex_number[index[0]]
            opponent_idx = index[1]  # this is not returned in order, so we need to assign it directly
            optimal_pokemons[opponent_idx] = optimal_pokemon
    return optimal_pokemons
