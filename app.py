from math import ceil, floor
from typing import *
import streamlit as st
import pathlib
import pandas as pd

from project.dataset import load_dataset
from project.opponents import OpponentInfo, agatha, loreli, bruno, lance, champion, custom
from project.optim_model import run_model
from project.types import PokedexId

"""## Choose your opponent"""

opponents: Dict[str, OpponentInfo] = {
    agatha.opponent_name: agatha,
    loreli.opponent_name: loreli,
    bruno.opponent_name: bruno,
    lance.opponent_name: lance,
    champion.opponent_name: champion,
    custom.opponent_name: custom
}

selected_opponent_key: str = st.selectbox(
    "",
    list(opponents.keys())
)

selected_opponent: OpponentInfo = opponents[selected_opponent_key]

# data has attributes name, pokedex_number
data, t, x, damage = load_dataset()
name_to_pokedex_number: Dict[str, PokedexId] = dict(zip(data.name, data.pokedex_number))


def to_mat_idx(pokemon_id: PokedexId):
    return pokemon_id - 1  # should do data[data.pokedex_number == pokemon_id].index[0] if order is not assured


def fetch_image_path(pokemon_id: PokedexId) -> pathlib.Path:
    """Constructs png path based on pokemon_id"""
    return pathlib.Path(f"project/black_white_sprites/{pokemon_id}.png")


def draw_pokemons(pokemon_ids: List[PokedexId]):
    images: List[str] = []
    for pokemon_id in pokemon_ids:
        images.append(str(fetch_image_path(pokemon_id=pokemon_id)))
    st.image(images)


"""## Selected Opponent"""
st.write(selected_opponent.opponent_name)

if selected_opponent_key == custom.opponent_name:
    # custom opponent
    columns = st.beta_columns(6)
    custom_opponent_pokemon = [None] * 6
    for idx, column in enumerate(columns):
        with column:
            custom.pokemons[idx] = name_to_pokedex_number[st.selectbox(
                "",
                options=list(data.name),
                index=custom.pokemons[idx] - 1,  # hack to show custom opponent pokemon on start
                key=f"custom_{idx}"
            )]
draw_pokemons(selected_opponent.pokemons)


# todo: make into class
def get_names(data: pd.DataFrame, pokedex_ids: List[PokedexId]):
    """data: pd.DataFrame with attribute pokedex_number, and name"""
    return [data[data.pokedex_number == id].name.iloc[0] for id in pokedex_ids]


def get_type_1(data: pd.DataFrame, pokedex_ids: List[PokedexId]):
    """data: pd.DataFrame with attribute pokedex_number, and type_1"""
    return [data[data.pokedex_number == id].type_1.iloc[0] for id in pokedex_ids]


def get_type_2(data: pd.DataFrame, pokedex_ids: List[PokedexId]):
    """data: pd.DataFrame with attribute pokedex_number, and type_2"""
    return [data[data.pokedex_number == id].type_2.iloc[0] for id in pokedex_ids]


def get_hp(data: pd.DataFrame, pokedex_ids: List[PokedexId]):
    """data: pd.DataFrame with attribute pokedex_number, and calculated_hp"""
    return [data[data.pokedex_number == id].calculated_hp.iloc[0] for id in pokedex_ids]


def to_mat_idx(pokemon_id: PokedexId):
    return data[data.pokedex_number == pokemon_id].index[0]


def get_turns_to_defeat(x: pd.DataFrame, team_ids: List[PokedexId], opponent_ids: List[PokedexId]):
    """x: NxN matrix indicating turns to defeat opponent pokemon"""
    return [floor(x.iloc[to_mat_idx(team_id), to_mat_idx(opponent_id)]) for team_id, opponent_id in
            zip(team_ids, opponent_ids)]


def get_turn_difference(t: pd.DataFrame, team_ids: List[PokedexId], opponent_ids: List[PokedexId]):
    """t: NxN matrix indicating turn difference aainst opponent pokemon"""
    return [floor(t.iloc[to_mat_idx(team_id), to_mat_idx(opponent_id)]) for team_id, opponent_id in
            zip(team_ids, opponent_ids)]


def get_damage(d: pd.DataFrame, team_ids: List[PokedexId], opponent_ids: List[PokedexId]):
    """d: NxN matrix indicating damage agaun opponent pokemon"""
    return [floor(d.iloc[to_mat_idx(team_id), to_mat_idx(opponent_id)]) for team_id, opponent_id in
            zip(team_ids, opponent_ids)]


