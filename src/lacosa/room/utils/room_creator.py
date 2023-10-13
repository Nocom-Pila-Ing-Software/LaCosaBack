from pony.orm import commit
from models import WaitingRoom, Player
from ..schemas import RoomCreationRequest, RoomCreationResponse
import lacosa.room.utils.exceptions as exceptions


class RoomCreator:
    def __init__(self, creation_request: RoomCreationRequest):
        self.host_name = creation_request.hostName
        self.room_name = creation_request.roomName
        self.room: WaitingRoom
        self.host: Player

        exceptions.validate_unique_room_name(self.room_name)

    def create(self):
        self.room = self._create_room_on_db()
        self.host = self._create_host_on_db()

    def get_response(self):
        response = RoomCreationResponse(
            roomID=self.room.id,
            playerID=self.host.id
        )
        return response

    def _create_host_on_db(self) -> Player:
        """
        Creates a new host for a room on the database

        Args:
        room (WaitingRoom): The room to create the host for

        Returns:
        int: The id of the new host
        """
        new_host = self.room.players.create(
            username=self.host_name,
            is_host=True,
            position=1
        )
        commit()
        return new_host

    def _create_room_on_db(self) -> WaitingRoom:
        """
        Creates a new room on the database

        Args:
        creation_request (RoomCreationRequest): Input data to validate

        Returns:
        WaitingRoom: The created room
        """
        new_room = WaitingRoom(
            room_name=self.room_name
        )
        commit()
        return new_room
