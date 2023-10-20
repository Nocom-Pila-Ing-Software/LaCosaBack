from lacosa.room.schemas import RoomListingList, RoomListing
from lacosa.interfaces import ResponseInterface
from pony.orm import select
from models import WaitingRoom


class RoomListHandler(ResponseInterface):
    def __init__(self):
        self.rooms = self.get_rooms()

    def get_rooms(self):
        # get all WaitingRoom records from db using PonyORM
        return select(r for r in WaitingRoom).sort_by(WaitingRoom.id)

    def create_room_schema(self, room: WaitingRoom) -> RoomListing:
        player_num = len(room.players)

        room_schema = RoomListing(
            id=room.id,
            name=room.name,
            playerAmount=player_num,
            minPlayers=room.min_players,
            maxPlayers=room.max_players,
        )
        return room_schema

    def get_response(self) -> RoomListingList:
        room_schemas = [self.create_room_schema(room) for room in self.rooms]
        return RoomListingList(rooms=room_schemas)