opponent_table = pd.DataFrame(
    [get_type_1(data, selected_opponent.pokemons),
     get_type_2(data, selected_opponent.pokemons),
     get_hp(data, selected_opponent.pokemons),
     [60] * len(selected_opponent.pokemons)
     ],
    columns=get_names(data, selected_opponent.pokemons), index=['Type 1', 'Type 2', 'Hitpoints', 'Level'])

opponent_table  # draw opponent table

"""## Banned pokemon"""

banned_pokemon: List[PokedexId] = [None]  # todo: some optimizaitons with st.empty() so you don't have to redraw page


def draw_banned_pokemon():
    for idx, pokemon_id in enumerate(banned_pokemon):
        selected = st.selectbox(
            "",
            options=[None] + list(data.name),
            key=f"banned_{idx}"
        )
        blank_slot = st.empty()
        if selected is not None:  # Otherwise this will draw infinitely
            # sum(c[to_mat_idx(pokedex_id), j] for pokedex_id in banned_pokemon) == 0
            # for j in range(no_opponents)
            mat_idx = to_mat_idx(name_to_pokedex_number[selected])
            blank_slot.write(
                f"Added constraint: $C_{{{mat_idx},j}} = 0$ for all $j \in$ Opponent Pokemons")
            banned_pokemon.append(name_to_pokedex_number[selected])


draw_banned_pokemon()
"""## Optimal team"""


def draw_objective_function():
    objective_function = st.selectbox("Objective function",
                                      options=["Maximise turns difference against opponent",
                                               "Minimize turns needed to win"]
                                      , index=1)
    blank_slot_1 = st.empty()
    turn_difference_chosen = objective_function == "Maximise turns difference against opponent"
    if turn_difference_chosen:
        blank_slot_1.write(
            "Objective Function: $max \sum_{i \in{A}} \sum_{j \in{O}} C_{ij} T_{ij}$ where $A$ denotes the set of "
            "all pokemons and $O$ denotes the set of pokemon opponents")

    else:
        blank_slot_1.write(
            "Objective Function: $min \sum_{i \in{A}} \sum_{j \in{O}} C_{ij} X_{ij}$ where $A$ denotes the set of "
            "all pokemons and $O$ denotes the set of pokemon opponents")
    return turn_difference_chosen


turn_difference_chosen = draw_objective_function()

unique_pokemon = st.checkbox("Enforce pokemon to be unique", value=True)
blank_slot = st.empty()  # no need to render below elements by using a blank slot
if unique_pokemon:
    blank_slot.write(
        "Added constraint: $C_{i,j} \leq 1$ for all $j \in$ Opponent Pokemons")

min_turn_difference = st.slider("Minimum turn difference", min_value=0, max_value=20, step=1)
st.write(
    f"Added constraint: $C_{{i,j}} T_{{i,j}} \geq {min_turn_difference}$ for all $i \in$ Selected Pokemons and $j \in$ Opponent Pokemons")

try:
    best_team: List[PokedexId] = run_model(data=data, t=t, x=x, opponents=selected_opponent.pokemons,
                                           enforce_unique_pokemon=unique_pokemon,
                                           maximise_turn_difference=turn_difference_chosen,
                                           banned_pokemon=[poke_id for poke_id in banned_pokemon if
                                                           poke_id is not None],
                                           min_turn_difference=min_turn_difference)
except AttributeError as e:
    raise AssertionError("Infeasible Model")  # Catch to show this rather than ugly attribute error.

draw_pokemons(best_team)

optimal_team_table = pd.DataFrame(
    [
        get_names(data, selected_opponent.pokemons),
        get_turns_to_defeat(x=x, team_ids=best_team, opponent_ids=selected_opponent.pokemons),
        get_turns_to_defeat(x=x, team_ids=selected_opponent.pokemons, opponent_ids=best_team),
        get_turn_difference(t=t, team_ids=best_team, opponent_ids=selected_opponent.pokemons),
        get_damage(d=damage, team_ids=best_team, opponent_ids=selected_opponent.pokemons),
        get_damage(d=damage, team_ids=selected_opponent.pokemons, opponent_ids=best_team),
        get_type_1(data, best_team),
        get_type_2(data, best_team),
        get_hp(data, best_team),
        [60] * len(best_team)
    ],
    columns=get_names(data, best_team),
    index=['Against opponent', 'Turns to defeat opponent', 'Turns to be defeated', 'Turn difference against opponent',
           'Damage against opponent', 'Damage from opponent', 'Type 1', 'Type 2', 'Hitpoints', 'Level'])

optimal_team_table
