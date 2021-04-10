import json
import urllib
from typing import Tuple

import numpy as np
import streamlit as st
import pandas as pd
@st.cache
def load_dataset() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]: # data, t, x, d
    pokedex = pd.read_csv('project/pokedex.csv')
    moves = pd.read_csv('project/pokemon-moves.csv')
    url = 'https://raw.githubusercontent.com/Deskbot/Pokemon-Learnsets/master/output/gen3.json'
    with urllib.request.urlopen(url) as response:
        page_content = response.read()
    learnset = json.loads(page_content)

    # clean pokedex to 151 pokemons in generation 1 (pokemons available in firered/ leafgreen)
    pokedex = pokedex.drop(pokedex.columns[0], axis=1)
    pokedex_final = pokedex[pokedex['generation'] == 1].groupby('pokedex_number').first().reset_index()
    pokedex_final['lowercase_name'] = pokedex_final['name'].apply(lambda x: x.lower().replace(" ", ""))

    # restructure learnset to long format
    learnset_df = pd.DataFrame.from_dict(learnset, orient='index').reset_index()
    learnset_df['level'] = learnset_df['level'].apply(lambda x: list(x.values()))
    learnset_final = pd.melt(learnset_df, id_vars='index', var_name='learn_by', value_name='move').explode('move')

    # join learnset to move statistic table
    # moves:'willowisp', 'doubleedge', 'mudslap', 'selfdestruct', 'lockon','softboiled' do not have matches!
    moves['move'] = moves['Name'].apply(lambda x: x.lower().replace(" ", ""))
    moves_final = pd.merge(learnset_final, moves, on='move').drop(['Index'], axis=1)
    moves_final.columns = map(str.lower, moves_final.columns)

    # to find moves with no matches, use left join and below code
    # moves_final['move'][moves_final['name'].isna() & moves_final['move'].notnull()].unique()

    moves_final['power'] = pd.to_numeric(moves_final["power"], downcast="float", errors='coerce')
    # average power of moves by each pokemon
    avg_power = pd.DataFrame(moves_final.groupby('index')['power'].mean()).reset_index()

    avg_power.loc[avg_power.power.isna(), 'power'] = 0

    # pokemon names that cannot be matched: nidoranf and nidoranm, farfetch'd, mr.mime (need to remove ' and .)
    pokedex_final['lowercase_name'] = pokedex_final['lowercase_name'].str.replace('.', '').str.replace("'", '')
    pokedex_final.loc[pokedex_final.pokedex_number == 29, 'lowercase_name'] = 'nidoranf'
    pokedex_final.loc[pokedex_final.pokedex_number == 32, 'lowercase_name'] = 'nidoranm'
    data = pd.merge(pokedex_final, avg_power, left_on='lowercase_name', right_on='index')

    # calculating damage constant for each pokemon in pokedex
    level = 60
    ev = 100
    iv = 15
    data['calculated_hp'] = (2 * data.hp + iv + ev / 4) * level / 100 + level + 10
    data['calculated_attack'] = (2 * data.attack + iv + ev / 4) * level / 100 + 5
    data['calculated_defense'] = (2 * data.defense + iv + ev / 4) * level / 100 + 5
    data['calculated_speed'] = (2 * data.speed + iv + ev / 4) * level / 100 + 5

    # create 151 by 151 matrix for modifier for damage i inflicts on j (j's against_typeofpokemoni)
    data = data.rename({'against_fight': 'against_fighting'}, axis=1)

    pokemon_types = ["against_" + x.lower() for x in data.type_1]
    modifier_type1 = []
    for pokemon_i in range(len(data)):
        row_i = [data.iloc[pokemon_j][pokemon_types[pokemon_i]] for pokemon_j in range(len(data))]
        modifier_type1.append(row_i)
    modifier_type1 = pd.DataFrame(modifier_type1)

    pokemon_types2 = ["against_" + x.lower() if isinstance(x, str) else 'NA' for x in data.type_2]
    modifier_type2 = []
    for pokemon_i in range(len(data)):
        row_i = [data.iloc[pokemon_j][pokemon_types2[pokemon_i]] if pokemon_types2[pokemon_i] != 'NA' else np.nan for
                 pokemon_j in range(len(data))]
        modifier_type2.append(row_i)
    modifier_type2 = pd.DataFrame(modifier_type2)

    # make more effective "type"
    modifier = pd.concat((modifier_type1, modifier_type2)).groupby(level=0).max()

    # create 151 by 151 matrix for damage i inflicts on j
    d = pd.DataFrame(0, index=np.arange(len(data)), columns=np.arange(len(data)))
    for i in range(len(data)):
        for j in range(len(data)):
            d.iloc[i, j] = ((2 * level / 5 * data.power[i] * data.calculated_attack[i] / data.calculated_defense[
                j]) / 50 + 2) * modifier.iloc[i, j]

    # create 151 by 151 matrix for # turns i needs to defeat j
    x = pd.DataFrame(0, index=np.arange(len(data)), columns=np.arange(len(data)))
    for i in range(len(data)):
        for j in range(len(data)):
            if d.iloc[i, j] == 0:
                x.iloc[i, j] = 1000
            else:
                x.iloc[i, j] = data.calculated_hp[j] / d.iloc[i, j]

    # create 151 by 151 matrix for # turns j needs to defeat i
    y = x.transpose()

    # t is spare turns for i to defeat j
    t = y.apply(np.ceil) - x.apply(np.ceil)
    return (data, t, x, d)