from pony.orm import commit
import lacosa.utils as utils


def delete_room(room_id: int) -> None:
    """
    Delete a room from the database.

    Args:
        room_ID (int): The ID of the room to delete.
    """
    room = utils.find_room(room_id)
    room.delete()
    commit()
