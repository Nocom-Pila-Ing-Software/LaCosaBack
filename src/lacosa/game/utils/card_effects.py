from models import Player, Game
from collections.abc import Callable
from typing import Dict

CardEffectFunc = Callable[[Player, Game], None]


def update_player_positions_after_death(player, game):
    for p in game.players:
        if p.position > player.position:
            p.position -= 1
    player.position = 0


def apply_lanzallamas_effect(target_player: Player, game: Game) -> None:
    target_player.is_alive = False
    update_player_positions_after_death(target_player, game)


def do_nothing(target_player: Player, game: Game):
    pass


def get_card_effect_function(card_name: str) -> CardEffectFunc:
    _card_effects: Dict[str, CardEffectFunc] = {
        "Lanzallamas": apply_lanzallamas_effect
    }

    return _card_effects.get(card_name, do_nothing)
