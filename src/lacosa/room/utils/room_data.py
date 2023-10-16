from lacosa.schemas import PlayerName
from lacosa.room.schemas import RoomDataResponse
from typing import List
import lacosa.utils as utils
from lacosa.interfaces import ResponseInterface


class RoomStatusHandler(ResponseInterface):
    def __init__(self, room_id: int):
        self.room_id = room_id
        self.room = utils.find_room(room_id)

    def get_response(self):
        """
        Returns a RoomDataResponse object with the number of players in the room,
        the player names and if the room has started.
        """
        number_players = self._get_number_of_players_in_room()
        players_names_room = self._get_players_names_in_room()
        has_room_started = self._has_room_started()

        response = RoomDataResponse(
            CountPlayers=number_players,
            Players=players_names_room,
            hasStarted=has_room_started
        )

        return response

    def _get_number_of_players_in_room(self) -> int:
        return len(self.room.players)

    def _get_players_names_in_room(self) -> List[PlayerName]:
        players_names = [
            PlayerName(playerName=player.username) for player in self.room.players
        ]
        return players_names

    def _has_room_started(self):
        return self.room.game is not None
