from models import Player
from ..schemas import GameStatus, PublicPlayerInfo
from lacosa.schemas import PlayerID, CardInfo
from ...room.utils.room_operations import delete_room
import lacosa.utils as utils
from lacosa.interfaces import ResponseInterface


class GameStatusHandler(ResponseInterface):
    def __init__(self, room_id):
        self.game = utils.find_game(room_id)
        self.players, self.dead_players = self._get_player_info()
        self.last_card = self._get_last_card_info()
        self.is_game_over = self._is_game_over()

    def get_response(self) -> GameStatus:
        response = GameStatus(
            gameID=self.game.id,
            players=self.players,
            deadPlayers=self.dead_players,
            lastPlayedCard=self.last_card,
            playerPlayingTurn=PlayerID(playerID=self.game.current_player),
            currentAction=self.game.current_action,
            result={
                "isGameOver": self.is_game_over,
                "humansWin": False,
                "winners": self._get_player_info()[1]
            },
            events=[],
        )
        return response

    def _is_game_over(self):
        return len(self.players) == 1

    def _get_player_schema(self, player):
        return PublicPlayerInfo(
            playerID=player.id,
            username=player.username,
            is_host=player.is_host,
            is_alive=player.is_alive
        )

    def _get_player_info(self):
        players = self.game.players.order_by(Player.position)
        alive_players = [
            self._get_player_schema(player) for player in players if player.is_alive
        ]
        dead_players = [
            self._get_player_schema(player) for player in players if not player.is_alive
        ]

        return alive_players, dead_players

    def _get_last_card_info(self):
        card_info = {"cardID": -1, "name": "", "description": ""}

        last_played_card = self.game.last_played_card
        if last_played_card:
            card_info = {
                "cardID": last_played_card.id,
                "name": last_played_card.name,
                "description": last_played_card.description
            }

        return CardInfo(**card_info)

    def delete_if_game_over(self, response: GameStatus) -> None:
        if response.result.isGameOver:
            # Delete deck
            for card in self.game.cards:
                card.delete()

            # Delete hands
            for player in self.game.players:
                for card in player.cards:
                    card.delete()

            delete_room(self.game.waiting_room.id)
