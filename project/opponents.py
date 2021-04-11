from typing import NamedTuple, List

from project.types import PokedexId


class OpponentInfo(NamedTuple):
    opponent_name: str
    pokemons: List[PokedexId]  # Six pokedex Ids


agatha = OpponentInfo(opponent_name="Agatha", pokemons=[
    94,  # gengar
    42,  # golbat
    93,  # haunter
    24,  # arbok
    94  # gengar
])

loreli = OpponentInfo(opponent_name="Lorei", pokemons=[
    87,  # steelix
    91,  # cloyster
    80,  # slowbro
    124,  # jynx
    131  # lapras
])

bruno = OpponentInfo(opponent_name="Bruno", pokemons=[
    95,  # onix
    95,  # onix
    107,
    106,
    68
])

lance = OpponentInfo(opponent_name="Lance", pokemons=[
    130,
    149,
    149,
    142,
    148
])

champion_venusaur = OpponentInfo(opponent_name="Champion (Venusaur)", pokemons=[
    18,
    65,
    112,
    130,
    59,
    3
])

champion_charizard = OpponentInfo(opponent_name="Champion (Charizard)", pokemons=[
    18,
    65,
    112,
    130,
    59,
    6
])

champion_blastoise = OpponentInfo(opponent_name="Champion (Blastoise)", pokemons=[
    18,
    65,
    112,
    130,
    59,
    9
])

custom = OpponentInfo(opponent_name="Custom opponent", pokemons=[
    1,
    2,
    3,
    4,
    5,
    6
])