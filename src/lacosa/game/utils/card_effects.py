from models import Player, Game
from collections.abc import Callable


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


def get_card_effect_function(card_name: str) -> Callable[[Player, Game], None]:
    match card_name:
        case "Lanzallamas":
            return apply_lanzallamas_effect
        case _:
            return do_nothing
