from models import Player, Game
from collections.abc import Callable
from typing import Dict

CardEffectFunc = Callable[[Player, Game], None]


def update_player_positions_after_death(player, game):
    for p in game.players:
        if p.position > player.position:
            p.position -= 1
    player.position = 0


def switch_player_positions(player1: Player, player2: Player) -> None:
    player1.position, player2.position = player2.position, player1.position


def apply_lanzallamas_effect(current_player: Player, target_player: Player, game: Game) -> None:
    target_player.is_alive = False
    # TODO: Las cartas del jugador muerto deberian volver al juego?
    update_player_positions_after_death(target_player, game)


def apply_cambio_de_lugar_effect(current_player: Player, target_player: Player, game: Game) -> None:
    switch_player_positions(current_player, target_player)


def do_nothing(target_player: Player, game: Game):
    pass


def get_card_effect_function(card_name: str) -> CardEffectFunc:
    _card_effects: Dict[str, CardEffectFunc] = {
        "Lanzallamas": apply_lanzallamas_effect,
        "Cambio de lugar": apply_cambio_de_lugar_effect
    }

    return _card_effects.get(card_name, do_nothing)
