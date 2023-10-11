from models import Player


def apply_lanzallamas_effect(target_player: Player) -> None:
    target_player.is_alive = False
