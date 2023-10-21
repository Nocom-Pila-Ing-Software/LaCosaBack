from models import Player, Game
from collections.abc import Callable
from typing import Dict

CardEffectFunc = Callable[[Player, Game], None]


def update_player_positions_after_death(player, game):
    for p in game.players:
        if p.position > player.position:
            p.position -= 1
    player.position = 0

def swap_player_positions(player1, player2):
    player1.position, player2.position = player2.position, player1.position

def apply_lanzallamas_effect(target_player: Player, game: Game) -> None:
    target_player.is_alive = False
    update_player_positions_after_death(target_player, game)

def apply_cambio_de_lugar_effect(target_player: Player, game: Game) -> None:
    swap_player_positions = swap_player_positions(target_player, game.current_player)
    # evento para intercambiar carta con el jugador adyasente desde esta posicion
    # preguntar gonza


def do_nothing(target_player: Player, game: Game):
    pass


def get_card_effect_function(card_name: str) -> CardEffectFunc:
    _card_effects: Dict[str, CardEffectFunc] = {
        "Lanzallamas": apply_lanzallamas_effect,
        "Cambio de lugar": apply_cambio_de_lugar_effect
    }

    return _card_effects.get(card_name, do_nothing)
