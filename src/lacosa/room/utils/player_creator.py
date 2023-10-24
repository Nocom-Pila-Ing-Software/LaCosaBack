from lacosa.schemas import PlayerName, PlayerID
from pony.orm import commit
from models import Player
import lacosa.utils as utils
import lacosa.room.utils.exceptions as exceptions
from lacosa.interfaces import ResponseInterface, CreatorInterface


class PlayerCreator(ResponseInterface, CreatorInterface):
    def __init__(self, player_name_payload: PlayerName, room_id: int):
        self.player_name = player_name_payload.playerName
        self.room = utils.find_room(room_id)
        self.player: Player
        self._handle_errors()

    def create(self) -> Player:
        """
        Create a new player and add them to the database.

        Args:
            player_name (PlayerName): The player's name.
            room_ID (int): The ID of the room to which the player will be added.

        Returns:
            Player: The created player.
        """

        self.player = self.room.players.create(
            username=self.player_name
        )
        commit()

    def get_response(self):
        response = PlayerID(playerID=self.player.id)
        return response

    def _handle_errors(self) -> None:
        """
        Handle the errors that may occur when adding a player to a room.

        Args:
            player_name (PlayerName): The player's name.
        room_ID (int): The ID of the room to which the player will be added.

        Raises:
            HTTPException: If any of the errors occur, raise an HTTP exception with a status code of 400.
        """
        exceptions.check_valid_player_name(self.player_name)
        exceptions.check_player_name_is_unique(self.player_name, self.room)
        exceptions.check_game_started(self.room)
