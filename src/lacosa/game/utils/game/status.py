from models import Player
from ...schemas import GameStatus, PublicPlayerInfo
from lacosa.schemas import PlayerID, CardInfo
from lacosa.room.utils.room_operations import delete_room
from lacosa.game.utils import event_serializer
import lacosa.utils as utils
from lacosa.interfaces import ResponseInterface


class GameStatusHandler(ResponseInterface):
    def __init__(self, room_id):
        self.game = utils.find_game(room_id)
        self.players, self.dead_players = self._get_player_info()
        self.last_card = self._get_last_card_info()

    def get_events(self):
        completed_events = self.game.events.filter(lambda x: x.is_completed)
        result = [event_serializer.get_event_text(
            event) for event in completed_events]
        return result

    def get_response(self) -> GameStatus:
        response = GameStatus(
            gameID=self.game.id,
            players=self.players,
            deadPlayers=self.dead_players,
            lastPlayedCard=self.last_card,
            playerPlayingTurn=PlayerID(playerID=self.game.current_player),
            currentAction=self.game.current_action,
            result=self.get_result_schema(),
            events=self.get_events(),
        )
        return response

    def get_result_schema(self):
        return {
            "isGameOver": self.game.is_game_over,
            "humansWin": self.game.have_humans_won,
            "winners": [],
        }

    def _get_player_schema(self, player):
        return PublicPlayerInfo(
            playerID=player.id,
            username=player.username,
            is_host=player.is_host,
            is_alive=player.is_alive,
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
                "description": last_played_card.description,
            }

        return CardInfo(**card_info)
