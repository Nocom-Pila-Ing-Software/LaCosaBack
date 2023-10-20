from pony.orm import commit
import lacosa.utils as utils
from models import WaitingRoom


def delete_room(room: WaitingRoom) -> None:
    """
    Delete a room from the database.

    Args:
        room_ID (int): The ID of the room to delete.
    """
    room.delete()
    commit()
