from models import Game, Player, Card
from schemas.game import PlayCardRequest
from pony.orm import db_session


def effect_lanzallamas(target_player_id: int) -> None:
    target_player = Player.get(id=target_player_id)

    with db_session:
        target_player.is_alive = False
