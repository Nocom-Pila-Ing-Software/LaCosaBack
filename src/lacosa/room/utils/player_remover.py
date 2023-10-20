from lacosa.schemas import PlayerID
from pony.orm import commit
import lacosa.utils as utils
import lacosa.room.utils.exceptions as exceptions
from lacosa.interfaces import ActionInterface
import lacosa.room.utils.room_operations as room_operations


class PlayerRemover(ActionInterface):
    def __init__(self, player_name_payload: PlayerID, room_id: int):
        self.room = utils.find_room(room_id)
        self.player = utils.find_player(player_name_payload.playerID)
        exceptions.validate_player_in_room(self.player.id, self.room)
        exceptions.check_game_started(self.room)

    def execute_action(self) -> None:
        if self.player.is_host:
            room_operations.delete_room(self.room)
        else:
            self.player.delete()
        commit()
