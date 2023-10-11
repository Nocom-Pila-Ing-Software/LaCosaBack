from fastapi import HTTPException
from models import Game, Player
from ..schemas import GameStatus, PublicPlayerInfo
from schemas.schemas import PlayerID, CardInfo
import lacosa.game.utils.utils as utils


class GameStatusHandler:
    def __init__(self, room_id):
        self.game = utils.find_game(room_id)

    def get_response(self) -> None:
        players = []
        dead_players = []
        last_card = CardInfo(cardID=-1, name="", description="")
        if self.game.last_played_card:
            last_card = CardInfo(
                cardID=self.game.last_played_card.id,
                name=self.game.last_played_card.name,
                description=self.game.last_played_card.description,
            )

        for player in self.game.players.order_by(Player.position):
            if player.is_alive:
                player_info = PublicPlayerInfo(
                    playerID=player.id,
                    username=player.username,
                    is_host=player.is_host,
                    is_alive=player.is_alive
                )
                players.append(player_info)
            else:
                player_info = PublicPlayerInfo(
                    playerID=player.id,
                    username=player.username,
                    is_host=player.is_host,
                    is_alive=player.is_alive
                )
                dead_players.append(player_info)

        response = GameStatus(
            gameID=self.game.id,
            players=players,
            deadPlayers=dead_players,
            lastPlayedCard=last_card,
            playerPlayingTurn=PlayerID(playerID=self.game.current_player)
        )
        return response
